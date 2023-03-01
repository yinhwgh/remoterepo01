# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0104787.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_ot import \
    dstl_set_scfg_tcp_ot, dstl_get_scfg_tcp_ot


class Test(BaseTest):
    """Short description:
       To check if it is possible to set the "Tcp/OT" parameter in SCFG

       Detailed description:
       1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
       2. Set Global "Tcp/OT" parameter in SCFG to min possible value (usually 1).
       3. Check if "Tcp/OT" parameter is changed correctly.
       4. Set Global "Tcp/OT" parameter in SCFG to max possible value (usually 6000).
       5. Check if "Tcp/OT" parameter is changed correctly.
       6. Set Global "Tcp/OT" parameter in SCFG to random correct value (e.g. 500).
       7. Check if "Tcp/OT" parameter is changed correctly.
       8. Try to set some illegal values.
       9. Check if "Tcp/OT" parameter is changed.
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.info("TC0104787.001 - TcpOt_BasicCheck")

        test.log.step("1) Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2) Set Global \"Tcp/OT\" parameter in SCFG to min possible value "
                      "(usually 1).")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "", use_min_value=True))

        test.log.step("3) Check if \"Tcp/OT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_ot(test.dut, use_min_value=True) == "min value as expected")

        test.log.step("4) Set Global \"Tcp/OT\" parameter in SCFG to max possible value "
                      "(usually 6000).")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "6000"))

        test.log.step("5) Check if \"Tcp/OT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_ot(test.dut) == "6000")

        test.log.step("6) Set Global \"Tcp/OT\" parameter in SCFG to random correct value "
                      "(e.g. 500).")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "500"))

        test.log.step("7) Check if \"Tcp/OT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_ot(test.dut) == "500")

        test.log.step("8) Try to set some illegal values.")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "-1", expected="CME ERROR"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "6001", expected="CME ERROR"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "6666", expected="CME ERROR"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "10000", expected="CME ERROR"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "test", expected="CME ERROR"))

        test.log.step("9) Check if \"Tcp/OT\" parameter is changed.")
        test.expect(dstl_get_scfg_tcp_ot(test.dut) == "500")

    def cleanup(test):
        try:
            dstl_set_scfg_tcp_ot(test.dut, "6000")
            test.expect(dstl_reset_settings_to_factory_default_values(test.dut))

        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()