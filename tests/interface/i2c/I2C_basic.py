#responsible: haofeng.ding@thalesgroup.com
#location: Dalian
#TC0103492.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.devboard import devboard
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module


class I2C_basic(BaseTest):
    """
        Testcase Version: TC0103492.001
        Intention: Basic test checking if connection with I2C external device can be established.
        Description:
                    1. Send test command AT^SSPI=? - Command should be accepted.
                    2. Send read command AT^SSPI? - Command should be accepted.
                    3. Send write command for I2C interface- at^sspi=0000,0000,0000 -"CONNECT" should be returned.
                    4. Close connection using # - "OK" should be returned.
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info("Step 1: Send test command")
        test.expect(test.dut.at1.send_and_verify('AT^SSPI=?', '.*OK.*'))
        test.log.info("Step 2: Send read command")
        test.expect(test.dut.at1.send_and_verify('AT^SSPI?', '.*OK.*'))
        test.log.info("Step 3: Send write command for I2C interface")
        test.expect(test.dut.at1.send_and_verify('AT^SSPI=0000,0000,0000', '.*CONNECT.*'))
        test.log.info("Step 4: Close connection using #")
        test.expect(test.dut.at1.send_and_verify('#', '.*OK.*'))
        test.log.info("Step 5: Basic test")
        test.expect(test.dut.at1.send_and_verify('AT^SSPI=0000,0000,0000', '.*CONNECT.*'))
        test.expect(test.dut.at1.send_and_verify('<aA0000012345678>', '{a+}'))
        test.expect(test.dut.at1.send_and_verify('<aA00000>', '{a+}'))
        test.expect(test.dut.at1.send_and_verify('<aA10004>', '{a+12345678}'))
        test.expect(test.dut.at1.send_and_verify('#', '.*OK.*'))
    def cleanup(test):

        pass

if(__name__ == "__main__"):
    unicorn.main()
