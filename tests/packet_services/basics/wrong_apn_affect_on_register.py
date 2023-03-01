# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107907.001
# intention: try to attach/register with wrong apn - network should deny. Try with selective and auto RAT setting
# note: possible with Berlin Ericsson Testnetwork, other networks unknown

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.call.switch_to_command_mode import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.network_service.customization_network_types import dstl_customized_network_types
from dstl.network_service.network_access_type import *
from dstl.security.lock_unlock_sim import *

dstl_set_network_max_modes, dstl_set_network_single_mode


class Test(BaseTest):
    """
        TC0107907.001 - wrong_apn_affect_on_register

        first implementation: Viper_100_120c
    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        # test.dut.dstl_set_sim_waiting_for_pin1()

        test.apn1 = test.dut.sim.gprs_apn
        test.apn2 = test.dut.sim.gprs_apn_2
        if test.apn1 is '':
            if test.apn2 is '':
                test.expect(False, critical=True, msg="at least one APN for this SIM has to be given - ABORT!")
            else:
                test.apn = test.apn2
        else:
            test.apn = test.apn1
        test.log.info(f' APN of SIM parameter used in this test is: {test.apn}')
        pass

    def run(test):
        rat_dict = test.dut.dstl_customized_network_types()
        test.log.info(f' these RATs are used for this product: {rat_dict}')

        if 'LTE' in rat_dict:

            # wrong APN will fail - CREG: 3  / registration denied   appears only after entering PIN!
            test.dut.dstl_restart()
            if test.dut.project is 'VIPER':
                test.expect(test.dut.at1.wait_for_strict('\+CIEV: prov,', timeout=9))
            test.dut.at1.send_and_verify('AT+cgdcont=1,"IP","wrong-lte-apn"')
            test.dut.dstl_set_network_single_mode('LTE')
            test.dut.at1.send_and_verify('AT+creg=2')
            test.dut.dstl_enter_pin(wait_till_ready=False)
            test.expect(test.dut.at1.wait_for_strict('\+CREG: 2', timeout=50))      # 3: Registration denied
            test.sleep(5)
            for i in range(1, 3):
                test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', 'ERROR: no network service', timeout=65))
                # sometimes CREG:3 appears, sometimes not, we will check it 3 times.
                ret = test.dut.at1.wait_for_strict('\+CREG: 3', timeout=15)  # 3: Registration denied
                if ret:
                    break
                    test.expcect(True, msg="+CREG: 3 (Registration denied) was found one time")
                test.sleep(4)

            # correct APN: now registration is possible:
            test.dut.at1.send_and_verify(f'AT+cgdcont=1,"IP",{test.apn}')
            test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', 'SYSSTART AIRPLANE MODE'))  # alternativ to +COPS=2
            test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', 'SYSSTART'))
            # test.dut.at1.send_and_verify('AT+COPS=2')
            # test.expect(test.dut.at1.send_and_verify('AT+COPS=,,,7', timeout=65))
            test.expect(test.dut.at1.wait_for_strict('\+CREG: 1', timeout=50))  # 1: registered to home network

        if 'GSM' in rat_dict:
            # wrong APN will fail for manual context activation, registration is possible (no pdp context necessary)
            test.dut.dstl_restart()
            if test.dut.project is 'VIPER':
                test.expect(test.dut.at1.wait_for_strict('\+CIEV: prov,', timeout=9))
            test.dut.at1.send_and_verify('AT+cgdcont=1,"IP","wrong-gsm-apn"')
            test.dut.dstl_set_network_single_mode('GSM')
            test.dut.at1.send_and_verify('AT+creg=2')
            test.dut.dstl_enter_pin(wait_till_ready=False)
            test.expect(test.dut.at1.wait_for_strict('\+CREG: 1', timeout=50))
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', 'ERROR: requested service option not subscribed',
                                                     timeout=15))
            test.sleep(9)

            # correct APN: now registration is possible:
            test.sleep(5)
            test.dut.at1.send_and_verify(f'AT+cgdcont=1,"IP",{test.apn}')
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', "OK", timeout=65))

        if 'UMTS' in rat_dict:
            # wrong APN will fail for manual context activation, registration is possible (no pdp context necessary)
            test.dut.dstl_restart()
            if test.dut.project is 'VIPER':
                test.expect(test.dut.at1.wait_for_strict('\+CIEV: prov,', timeout=9))
            test.dut.at1.send_and_verify('AT+cgdcont=1,"IP","wrong-umts-apn"')
            test.dut.dstl_set_network_single_mode('UMTS')
            test.dut.at1.send_and_verify('AT+creg=2')
            test.dut.dstl_enter_pin(wait_till_ready=False)
            test.expect(test.dut.at1.wait_for_strict('\+CREG: 1', timeout=50))
            test.expect(
                test.dut.at1.send_and_verify('AT+CGACT=1,1', 'ERROR: requested service option not subscribed',
                                             timeout=15))
            test.sleep(9)

            # correct APN: now registration is possible:
            test.sleep(5)
            test.dut.at1.send_and_verify(f'AT+cgdcont=1,"IP",{test.apn}')
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', "OK", timeout=65))

            '''
        
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2', timeout=45))
            
            ret = test.dut.dstl_register_to_lte()
            if not ret:
                lr = test.dut.at1.last_response
            print(lr)

            test.dut.at1.send_and_verify('AT+creg?', '\+CREG: [3].*OK')
            test.dut.at1.send_and_verify('AT+creg=2')
            '''

        test.dut.at1.send_and_verify('AT^SMONI')
        test.dut.at1.send_and_verify('AT+COPS=0', timeout=45)
        pass

    def cleanup(test):
        test.dut.at1.send_and_verify('AT+COPS=2', timeout=45)
        test.dut.at1.send_and_verify(f'AT+cgdcont=1,"IP",{test.apn}')
        test.dut.dstl_set_network_max_modes()
        test.dut.at1.send_and_verify('AT+creg=2', '.*OK*')
        test.dut.at1.send_and_verify('AT+COPS=0', timeout=45)
        test.sleep(9)
        test.dut.at1.send_and_verify('AT&F', '.*OK*')
        pass


if __name__ == "__main__":
    unicorn.main()
