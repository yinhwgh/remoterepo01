#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0095761.001-SindSimtrayStressTest
'''
Test with McTest4 board
'''

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_remove_sim,dstl_insert_sim
from dstl.auxiliary.restart_module import dstl_restart
from dstl.status_control.extended_indicator_control import dstl_enable_one_indicator
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

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Remove SIM tray")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_remove_sim())

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Enable simtray indicator in AT^SIND")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator("simtray",True,0)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: insert SIM tray then remove SIM tray for 100 times")
        test.log.info("*******************************************************************")
        for i in range(100):
            test.dut.at1.send_and_verify('at+cmer=2,0,0,2', 'OK')
            test.dut.devboard.send("MC:CCIN=0")
            test.expect(test.dut.at1.wait_for("+CIEV: simtray,1"))

            test.dut.devboard.send("MC:CCIN=1")
            test.expect(test.dut.at1.wait_for("+CIEV: simtray,0"))
            test.log.info("*******************************************************************")
            test.log.info(f"Stress test loop {i+1} finished")
            test.log.info("*******************************************************************")


    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Iinsert the SIM card and disable simtray indicator")
        test.log.info("*******************************************************************")
        test.dut.devboard.send("MC:CCIN=0")
        test.dut.dstl_disable_one_indicator("simtray", True, 1)

if (__name__ == "__main__"):
    unicorn.main()