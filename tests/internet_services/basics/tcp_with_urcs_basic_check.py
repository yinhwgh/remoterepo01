# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107956.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs, \
    dstl_get_scfg_tcp_with_urcs


class Test(BaseTest):
    """
    Intention:
    To check if it is possible to set the "Tcp/WithURCs" parameter in SCFG.

    Detailed description:
    1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
    2. Set "Tcp/WithURCs" parameter in SCFG to off.
    3. Check if "Tcp/WithURCs" parameter is changed correctly.
    4. Set "Tcp/WithURCs" parameter in SCFG to on.
    5. Check if "Tcp/WithURCs" parameter is changed correctly.
    6. Try to set some illegal value (e.g. "local", "0")
    7. Check if "Tcp/WithURCs" parameter is changed.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.value_off = "off"
        test.value_on = "on"

    def run(test):
        test.log.info("TC0107956.001 TcpWithURCs_BasicCheck")

        test.log.step("1. Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Set \"Tcp/WithURCs\" parameter in SCFG to off.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, test.value_off))

        test.log.step("3. Check if \"Tcp/WithURCs\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("4. Set \"Tcp/WithURCs\" parameter in SCFG to on.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, test.value_on))

        test.log.step("5. Check if \"Tcp/WithURCs\" parameter is changed correctly.")
        test.log.info("Done in previous step")

        test.log.step("6. Try to set some illegal value (e.g. \"local\", \"0\")")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "local", expected=test.error))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "0", expected=test.error))

        test.log.step("7. Check if \"Tcp/WithURCs\" parameter is changed.")
        test.expect(dstl_get_scfg_tcp_with_urcs(test.dut, test.value_on))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()