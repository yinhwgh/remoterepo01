#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0091661.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.security.lock_unlock_sim import dstl_lock_sim


class Test(BaseTest):
    """TC0091661.001    CemodeBasic

    Check the function of the UE mode of operation for EPS

    1. Restart module to eject PIN number (if required)
    2. Check command without PIN (test, read and write form)
    3. Register to the network
    4. Check command with PIN (test, read and write form)
    5. Check write command with invalid parameters
    6. Enter Airplane Mode
    7. Check the command (test and read form)
    8. Back to normal functionality
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)

    def run(test):
        project = test.dut.project.upper()
        test.log.step("1. Restart module to eject PIN number (if required)")
        test.expect(dstl_restart(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*"))
        if "READY" in test.dut.at1.last_response:
            dstl_lock_sim(test.dut)
            test.expect(dstl_restart(test.dut))
            test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

        test.log.step("2. Check command without PIN (test, read and write form)")
        if project == "COUGAR":
            check_cemode(test, "test", r"\+CEMODE: \(0,2\).*OK")
            check_cemode(test, "read", r"\+CEMODE: 2.*OK")
            check_cemode(test, "write", "OK")
        else:
            check_cemode(test, "test", r"\+CME ERROR: SIM PIN required")
            check_cemode(test, "read", r"\+CME ERROR: SIM PIN required")
            if project == "VIPER":
                check_cemode(test, "write", r"\+CME ERROR: unknown")
            else:
                check_cemode(test, "write", r"\+CME ERROR: SIM PIN required")

        test.log.step("3. Register to the network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("4. Check command with PIN (test, read and write form)")
        if project == "SERVAL":
            check_cemode(test, "test", r"\+CEMODE: \(0,2\).*OK")
            check_cemode(test, "read", r"\+CEMODE: (0|2).*OK")
        elif project == "COUGAR":
            check_cemode(test, "test", r"\+CEMODE: \(0,2\).*OK")
            check_cemode(test, "read", r"\+CEMODE: 0.*OK")
        elif project in ("BOBCAT", "VIPER"):
            check_cemode(test, "test", r"\+CEMODE: (\(0,1,2,3\)|\(0-3\)).*OK")
            check_cemode(test, "read", r"\+CEMODE: 1.*OK")
            check_cemode(test, "write", "ERROR", "3")
        if project not in ("BOBCAT", "VIPER"):
            check_cemode(test, "write", "OK")
            check_cemode(test, "read", r"\+CEMODE: 0.*OK")
            check_cemode(test, "write", "OK", "2")
            check_cemode(test, "read", r"\+CEMODE: 2.*OK")

        test.log.step("5. Check write command with invalid parameters")
        if project == "SERVAL" or project == "COUGAR":
            check_cemode(test, "write", r"\+CME ERROR:", "1")
            check_cemode(test, "write", r"\+CME ERROR:", "3")
        check_cemode(test, "write", r"\+CME ERROR:", "4")
        check_cemode(test, "write", r"\+CME ERROR:", "-1")
        check_cemode(test, "write", r"\+CME ERROR:", "")
        check_cemode(test, "write", r"\+CME ERROR:", "020")
        check_cemode(test, "write", r"\+CME ERROR:", "2a")
        check_cemode(test, "write", r"\+CME ERROR:", "max")
        check_cemode(test, "write", r"\+CME ERROR:", "min")

        test.log.step("6. Enter Airplane Mode")
        test.expect(dstl_set_airplane_mode(test.dut))

        test.log.step("7. Check the command (test and read form)")
        if project == "COUGAR":
            check_cemode(test, "test", r"\+CEMODE: \(0,2\).*OK")
            check_cemode(test, "read", r"\+CEMODE: 2.*OK")
        else:
            check_cemode(test, "test", r"\+CME ERROR: operation not supported")
            check_cemode(test, "read", r"\+CME ERROR: operation not supported.")

        test.log.step("8. Back to normal functionality")
        test.expect(dstl_set_full_functionality_mode(test.dut))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


def check_cemode(test, type, expected_response, value='0'):
    if type is "test":
        test.expect(test.dut.at1.send_and_verify("AT+CEMODE=?", ".*{}.*".format(expected_response)))
    elif type is "read":
        test.expect(test.dut.at1.send_and_verify("AT+CEMODE?", ".*{}.*".format(expected_response)))
    elif type is "write":
        test.expect(test.dut.at1.send_and_verify("AT+CEMODE={}".format(value), ".*{}.*".format(expected_response)))


if "__main__" == __name__:
    unicorn.main()
