# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107955.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.internet_service.configuration.scfg_tcp_irt import dstl_get_scfg_tcp_irt, \
    dstl_set_scfg_tcp_irt


class Test(BaseTest):
    """
    Intention:
    To check if it is possible to set the "Tcp/IRT" parameter in SCFG.

    Detailed description:
    1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
    2. Set "Tcp/IRT" parameter in SCFG to min possible value (usually 1).
    3. Check if "Tcp/IRT" parameter is changed correctly.
    4. Set "Tcp/IRT" parameter in SCFG to max possible value (usually 60).
    5. Check if "Tcp/IRT" parameter is changed correctly.
    6. Set "Tcp/IRT" parameter in SCFG to random correct value (e.g. 20).
    7. Check if "Tcp/IRT" parameter is changed correctly.
    8. Try to set some illegal values.
    9. Check if "Tcp/IRT" parameter is changed.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.value_1 = "1"
        test.value_60 = "60"
        test.value_20 = "20"

    def run(test):
        test.log.info("TC0107955.001 TcpIrt_BasicCheck")

        test.log.step("1) Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Set \"Tcp/IRT\" parameter in SCFG to min possible value (usually 1)")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, test.value_1))

        test.log.step("3) Check if \"Tcp/IRT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == test.value_1)

        test.log.step("4. Set \"Tcp/IRT\" parameter in SCFG to max possible value (usually 60).")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, test.value_60))

        test.log.step("5) Check if \"Tcp/IRT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == test.value_60)

        test.log.step("Set \"Tcp/IRT\" parameter in SCFG to random correct value (e.g. 20).")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, test.value_20))

        test.log.step("7) Check if \"Tcp/IRT\" parameter is changed correctly.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == test.value_20)

        test.log.step("8) Try to set some illegal values.")
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "0", expected=test.error))
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "61", expected=test.error))
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "100", expected=test.error))
        test.expect(dstl_set_scfg_tcp_irt(test.dut, "local", expected=test.error))

        test.log.step("9) Check if \"Tcp/IRT\" parameter is changed.")
        test.expect(dstl_get_scfg_tcp_irt(test.dut) == test.value_20)

    def cleanup(test):
        dstl_set_scfg_tcp_irt(test.dut, "3")


if "__main__" == __name__:
    unicorn.main()
