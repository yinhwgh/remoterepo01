#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0093828.001

import unicorn
import random

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import init
from dstl.configuration import dual_sim_operation


class DualSimRegisterHomeNetwork(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("Setup_1: Initiate module and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))

        test.log.info("*******************************************************************")
        test.log.info("Setup_2. Enable SIM PIN lock before testing")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.sleep(2)
        pass

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("Test_1: Input SIM PIN and regesiter to network ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("*******************************************************************")
        test.log.info("Test_2: Eanble Dual SIM mode and switch to SIM slot2")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enable_dual_sim_mode())
        test.sleep(5)
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.sleep(5)

        test.log.info("*******************************************************************")
        test.log.info("Test_3: Register to network with sim slot2")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_enter_pin(test.dut.sim2))
        test.sleep(15)
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("*******************************************************************")
        test.log.info("Test_4: Switch back to sim slot1, module will regsiter to network after input PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(30)
        test.expect(test.dut.dstl_check_network_status())

        test.log.info("*******************************************************************")
        test.log.info("Test_5: Switch back to sim slot2, module will regsiter to network after input PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin(test.dut.sim2))
        test.sleep(30)
        test.expect(test.dut.dstl_check_network_status())

        test.log.info("*******************************************************************")
        test.log.info("Test_6: Switch back to sim slot1, module will regsiter to network after input PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(30)
        test.expect(test.dut.dstl_check_network_status())

        test.log.info("*******************************************************************")
        test.log.info("Test_7: Disable Dual SIM mode.")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_disable_dual_sim_mode())
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(30)
        test.expect(test.dut.dstl_check_network_status())

        test.log.info("*******************************************************************")
        test.log.info("Test_8: Check it is not allowed to switch to sim slot2 while dual sim mode is disabled.")
        test.log.info("*******************************************************************")
        test.expect(not test.dut.dstl_switch_to_sim_slot2())

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("Cleanup_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.at1.send_and_verify(r'AT&F','.*OK')
        test.dut.at1.send_and_verify(r'AT&W', '.*OK')

        test.log.info("*******************************************************************")
        test.log.info("Cleanup_2: Disable dual sim mode ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_disable_dual_sim_mode())



if (__name__ == "__main__"):
    unicorn.main()
