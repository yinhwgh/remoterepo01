# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107957.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version


class Test(BaseTest):
    """
    Intention:
    To check if it is possible to set the "Tcp/TLS/Version" parameter in SCFG.

    Detailed description:
    1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
    2. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version MIN
    - TLS_max_version 1.2.
    3. Check if "Tcp/TLS/Version" parameter is changed correctly.
    4. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version 1.1
    - TLS_max_version 1.3
    5. Check if "Tcp/TLS/Version" parameter is changed correctly.
    6. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version 1.2
    - TLS_max_version MAX
    7. Check if "Tcp/TLS/Version" parameter is changed correctly.
    8. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version 1.3
    - TLS_max_version 1.3
    9. Check if "Tcp/TLS/Version" parameter is changed correctly.
    10. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version MAX
    - TLS_max_version MAX
    11. Check if "Tcp/TLS/Version" parameter is changed correctly.
    12. Set "Tcp/TLS/Version" parameters in SCFG to:
    - TLS_min_version MAX
    - TLS_max_version MIN
    13. Check if "Tcp/TLS/Version" parameter is changed correctly.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.value_MIN = "MIN"
        test.value_MAX = "MAX"
        test.value_1_1 = "1.1"
        test.value_1_2 = "1.2"
        test.value_1_3 = "1.3"

    def run(test):
        test.log.info("TC0107957.001 TcpTlsVersion_BasicCheck")

        test.log.step("1. Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version MIN\r\n- TLS_max_version 1.2")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_MIN, test.value_1_2))

        test.log.step("3. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("4. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version 1.1\r\n- TLS_max_version 1.3")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_1_1, test.value_1_3))

        test.log.step("5. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("6. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version 1.2\r\n- TLS_max_version MAX")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_1_2, test.value_MAX))

        test.log.step("7. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("8. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version 1.3\r\n- TLS_max_version 1.3")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_1_3, test.value_1_3))

        test.log.step("9. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("10. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version MAX\r\n- TLS_max_version MAX")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_MAX, test.value_MAX))

        test.log.step("11. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("12. Set \"Tcp/TLS/Version\" parameters in SCFG to:\r\n"
                      "- TLS_min_version MAX\r\n- TLS_max_version MIN")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_MAX, test.value_MIN,
                                                  expected=test.error))

        test.log.step("13. Check if \"Tcp/TLS/Version\" parameter is changed correctly.")
        test.log.info("Done in previous step")

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, test.value_1_2, test.value_MAX))


if "__main__" == __name__:
    unicorn.main()