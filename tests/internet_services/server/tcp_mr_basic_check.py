#responsible marek.kocela@globallogic.com
#Wroclaw
#TC TC0104786.001
import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_get_scfg_tcp_mr, dstl_set_scfg_tcp_mr
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """Short description:
       To check if it is possible to set the "Tcp/MR" parameter in SCFG.

       Detailed description:
       1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
       2. Set Global "Tcp/MR" parameter in SCFG to min possible value (usually 1).
       3. Check if "Tcp/MR" parameter is changed correctly.
       4. Set Global "Tcp/MR" parameter in SCFG to max possible value (usually 30).
       5. Check if "Tcp/MR" parameter is changed correctly.
       6. Set Global "Tcp/MR" parameter in SCFG to random correct value (e.g. 12).
       7. Check if "Tcp/MR" parameter is changed correctly.
       8. Try to set some illegal values.
       9. Check if "Tcp/MR" parameter is changed.
       """

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.info("TC0104786.001 - TcpMr_BasicCheck")

        test.log.step("1) Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect="OK", wait_for="OK", timeout=10))

        test.log.step("2) Set Global \"Tcp/MR\" parameter in SCFG to min possible value (usually 1).")
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "1"))

        test.log.step("3) Check if \"Tcp/MR\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_mr(test.dut) == "1")

        test.log.step("4 Set Global \"Tcp/MR\" parameter in SCFG to max possible value (usually 30).")
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "30"))

        test.log.step("5) Check if \"Tcp/MR\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_mr(test.dut) == "30")

        test.log.step("6) Set Global \"Tcp/MR\" parameter in SCFG to random correct value (e.g. 12).")
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "12"))

        test.log.step("7) Check if \"Tcp/MR\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_mr(test.dut) == "12")

        test.log.step("8) Try to set some illegal values.")
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "-1", expected="ERROR"))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "0", expected="ERROR"))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "31", expected="ERROR"))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "test", expected="ERROR"))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, "1000", expected="ERROR"))

        test.log.step("9) Check if \"Tcp/MR\" parameter is changed.")
        test.expect(dstl_get_scfg_tcp_mr(test.dut) == "12")

    def cleanup(test):
        try:
            dstl_set_scfg_tcp_mr(test.dut, "10")
            test.dut.at1.send_and_verify('at&f', expect="OK", wait_for="OK", timeout=10)

        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
