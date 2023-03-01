#responsible: damian.latacz@globallogic.com
#location: Wroclaw
# TC0104669.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_irt import dstl_set_scfg_tcp_irt, dstl_get_scfg_tcp_irt
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       TC intention: To check if it is possible to set the "Tcp/IRT" parameter in SCFG.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.step("1. Change \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", expect="OK"))

        test.log.step("2. Set \"Tcp/IRT\" parameter in SCFG to \"1\".")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "1"))

        test.log.step("3. Check if \"Tcp/IRT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == "1")

        test.log.step("4. Set \"Tcp/IRT\" parameter in SCFG to \"60\".")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "60"))

        test.log.step("5. Check if \"Tcp/IRT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == "60")

        test.log.step("6. Try to set some illegal values.")
        illegal_values = ["-1", "61", "a", "abc", "@"]
        for value in illegal_values:
            test.expect(dstl_set_scfg_tcp_irt(test.dut, value, expected=".*CME ERROR:.*"))

        test.log.step("6. Check if \"Tcp/IRT\" parameter is changed.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == "60")

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "3"))


if "__main__" == __name__:
    unicorn.main()
