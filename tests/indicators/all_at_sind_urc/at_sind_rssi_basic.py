#responsible: wei.guo@thalesgroup.com
#location: Dalian
#TC0105152.001

import unicorn

from core.basetest import BaseTest

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim

class sind_service_basic_check(BaseTest):
    '''
    TC0105152.001--sind_rssi_basic_check

    Test case to check:
    1. Enable/Disable sind\dtmf URC under pin lock/unlock state
    2. Check valid/invalid values setting
    3. Check setting is not in NV, after power up, should be changed to default disabled state
    4. Check query command at^sind="rssi",2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())

    def run(test):
        test.expect(test.dut.dstl_restart())
        test.sleep(10)
        test.log.info("1. Check test/read/write command under pin locked state")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?",".*\(rssi,\(0-5,99\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND?",".*(?s)SIND: rssi,0,\\d+.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",0",".*(?s)SIND: rssi,0,\\d+.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",1",".*(?s)SIND: rssi,1,\\d+.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",2",".*(?s)SIND: rssi,1,\\d+.*"))

        test.log.info("2. Check test/read/write command under pin unlocked state")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", ".*\(rssi,\(0-5,99\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*(?s)SIND: rssi,1.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",0", ".*(?s)SIND: rssi,0.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",1", ".*(?s)SIND: rssi,1.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",2", ".*(?s)SIND: rssi,1.*"))

        test.log.info("3. Check some invalid value, error should be output")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",3",".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",abc",".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",@#$",".*ERROR.*"))

        test.log.info("4. Restart module and check setting is not in NV")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", ".*(?s)SIND: rssi,0.*"))

    def cleanup(test):
        pass

if __name__=='__main__':
    unicorn.main()
