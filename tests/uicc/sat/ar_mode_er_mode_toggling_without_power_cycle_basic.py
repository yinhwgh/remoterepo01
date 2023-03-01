#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095445.001

import unicorn
from core.basetest import BaseTest
from dstl.security import lock_unlock_sim
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.usat import ssta_command


class ARmodeERmodeTogglingwithoutPowercycleBasic(BaseTest):
    """
        TC0095445.001 - ARmodeERmodeTogglingwithoutPowercycleBasic
        Function: Check if AR mode and ER mode can be toggled without power cycle.
        Debugged: Dingo, Jakarta
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_unlock_sim())
        test.expect(test.dut.at1.send_and_verify("AT^SSTA=0", ".*OK.*"))  #initialize to AR mode
        test.dut.dstl_restart()

    def run(test):
        total_times = 5
        test.dut.at1.log.info("This test is going to loop for {} times".format(total_times))
        for loop_count in range(1, total_times + 1):
            test.dut.at1.log.info("This is {} of {} times".format(loop_count, total_times))
            # change to ER mode and check value
            test.expect(test.dut.dstl_set_and_check_ssta_mode(new_value="1", old_value="0", restart=False))
            # restart and check value
            test.expect(test.dut.dstl_set_and_check_ssta_mode(new_value="1", old_value="1", restart=True))
            # change to AR mode and check value
            test.expect(test.dut.dstl_set_and_check_ssta_mode(new_value="0", old_value="1", restart=False))
            # restart and check value
            test.expect(test.dut.dstl_set_and_check_ssta_mode(new_value="0", old_value="0", restart=True))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SSTA=0", ".*OK.*"))  #restore to AR mode
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_restart()


if "__main__" == __name__:
    unicorn.main()


