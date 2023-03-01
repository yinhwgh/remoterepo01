#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0102405.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard import devboard
from dstl.configuration import shutdown_smso
from dstl.identification import get_imei


class Test(BaseTest):
    """
    TC0102405.001    MuxChannelRestartShutdown
    Check behavior of MUX channel after module's restart and shutdown.
    responsible: mariusz.wojcik@globallogic.com
    location: Wroclaw
    """

    def setup(test):
        test.dut.at1 = test.dut.mux_1
        test.dut.at1.open()
        test.sleep(10)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step("1. Restart module from MUX channel.")
        test.expect(test.dut.dstl_restart())

        test.log.step("2. Send AT command.")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

        test.log.step("3. Send AT^SMSO from MUX channel.")
        test.expect(test.dut.dstl_shutdown_smso())
        test.sleep(10)

        test.log.step("4. Turn on module using McTest.")
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())

        test.log.step("5. Wait 90 seconds until DUT started and be ready, send AT.")
        test.sleep(90)
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
