# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0102407.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.configuration import shutdown_smso


class Test(BaseTest):
    """
    Check behavior of MUX channel after multiple restart and shutdown of module.

    1. Restart DUT from mux channel.
    2. Send AT command.
    3. Send AT^SMSO from mux channel.
    4. Turn on module using McTest.
    5. Wait 60 seconds until DUT started, send AT.
    Repeat steps 1-5 100 times.
    """

    def setup(test):
        test.dut.at1 = test.dut.mux_1
        test.dut.at1.open()
        test.sleep(10)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.info("Repeat steps 1-5 100 times.")
        for iteration in range(100):
            test.log.info("REPEATING STEPS 1-5: ITERATION {}/100".format(iteration + 1))
            test.log.step("1. Restart DUT from mux channel.")
            test.expect(test.dut.dstl_restart())

            test.log.step("2. Send AT command.")
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))

            test.log.step("3. Send AT^SMSO from mux channel.")
            test.expect(test.dut.dstl_shutdown_smso())

            test.log.step("4. Turn on module using McTest.")
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())

            test.log.step("5. Wait 60 seconds until DUT started, send AT.")
            test.expect(test.dut.at1.wait_for("SYSSTART", timeout=60))
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))

    def cleanup(test):
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.close()


if "__main__" == __name__:
    unicorn.main()
