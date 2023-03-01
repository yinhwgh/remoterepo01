#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0095758.001-TpSindSimtray
'''
Test with McTest4 board
'''

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_remove_sim,dstl_insert_sim
from dstl.auxiliary.restart_module import dstl_restart
from dstl.status_control.extended_indicator_control import dstl_enable_one_indicator,dstl_check_indicator_value,dstl_disable_one_indicator
from dstl.security.lock_unlock_sim import dstl_unlock_sim,dstl_lock_sim
from dstl.auxiliary.init import dstl_detect


class SindSimtrayStressTest(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate DUT and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Enable DUT SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Check the simtray indicator in AT^SIND")
        test.log.info("*******************************************************************")
        test.dut.dstl_check_indicator_value("simtray", 0, 1)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Enable simtray indicator in AT^SIND")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enable_one_indicator("simtray", True, 1))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Remove SIM tray")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,0"))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: insert SIM tray")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,1"))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))
        test.sleep(2)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Repeat above steps after input PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,0"))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 0))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,1"))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 1, 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Repeat above steps after restart module")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_indicator_value("simtray", 0, 1))
        test.expect(test.dut.dstl_enable_one_indicator("simtray", True, 1))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,0"))
        test.sleep(2)
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", "OK"))
        test.expect(test.dut.at1.wait_for("\+CIEV: simtray,1"))


        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Disable the simtray indicator in AT^SIND and remove/insert sim card ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_disable_one_indicator("simtray", True, 1))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1", "OK"))
        test.expect(test.dut.dstl_check_indicator_value("simtray", 0, 0))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", "OK"))
        test.sleep(1)
        test.expect(test.dut.dstl_check_indicator_value("simtray", 0, 1))

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Iinsert the SIM card and disable simtray indicator")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", "OK"))
        test.dut.dstl_disable_one_indicator("simtray", True, 1)


if (__name__ == "__main__"):
    unicorn.main()