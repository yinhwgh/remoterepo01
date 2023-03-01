#responsible: maksym.les@globallogic.com
#location: Wroclaw
#TC0102203.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE?", "+CMEE: 2"))

        test.log.step("Precondition: Domain passwords set (as part of the TC0102194.002 or TC0102204.001)")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory/PW\", \"1234567890123456789012\"",
                                                 ".*OK.*|.*ERROR.*"), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug/PW\","
                    " \"12345678\"", ".*OK.*|.*ERROR.*"), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS/PW\", \"12345678\"",
                                                 ".*OK.*|.*ERROR.*"), critical=True)

    def run(test):
        test.log.step("1.Unlock all the functionality domains (in case they are not)")
        test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\"")
        if "unlock" in test.dut.at1.last_response:
            test.expect(True)
        elif "lock" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\","
                                                     " \"unlock\", \"1234567890123456789012\"", ".*OK.*"),
                        critical=True)
        else:
            test.expect(False, critical=True,
                        msg="\"AT^SSECUG=\"Factory/Factory\", \"unlock\", \"1234567890123456789012\"\" failed")
        test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"")
        if "unlock" in test.dut.at1.last_response:
            test.expect(True)

        elif "lock" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\","
                                                     " \"unlock\", \"12345678\"", ".*OK.*"),
                        critical=True)
        else:
            test.expect(False, critical=True,
                        msg="\"AT^SSECUG=\"Factory/Debug\", \"unlock\", \"12345678\"\" failed")
        test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"")
        if "unlock" in test.dut.at1.last_response:
            test.expect(True)

        elif "lock" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\","
                                                     " \"unlock\", \"12345678\"", ".*OK.*"),
                        critical=True)
        else:
            test.expect(False, critical=True,
                        msg="\"AT^SSECUG=\"Factory/PreconfiguredTLS\", \"unlock\", \"12345678\"\" failed")

        test.log.step("2. Try all the protected commands from each domain (do not check commands +SQNOMAGET and +SQNOMADMACC? )=> All shall work")
        check_debug_unlock_commands(test)
        check_preconfigured_unlock_commands(test)
        test.log.info("Try \"Factory\" protected commands")
        # ------------------------------------ #
        # +++  !!!AT+SMSWBOOT Commands!!!  +++ #
        # Note: The details for this command will be provided in a future revision of the document.[2020-02-12]
        test.log.info("Try \"AT+SMSWBOOT\" command")
        test.expect(False)

        factory_protected_commands = ["SMBB", "SMBC", "SMA", "SMCB", "SMGD", "SMGI",
                                      "SMGT", "SMMT", "SMNA", "SMRI", "SMSV", "SMXT"]
        for command in factory_protected_commands:
            test.log.info("Try \"AT+{}=?\" command".format(command))
            test.expect(test.dut.at1.send_and_verify("AT+{}=?".format(command), ".*OK.*"))

            test.log.info("Try \"AT+{}?\" command".format(command))
            test.expect(test.dut.at1.send_and_verify("AT+{}?".format(command), ".*OK.*"))

            test.log.info("Try \"AT+{}\" command".format(command))
            test.expect(test.dut.at1.send_and_verify("AT+{}".format(command), ".*OK.*"))
        # ----------------------------------- #
        # +++  !!!AT+SQNHWID Commands!!!  +++ #
        # Note: This command doesn't appear in the documentation.[2020-02-12]
        test.log.info("Try \"AT+SQNHWID\" command")
        test.expect(False)

        test.expect(test.dut.at1.send_and_verify("AT+SMDC=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SMDC", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect("<sequans3330 major=\"1\">" in test.dut.at1.last_response)
        regex_smaa = r'[+SMAA: ]\w\w\w\w\w'
        test.expect(test.dut.at1.send_and_verify("AT+SMAA", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect(re.findall(regex_smaa, test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+SMBI=?", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect("+SMBI: [\"AA:BB:CC:DD:EE:FF\"],[\"AA-BBBBBB-CCCCCC-D\"]" in test.dut.at1.last_response)
        regex_smbi1 = r'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w+'
        regex_smbi2 = r'\d\d-\d\d\d\d\d\d-\d\d\d\d\d\d-\d+'
        test.expect(test.dut.at1.send_and_verify("AT+SMBI?", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect(re.findall(regex_smbi1, test.dut.at1.last_response))
            test.expect(re.findall(regex_smbi2, test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+SMBI", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SME=?", ".*OK.*"))
        regex_sme = r'[+]SME: \w\w\w\w+'
        test.expect(test.dut.at1.send_and_verify("AT+SME?", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect(re.findall(regex_sme, test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+SME=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SFVER=?", ".*OK.*"))
        regex_sfver = r'[+]SFVER: \w\w\w\w,\w\w\w\w,\w\w\w\w,\w\w\w\w,\w\w\w\w\w\w\w,\w\w\w\w\w\w\w\w\w'
        test.expect(test.dut.at1.send_and_verify("AT+SFVER", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect(re.findall(regex_sfver, test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+SMST=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SMST", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect("+SMST: " in test.dut.at1.last_response)
        # ----------------------------------- #
        # +++  !!!AT+SQNHWID Commands!!!  +++ #
        # Note: This command doesn't appear in the documentation.[2020-02-12]
        test.log.info("Try \"AT+SQNHWID\" command")
        test.expect(False)

        test.expect(test.dut.at1.send_and_verify("AT+SVER=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+SVER", ".*OK.*"))
        if "OK" in test.dut.at1.last_response:
            test.expect("+SVER: " in test.dut.at1.last_response)
        # ------------------------------------ #
        # +++  !!!AT+SMSWBOOT Commands!!!  +++ #
        # Note: The details for this command will be provided in a future revision of the document.[2020-02-12]
        test.log.info("Try \"AT+SMSWBOOT\" command")
        test.expect(False)

        test.log.step("3. Lock Factory domain AT^SSECUG=\"Factory/Factory\",\"lock\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\""
                                                 , "^SSECUG: \"Factory/Factory\",\"lock\""))
        if "^SSECUG: \"Factory/Factory\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Factory\", \"lock\"", ".*OK.*"), critical=True)
        elif "ERROR" in test.dut.at1.last_response:
            test.expect(False, critical=True, msg="\"AT^SSECUG=\"Factory/Factory\", \"lock\"\" failed")

        test.log.step("4. Try all the protected commands from each domain "
                      "(do not check commands +SQNOMAGET and +SQNOMADMACC? )"
                      "=> All shall work except commands from factory domain")
        check_debug_unlock_commands(test)
        check_preconfigured_unlock_commands(test)
        check_factory_lock_commands(test)

        test.log.step("5. Lock \"Debug\" domain AT^SSECUG=\"Factory/Debug\",\"lock\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "^SSECUG: \"Factory/Debug\",\"lock\""))
        if "^SSECUG: \"Factory/Debug\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\", \"lock\"", ".*OK.*"), critical=True)
        elif "ERROR" in test.dut.at1.last_response:
            test.expect(False, critical=True, msg="\"AT^SSECUG=\"Factory/Debug\", \"lock\"\" failed")

        test.log.step(
            "6. Try all the protected commands from each domain "
            "=> All shall work except commands from factory and Debug domains")
        check_debug_lock_commands(test)
        check_preconfigured_unlock_commands(test)
        check_factory_lock_commands(test)

        test.log.step("\n\r7. Lock \"PreconfiguredTLS\" domain AT^SSECUG=\"Factory/PreconfiguredTLS\",\"lock\"")
        test.log.info("   AT^SSECUG=\"Factory/PreconfiguredTLS\",\"lock\"")
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\"",
                    "^SSECUG: \"Factory/PreconfiguredTls\",\"lock\""))
        if "^SSECUG: \"Factory/PreconfiguredTls\",\"unlock\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/PreconfiguredTLS\", \"lock\"", ".*OK.*"), critical=True)
        elif "ERROR" in test.dut.at1.last_response:
            test.expect(False, critical=True, msg="\"AT^SSECUG=\"Factory/PreconfiguredTls\", \"lock\"\" failed")

        test.log.step("8. Try all the protected commands from each domain => None shall work")
        check_debug_lock_commands(test)
        check_preconfigured_lock_commands(test)
        check_factory_lock_commands(test)

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=10)


def check_debug_unlock_commands(test):
    test.log.info("\n\rTry \"Debug\" protected commands")
    test.expect(test.dut.at1.send_and_verify("AT+BIND=?", ".*OK.*"))
    if "OK" in test.dut.at1.last_response:
        test.expect("+BIND: (\"CONSOLE\",\"AT\",\"DCP\",\"PPP\",\"NONE\",\"BR\")"
                    "[,(\"UART0\",\"UART1\",\"UART2\")[,\"store\"]]"
                    in test.dut.at1.last_response)
    test.expect(test.dut.at1.send_and_verify("AT+BIND?", ".*OK.*"))
    if "OK" in test.dut.at1.last_response:
        test.expect("+BIND: " in test.dut.at1.last_response)
    test.expect(test.dut.at1.send_and_verify("AT+BIND", ".*OK.*"))
    if "OK" in test.dut.at1.last_response:
        if "+BIND: UART0, \"AT\"" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT+BIND=\"AT\",\"UART0\"", ".*OK.*"))
        elif "+BIND: UART1, \"AT\"" in test.dut.at1.last_response and ".*OK.*" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT+BIND=\"AT\",\"UART1\"", ".*OK.*"))
        elif "+BIND: UART2, \"CONSOLE\"" in test.dut.at1.last_response and "OK" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT+BIND=\"CONSOLE\",\"UART2\"", ".*OK.*"))
    # --------------------------------- #
    # +++  !!!AT+SMLOG Commands!!!  +++ #
    # Note: The details for this command will be provided in a future revision of the document.[2020-02-12]
    test.log.info("Try \"AT+SMLOG\" command")
    test.expect(False)


