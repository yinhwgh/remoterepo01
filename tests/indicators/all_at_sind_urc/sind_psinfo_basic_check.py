#responsible: hui.yu@thalesgroup.com
#location: Dalian
#TC0105198.001

#!/usr/bin/env unicorn
"""

This file represents Unicorn test template, that should be the base for every new test. Test can be executed with
unicorn.py and test file as parameter, but also can be run as executable script as well. Code defines only what is
necessary while creating new test. Examples of usage can be found in comments. For more details please refer to
basetest.py documentation.

"""
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class Test(BaseTest):
    """TC0105198.001 - sind_psinfo_basic_check

    Feature:
    Products:   Viper: PLS63/PLS83
    Intention:
    End state:
    Devices:    DUT_ASC0
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        """Run method.
            1. Enable/Disable sind\psinfo URC under pin lock/unlock state
            2. Check valid/invalid values setting
            3. Check setting is not in NV, after power up, should be changed to default disabled state
            4. Check query command at^sind="psinfo",2
        """
        test.log.info("1. Check test/read/write command under pin locked state")
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*SIND: psinfo,0,0", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", "psinfo,\(0\-10,16,17\)", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",0", ".*SIND: psinfo,0,0", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",1", ".*SIND: psinfo,1,0", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",2", ".*SIND: psinfo,1,0", wait_for="OK"))

        test.log.info("2. Check test/read/write command under pin unlocked state")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*SIND: psinfo,1,([0-9]|10|16|17)\s+", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", "psinfo,\(0\-10,16,17\)", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",0", ".*SIND: psinfo,0,([0-9]|10|16|17)\s+", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",1", ".*SIND: psinfo,1,([0-9]|10|16|17)\s+", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",2", ".*SIND: psinfo,1,([0-9]|10|16|17)\s+", wait_for="OK"))

        test.log.info("3. Check some invalid value, error should be output")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",3",".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",abc",".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",@#$",".*ERROR.*"))

        test.log.info("4. Restart module and check setting is not in NV")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*SIND: psinfo,0.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"psinfo\",0", ".*SIND: psinfo,0,([0-9]|10|16|17)\s+", wait_for="OK"))

if "__main__" == __name__:
    unicorn.main()
