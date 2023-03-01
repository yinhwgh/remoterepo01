#responsible: mateusz.wasielewski@globallogic.com
#location: Wroclaw
#TC

import unicorn

from core.basetest import BaseTest
from dstl.devboard.ignite_module import dstl_ignite_module
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.scfg_radio_band import dstl_set_all_radio_bands
from dstl.auxiliary.restart_module import dstl_restart

from dstl.sms.send_and_wait_for_sms import send_and_wait_for_sms

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_ignite_module()

        #Module:
        # 0.1 Run dstl_detect() to identify device
        # 0.2 Ensure that Normal Functionality level is set
        # 1. Unlock SIM PIN
        # 2. Switch to automatic network selection mode
        # 3. Enable all radio bands for all RATs
        # 4. Restart module to apply settings
        # 5. Insert SIM PIN and attach to network
        # 6. Enable URC report for incoming messages

        #Remote:
        # 0 Run dstl_detect() to identify device
        # 1 Insert SIM PIN and attach to network
        # 2 Enable URC report for incoming messages

        #Module
        # 0.1
        test.dut.dstl_detect()   

        # 0.2
        test.log.info("Set Normal Functionality Mode")
        test.dut.dstl_set_full_functionality_mode()

        # 1
        test.log.info("Insert SIM PIN")
        status = test.dut.dstl_enter_pin()
        test.expect(status, critical = True)

        # 2
        test.log.info("Switch to automatic network selecion mode")
        status = test.dut.at1.send_and_verify("at+cops=0", expect="OK")
        test.expect(status, critical = True)

        # 3
        test.log.info("Enable all radio bands for all RATs")
        status = test.dut.dstl_set_all_radio_bands()
        test.expect(status, critical = True)

        # 4
        test.log.info("Restart module to apply settings")
        status = test.dut.dstl_restart()
        test.expect(status, critical = True)

        # 5
        test.log.info("Insert SIM PIN and attach to network")
        status = dstl_register_to_network(test.dut)
        test.expect(status, critical = True)

        # 6
        test.log.info("Enable URC report for incoming messages")
        status = test.dut.at1.send_and_verify('AT+CNMI=2,1', expect="OK")
        test.expect(status, critical = True)

        # Remote
        # 0
        test.r1.dstl_detect()

        # 1
        test.log.info("Insert SIM PIN and attach to network")
        status = dstl_register_to_network(test.r1)
        test.expect(status, critical = True)

        # 2
        test.log.info("Enable URC report for incoming messages")
        status = test.r1.at1.send_and_verify('AT+CNMI=2,1', expect="OK")
        test.expect(status, critical = True)

    def run(test):

        # 1. Sleep for  10 s
        test.sleep(10)

        # 2. Measure mo_cs_call and mo_cs_call_setup_time KPIs
        status = send_and_wait_for_sms(test.dut, test.r1, direction=True)
        test.expect(status)

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