def check_preconfigured_unlock_commands(test):
    test.log.info("\n\rTry \"Preconfigured\" protected commands")
    # -------------------------------- #
    # +++  !!!AT+SBNW Commands!!!  +++ #
    # Note: This command is not in the spec.[2020-02-12]
    test.log.info("Try \"AT+SBNW\" command")
    test.expect(False)


def check_factory_lock_commands(test):
    test.log.info("\n\rTry \"Factory\" protected commands with \"lock\" mode")
    factory_protected_commands = ["SMBB", "SMDC", "SMBC", "SMA", "SMAA", "SMBI", "SMCB", "SME", "SFVER", "SMGD", "SMGI",
                                    "SMGT", "SMMT", "SMNA", "SMRI", "SMST", "SMSV", "SMXT", "SVER"]
    for command in factory_protected_commands:
        test.log.info("Try \"AT+{}=?\" command".format(command))
        test.expect(test.dut.at1.send_and_verify("AT+{}=?".format(command), ".*OK.*"))

        test.log.info("Try \"AT+{}?\" command".format(command))
        test.expect(test.dut.at1.send_and_verify("AT+{}?".format(command), ".*OK.*"))

        test.log.info("Try \"AT+{}\" command".format(command))
        test.expect(test.dut.at1.send_and_verify("AT+{}".format(command), ".*OK.*"))
    # ----------------------------------- #
    # +++  !!!AT+SQNHWID Commands!!!  +++ #
    # Note: This command doesn't appear in the documentation.[2020-02-12]
    test.log.info("Try \"AT+SQNHWID\" command")
    test.expect(False)


def check_debug_lock_commands(test):
    test.log.info("\n\rTry \"Debug\" protected commands with \"lock\" mode")
    test.expect(test.dut.at1.send_and_verify("AT+BIND=?", ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify("AT+BIND?", ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify("AT+BIND", ".*OK.*"))
    # --------------------------------- #
    # +++  !!!AT+SMLOG Commands!!!  +++ #
    # Note: The details for this command will be provided in a future revision of the document.[2020-02-12]
    test.log.info("Try \"AT+SMLOG\" command")
    test.expect(False)


def check_preconfigured_lock_commands(test):
    test.log.info("\n\rTry \"Preconfigured\" protected commands with \"lock\" mode")
    # -------------------------------- #
    # +++  !!!AT+SBNW Commands!!!  +++ #
    # Note: This command is not in the spec.[2020-02-12]
    test.log.info("Try \"AT+SBNW\" command")
    test.expect(False)


if "__main__" == __name__:
    unicorn.main()
