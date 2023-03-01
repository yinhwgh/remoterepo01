# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108211.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board


class Test(BaseTest):
    """
       TC0108211.001 - SWShutDownTime
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.sleep(2)

    def run(test):
        test.log.step("1. Send AT^SMSO=? And check response")
        test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK"), critical=True)

        test.log.step("2. Send AT^SMSO command")
        test.expect(test.dut.dstl_shutdown_smso())

        test.log.step("3. Using McTest check if module is Off(MC:PWRIND) with in 1s after URC pop out")
        test.expect(test.dut.devboard.send_and_verify('MC:PWRIND', '.*PWRIND: 1.*', wait_for='.*PWRIND: 1.*', timeout=1), critical=True)
        test.sleep(2)

        test.log.step("4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
        test.dut.at1.wait_for('.*SYSSTART.*')
        test.sleep(10)

        test.log.step("5. Send AT command to check if communication with module is possible")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK"))

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


if "__main__" == __name__:
    unicorn.main()