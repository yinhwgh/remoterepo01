#responsible: shuang.liangg@thalesgroup.com
#location: Beijing
#TC0103567.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network,dstl_enter_pin
from dstl.call.switch_to_command_mode import *


class Test(BaseTest):
    """
        TC0103567.001	PsAttachDuringPppConnection
        Intention : Checking properly activation to Packet Domain service using PPP commands: ATD*99# and AT+CGDATA.
        If the MT is not PS attached when the activation form of the command is executed, the MT first performs
        a PS attach and then attempts to activate the specified contexts.
        Ref. IPIS100228359 and its next FUPs

         1. Attach module to the network
        1a) if DUT is in LTE check activated context ID (AT+CGACT?)
        1b) if DUT is in 2G/3G try to activate 1st context via AT+CGACT=1,1 and check if it can be activated correctly (AT+CGACT?)
        2. Detach module from Packet Domain via AT+CGATT=0
        3. Enter PPP mode via AT+CGDATA and wait for CONNECT
        4. Switch to command mode via +++
        5. Check AT+CGATT?
        6. return to data mode via ATO and wait for CONNECT and disconnect active PPP connection (e.g. via ATH or using DTR line) and wait for NO CARRIER
        7. Detach module from Packet Domain via AT+CGATT=0
        8. Request Packet Domain Service via ATD*99# and wait for CONNECT
        9. Switch to command mode via +++
        10. Check AT+CGATT?
        11. return to data mode via ATO and wait for CONNECT and disconnect active PPP connection (e.g. via ATH or using DTR line) and wait for NO CARRIER
    """
    def setup(test):
        dstl_restart(test.dut)
        dstl_detect(test.dut)

    def run(test):

        test.log.step("1. Attach module to the network.")
        # test.expect(test.dut.at1.send_and_verify('at+cops=2', '.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}"'.format(1, test.dut.sim.apn_v4), '.*OK.*'))
        #
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+cgact?', '.*OK.*'))
        if 'CGACT: 1,0' in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('at+cgact=1,1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+cgact?', '.*\+CGACT: 1,1.*OK.*'))

        test.log.step("2. Detach module from Packet Domain via AT+CGATT=0.")
        test.expect(test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*', timeout=60))
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*\+CGATT: 0.*', timeout=60))

        test.log.step("3. Enter PPP mode via AT+CGDATA and wait for CONNECT")
        test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",{}'.format(1), ".*CONNECT.*"))

        test.log.step("4. Switch to command mode via +++")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

        test.log.step("5. Check AT+CGATT?")
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*\+CGATT: 1.*OK.*', timeout=60))

        test.log.step("6. Return to data mode via ATO and wait for CONNECT and disconnect active PPP connection (e.g. via ATH or using DTR line) and wait for NO CARRIER")
        test.expect(test.dut.at1.send_and_verify('ATO', ".*CONNECT.*",timeout=60))
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.expect(test.dut.at1.send_and_verify('ATH', '.*OK.*'))

        test.log.step("7. Detach module from Packet Domain via AT+CGATT=0")
        test.expect(test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*', timeout=60))
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*\+CGATT: 0.*', timeout=60))

        test.log.step("8. Request Packet Domain Service via ATD*99# and wait for CONNECT")
        test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*',timeout=60))

        test.log.step("9. Switch to command mode via +++")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

        test.log.step("10. Check AT+CGATT?")
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*\+CGATT: 1.*OK.*', timeout=60))

        test.log.step(
            "11. Return to data mode via ATO and wait for CONNECT and disconnect active PPP connection (e.g. via ATH or using DTR line) and wait for NO CARRIER")
        test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', timeout=60))
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.expect(test.dut.at1.send_and_verify('ATH', '.*OK.*'))

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
