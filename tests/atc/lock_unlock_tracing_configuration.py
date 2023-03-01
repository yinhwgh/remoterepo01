#responsible: maksym.les@globallogic.com
#location: Wroclaw
#TC0102194.002

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
        if test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\", \"lock\"", ".*ERROR.*")):
            test.log.step("1.Try to lock each domain. => Expected ERROR since passwords are not set")
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\", \"lock\"", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\",\"lock\"", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\", \"lock\"", ".*ERROR.*"))

            test.log.step("2. Check the state of each domain lock => should be \"Unlock\"")
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"",
                                                     "^SSECUG: \"Factory/Factory\",\"unlock\""))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"",
                                                     "^SSECUG: \"Factory/Factory\",\"unlock\""))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"",
                                                     "^SSECUG: \"Factory/PreconfiguredTls\",\"unlock\""))

            test.log.step("3. Set domain passwords: => OK expected")
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\", \"1234567890123456789012\"",
                                                     ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug/PW\", \"12345678\"",
                                                     ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS/PW\", \"12345678\"",
                                                     ".*OK.*"))

        test.log.step("4. Lock each domain: => OK expected")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\""
                                                 , "^SSECUG: \"Factory/Factory\",\"lock\""))
        if "^SSECUG: \"Factory/Factory\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\", \"lock\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "^SSECUG: \"Factory/Debug\",\"lock\""))
        if "^SSECUG: \"Factory/Debug\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\", \"lock\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"",
                                                 "^SSECUG: \"Factory/PreconfiguredTls\",\"lock\""))
        if "^SSECUG: \"Factory/PreconfiguredTls\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\", \"lock\"", ".*OK.*"))

        test.log.step("5.  Check the state of each domain lock => should be \"lock\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"",
                                                 "^SSECUG: \"Factory/Factory\",\"lock\""), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"",
                                                 "^SSECUG: \"Factory/Debug\",\"lock\""), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"",
                                                 "^SSECUG: \"Factory/PreconfiguredTls\",\"lock\""), critical=True)

        test.log.step("6. Try to use command from each domain => Shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT+BIND=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SMBI=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SBNW=\"preconfig_cert\",1", ".*ERROR.*"))

        test.log.step("7. Try to unlock Factory domain without Password => Shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\", \"unlock\"",
                                                 ".*ERROR.*"))

        test.log.step("8. Try to unlock Factory domain with wrong Password (\"12345678\") => Shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\",\"unlock\",\"12345678\"",
                                                 ".*ERROR.*"))

        test.log.step("9. Try to immediately unlock Factory domain with correct Password"
                      " => Shall return ERROR (back-off timer)")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\",\"unlock\",\"1234567890123456789012\"",
                                                 ".*ERROR.*"))

        test.log.step("10. Wait 5s and unlock the factory domain with correct password => OK")
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\",\"unlock\",\"1234567890123456789012\"",
                                                 ".*OK.*"), critical=True)

        test.log.step("11. Unlock all other domains with the correct passwords => OK")
        test.expect(test.dut.at1.send_and_verify("AAT^SSECUG=\"Factory/Debug\",\"unlock\",\"12345678\"",
                                                 ".*OK.*"), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\",\"unlock\",\"12345678\"",
                                                 ".*OK.*"), critical=True)

        test.log.step("12. Check the state of each domain lock => should be \"Unlock\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"",
                                                 "^SSECUG: \"Factory/Factory\",\"unlock\""), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"",
                                                 "^SSECUG: \"Factory/Factory\",\"unlock\""), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"",
                                                 "^SSECUG: \"Factory/PreconfiguredTls\",\"unlock\""), critical=True)

        test.log.step("13. Try to use command from each domain => Shall return OK")
        test.expect(test.dut.at1.send_and_verify("AT+BIND=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SMBI=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SBNW=\"preconfig_cert\",1", ".*OK.*"))

        test.log.step("14. Try Read, Test, Exec command versions => Shall return ERROR")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG", ".*ERROR.*"))

        test.log.step("15. Perform AT+CFUN=0, AT+CFUN=1 cycle to force PIN not verified")
        test.expect(dstl_set_minimum_functionality_mode(test.dut))
        test.expect(dstl_set_full_functionality_mode(test.dut))

        test.log.step("16. Try to check domain state to see if command is not PIN protected => OK")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?  ", ".*SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"",
                                                 "^SSECUG: \"Factory/Factory\",\"unlock\""))

        test.log.step("17. Switch to airplane mode AT+CFUN=4")
        test.expect(dstl_set_airplane_mode(test.dut))

        test.log.step("18. Try to check domain state to see if command is working"
                      " in airplane mode => OK AT^SSECUG=\"Factory/Factory\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"", ".*OK.*"), critical=True)

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=10)


if "__main__" == __name__:
    unicorn.main()
