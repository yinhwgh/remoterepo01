#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0093394.002 -IndSimdata



import unicorn
import random
import re
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control
from dstl.configuration.dual_sim_operation import *






class Indsimdata(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Enable dual sim mode and enable SIM Slot1")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_dual_sim_mode()

        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Enable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_switch_to_sim_slot1()
        test.sleep(2)
        test.dut.dstl_lock_sim()
        test.dut.dstl_switch_to_sim_slot2()
        test.sleep(2)
        test.dut.dstl_lock_sim(test.dut.sim2)
        test.dut.dstl_switch_to_sim_slot1()
        test.sleep(2)
        test.dut.dstl_restart()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Check default simdata staus")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata",0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Turn on Simdata indicator")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enable_one_indicator("simdata"))
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"',"+CIEV: simdata,1,4",wait_for='+CIEV: simdata,1,4'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Change to sim slot2")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.sleep(2)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"',"+CIEV: simdata,1,4",wait_for='+CIEV: simdata,1,4'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_9: Turn off Simdata indicator")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_disable_one_indicator("simdata"))
        test.expect(test.dut.dstl_check_indicator_value("simdata", 0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_10: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"',"OK",wait_for='OK'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_11: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_12:  Change to sim slot1")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin())

        test.log.info("*******************************************************************")
        test.log.info("RunTest_13: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_14: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"',"OK",wait_for='OK'))


        test.log.info("*******************************************************************")
        test.log.info("RunTest_15: Turn on Simdata indicator")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enable_one_indicator("simdata"))
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_16: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"', "+CIEV: simdata,1,4",
                                                 wait_for='+CIEV: simdata,1,4'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_17: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_18: Change to sim slot2")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.sleep(2)
        test.expect(test.dut.dstl_enter_pin(test.dut.sim2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_19: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 1))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_20: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"', "+CIEV: simdata,1,4",
                                                 wait_for='+CIEV: simdata,1,4'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_21: Turn off Simdata indicator")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_disable_one_indicator("simdata"))
        test.expect(test.dut.dstl_check_indicator_value("simdata", 0))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_22: Send sim refresh SSTK command")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010482028182"', "OK", wait_for='OK'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_23: Check simdata status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_check_indicator_value("simdata", 0))


    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("Cleanup_1: Enable dual sim mode and enable SIM Slot1")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_dual_sim_mode()
        test.dut.dstl_switch_to_sim_slot1()

if (__name__ == "__main__"):
    unicorn.main()
