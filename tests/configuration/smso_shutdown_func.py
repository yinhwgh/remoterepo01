#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0103456.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
class Test(BaseTest):
    """
    TC0103456.001-SmsoShutdownFunc

    Check if command is implemented and if possible to execute it in both Functionality Levels: "Normal mode" and "Airplane mode".

   1. Set Normal functionality level: AT+CFUN=1
   2. Login Module to the network
   3. Send AT^SMSO=? And check response
   4. Send AT^SMSO command
   5. Using McTest check if module is turned off (MC:PWRIND)
   6. Turn On module using McTest (MC:IGT=1000)
   7. Check Functionality Level: AT+CFUN?
   Repeat steps 2-7 10 times
   8. Set Airplane Mode: AT+CFUN=4. Repeat Steps 3-7 10 times

    """
    numOfLoops = 10
    def setup(test):
        dstl_detect(test.dut)
        test.sleep(2)

    def run(test):
        test.log.info("*** Set Normal functionality level: AT+CFUN=1 ***")
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.step('Loop: {} - Begin'.format(loop))
            test.log.step("2. Login Module to the network")
            test.expect(dstl_register_to_network(test.dut))
            test.log.step("3. Send AT^SMSO=? And check response")
            test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK"))
            test.log.step("4. Send AT^SMSO command")
            test.expect(dstl_shutdown_smso(test.dut))
            test.log.step("5. Using McTest check if module is turned off ")
            #test.expect(test.dut.devboard.wait_for('.* PWRIND: 1'))
            test.sleep(5)
            test.log.step("6. Turn On module")
            test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(1)
            test.log.step("7. Check Functionality Level: AT+CFUN?")
            test.expect(test.dut.at1.send_and_verify('AT+CFUN?',".*1"))
            test.log.step("8.  Repeat step 2 to 7, 10 times")
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
            test.log.step('Loop: {} - END'.format(loop))
            loop = loop + 1

        test.log.step("11. Reset AT Command Settings to Factory Default Values")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

        test.log.info("***  Set Airplane Mode: AT+CFUN=4 ***")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","0"', "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=4", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('Loop: {} of CFUN4 - Begin '.format(loop))
            test.log.step("3. Send AT^SMSO=? And check response")
            test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK.*"))
            test.log.step("4. Send AT^SMSO command")
            test.expect(dstl_shutdown_smso(test.dut))
            test.log.step("5. Using McTest check if module is turned off")
            #test.expect(test.dut.devboard.send_and_verify('MC:PWRIND?', '.* PWRIND: 1'))
            test.sleep(5)
            test.log.step("6. Turn On module")
            test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(1)
            test.log.step("7. Check Functionality Level: AT+CFUN?")
            test.expect(test.dut.at1.send_and_verify('AT+CFUN?', ".*4"))
            test.log.step("8.  Repeat step 3 - 7, 10 times")
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
            test.log.info('Loop: {} of CFUN4 - END '.format(loop))
            loop = loop + 1

        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CFUN","1"', "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
