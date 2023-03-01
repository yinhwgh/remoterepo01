#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0095743.001 - TpCcinSimDetectionNormalAndAirplane

"""
Check the status of uicc card during normal/airplane mode.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.status_control import extended_indicator_control
from dstl.auxiliary import check_urc
from dstl.configuration.functionality_modes import *


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(5)

    def run(test):
        test.log.step("1. Check the status without PIN in normal function **")
        test.log.info("** set the mode to normal function")
        test.dut.dstl_set_functionality_mode(1)
        check_sim_status_remove_insert(test)

        test.log.step("2. Check the status with PIN in normal function **")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        check_sim_status_remove_insert(test)

        test.log.step("3. Check the status in airplane function **")
        test.log.info("** set the mode to airplane mode")
        test.dut.dstl_set_functionality_mode(4)
        check_sim_status_remove_insert(test)

        test.log.step("4. Check the status in Minimum Functionality mode **")
        test.dut.dstl_set_functionality_mode(1)
        test.log.info("** Activate URC simtray & scks **")
        test.expect(test.dut.dstl_enable_one_indicator("simtray"))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
        test.log.info("** Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))
        test.log.info("** set the mode to Minimum Functionality mode")
        test.dut.dstl_set_functionality_mode(0)
        test.expect(test.dut.dstl_check_urc("^SCKS: 0"))
        test.log.info("** Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,0\s+OK\s+"))
        test.dut.dstl_set_functionality_mode(1)
        test.expect(test.dut.dstl_check_urc("^SCKS: 1"))
        test.log.info("** Check the setting **")
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))

        test.log.step("5. Restore default setting **")
        test.log.info("** Deactivate URC simtray & scks **")
        test.expect(test.dut.dstl_disable_one_indicator("simtray"))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS=0", ".*OK*."))



    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


def check_sim_status_remove_insert(test):
    test.log.info("** Check the setting **")
    test.expect(test.dut.dstl_check_indicator_value("simtray", 0))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 0,1\s+OK\s+"))
    test.log.info("** Activate URC simtray & scks **")
    test.expect(test.dut.dstl_enable_one_indicator("simtray"))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
    test.log.info("** Check the setting **")
    test.expect(test.dut.dstl_check_indicator_value("simtray", 1))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))
    test.log.info("** Remove SIM Card **")
    test.dut.dstl_remove_sim()
    test.sleep(2)
    test.expect(test.dut.dstl_check_urc("^SCKS: 0"))
    test.expect(test.dut.dstl_check_urc("+CIEV: simtray,0"))
    test.log.info("** Check the setting **")
    test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 0))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,0\s+OK\s+"))
    test.log.info("** Insert SIM Card **")
    test.dut.dstl_insert_sim()
    test.sleep(2)
    test.expect(test.dut.dstl_check_urc("^SCKS: 1"))
    test.expect(test.dut.dstl_check_urc("+CIEV: simtray,1"))
    test.log.info("** Check the setting **")
    test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))
    test.log.info("** Deactivate URC simtray & scks **")
    test.expect(test.dut.dstl_disable_one_indicator("simtray"))
    test.expect(test.dut.at1.send_and_verify("AT^SCKS=0", ".*OK*."))


if (__name__ == "__main__"):
    unicorn.main()
