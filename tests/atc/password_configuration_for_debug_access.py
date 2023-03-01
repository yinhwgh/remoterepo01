#responsible: maksym.les@globallogic.com
#location: Wroclaw
#TC0102204.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode,\
                                                    dstl_set_minimum_functionality_mode


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.step("1. Invalid password tests")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\", \"1234567\"",
                                                 ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\","
                                                 " \"123456789012345678901234567890123\"",
                                                 ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\","
                                                 " \"123456789-\"",
                                                 ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\","
                                                 " \"123456789@\"",
                                                 ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\","
                                                 " \"123456789$\"",
                                                 ".*ERROR.*"))

        test.log.step("2. Check that \"Factory\" domain commands are available"
                      " - AT+SMBI? shall be available (return +SMBI: ... OK)")
        test.expect(test.dut.at1.send_and_verify("AT+SMBI?", ".*OK.*"))

        test.log.step("3. Set the password for \"Factory\" domain - "
                      "AT^SSECUG=\"Factory/Factory/PW\", \"12345678901234567890123456789012\" => OK expected")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\""
                                                 ", \"12345678901234567890123456789012\"", ".*OK.*"), critical=True)

        test.log.step("4. Check if the \"Factory\" domain commands were automatically locked"
                      " - AT+SMBI? shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT+SMBI?", ".*ERROR.*"))

        test.log.step("5. Try to re-set the password for \"Factory\" domain - AT^SSECUG=\"Factory/Factory/PW\","
                      " \"12345678901234567890\" => ERROR expected")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\","
                      " \"12345678901234567890\"", ".*ERROR.*"))

        test.log.step("6. Try Read, Test, Exec command versions => Shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG", ".*ERROR.*"))

        test.log.step("7. Set minimum functionality mode (CFUN0) to force PIN not verified - AT+CFUN=0")
        test.expect(dstl_set_minimum_functionality_mode(test.dut), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?  ", ".*SIM PIN.*"))

        test.log.step("8. Set back full functionality mode (CFUN1) - AT+CFUN=1")
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)

        test.log.step("9. Check functionality availability - AT^SSECUG=\"Factory/Debug/PW\", \"12345678\""
                      " => OK expected")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug/PW\", \"12345678\"", ".*OK.*"))

        test.log.step("10. Set Airplane mode functionality (CFUN4) - AT+CFUN=4")
        test.expect(dstl_set_airplane_mode(test.dut), critical=True)

        test.log.step("11. Check functionality availability - AT^SSECUG=\"Factory/PreconfiguredTLS/PW\","
                      " \"12345678\" => OK expected")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS/PW\", \"12345678\"", ".*OK.*"), critical=True)

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=10)


if "__main__" == __name__:
    unicorn.main()
