#responsible maciej.gorny@globallogic.com
#location Wroclaw
#corresponding Test Case TC 0096580.003
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import *
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
        Short description:
        To check if supported TLS version is configurable via the AT command (at^scfg).
        Test if above settings are non-volatile.

        Detailed description:
        1. Set "MAX" value for "TLS_min_version" and "TLS_max_version" parameters using AT^SCFG= "Tcp/TLS/Version"
            write command.
        2. Using AT^SCFG read command display list of setting and check set values from previous step.
        3. Try to set all possible values for TLS_min_version parameter using AT^SCFG= "Tcp/TLS/Version" write command:
            - "MIN" automatic minimum
            - "1.2" (D)TLSv1.2
            - "MAX" automatic maximum
            - "1.1" TLSv1.1 - set it as a last value
        4. Using AT^SCFG read command display list of setting and check if all values from previous step were set
            for "Tcp/TLS/Version" (one by one).
        5. Try to set all possible values for "TLS_max_version" parameter using AT^SCFG= "Tcp/TLS/Version"
            write command:
            - "1.2" TLSv1.2
            - "MAX" (D) automatic maximum
        6. Using AT^SCFG read command display list of setting and check if all values from previous step were
            set for "Tcp/TLS/Version" (one by one)
        7. Try to set some illegal values for both parameters
        8. Repeat step 6
        9. Restart module
        10. Repeat step 6
       """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        tls_min_version = ["MIN", "1.2", "MAX", "1.1"]
        tls_max_version = ["1.2", "MAX"]
        tls_incorrect_values = {"1.4", "MON", "0,9", "X", "10", "1."}
        test.expect(dstl_enter_pin(test.dut))

        test.log.h2("Executing script for test case: TC0096580.003 ConfigurabilityOfSupportedTLSversions ")

        test.log.step("1) set MAX value for TLS_min_version and TLS_max_version parameters "
                      "using AT^SCFG= Tcp/TLS/Version write command.")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MAX", "MAX"))

        test.log.step("2) Using AT^SCFG read command display list of setting and check set values from previous step.")
        test.expect(('MAX', 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step("3 Try to set all possible values for TLS_min_version parameter "
                      "using AT^SCFG= \"Tcp/TLS/Version\" write command:\n"
                      "- \"MIN\" automatic minimum\n"
                      "-\"1.2\" (D)TLSv1.2\n"
                      "-\"MAX\" automatic maximum\n"
                      "-\"1.1\" TLSv1.1 - set it as a last value")

        for parameter_min_value in tls_min_version:
            test.log.info("Setting TLS_min_version to: " + parameter_min_value)
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, parameter_min_value, "MAX"))
            test.log.info("Checking if set value is correct, expected: " + parameter_min_value)
            test.expect((parameter_min_value, "MAX") == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step("4) Using AT^SCFG read command display list of setting and check if all values from "
                      "previous step were set for \"Tcp/TLS/Version\" (one by one).")
        test.log.info("4) Step checked in previous step")

        test.log.step("5) Try to set all possible values for \"TLS_max_version\" parameter "
                      "using AT^SCFG= \"Tcp/TLS/Version\" write command:")
        for parameter_max_value in tls_max_version:
            test.log.info("Setting TLS_max_version to: " + parameter_max_value)
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.1", parameter_max_value))
            test.log.info("Checking if set value is correct, expected: " + parameter_max_value)
            test.expect(("1.1", parameter_max_value) == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step("6) Using AT^SCFG read command display list of setting and check if all values from "
                      "previous step were set for \"Tcp/TLS/Version\" (one by one).")
        test.log.info("6) Step checked in previous step")

        test.log.step("7) Try to set some illegal values for both parameters")
        for parameter_incorrect_value in tls_incorrect_values:
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, parameter_incorrect_value, "MAX", expected=".*ERROR.*"))
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", parameter_incorrect_value, expected=".*ERROR.*"))
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, parameter_incorrect_value, parameter_incorrect_value,
                                                      expected=".*ERROR.*"))

        test.log.step("8) Repeat step 6")
        test.log.info("Checking if set value is correct.")
        test.expect(("1.1", 'MAX') == dstl_get_scfg_tcp_tls_version(test.dut))

        test.log.step("9) Restart module")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("10) Repeat step 6")
        test.log.info("Checking if set value is correct.")
        test.expect(("1.1", "MAX") == dstl_get_scfg_tcp_tls_version(test.dut))

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

if "__main__" == __name__:
    unicorn.main()
