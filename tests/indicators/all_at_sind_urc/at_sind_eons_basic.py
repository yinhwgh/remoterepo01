#responsible: wei.guo@thalesgroup.com
#location: Dalian
#TC0105073.001

import unicorn

from core.basetest import BaseTest

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim

class sind_eons_basic_check(BaseTest):
    '''
    TC0105073.001 - sindeonsbasicchecking
    Test case to check test/read/write command of at^sind="eons", as well as invalid setting/pin protected/query command.
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())

    def run(test):
        test.expect(test.dut.dstl_restart())
        test.log.info("1. Check test/read/write command under pin locked state")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", ".*\(eons,\(0-6\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", '(?s)SIND: eons,0,0,"","",0.*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",0", '(?s)SIND: eons,0,0,"","",0.*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",1", '(?s)SIND: eons,1,0,"","",0.*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",2", '(?s)SIND: eons,1,0,"","",0.*'))

        test.log.info("2. Check test/read/write command under pin unlocked state")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", ".*\(eons,\(0-6\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", '(?s)SIND: eons,1,4,"[\w\s]+","[\w\s]+",[012].*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",0", '(?s)SIND: eons,0,4,"[\w\s]+","[\w\s]+",[012].*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",1", '(?s)SIND: eons,1,4,"[\w\s]+","[\w\s]+",[012].*'))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",2", '(?s)SIND: eons,1,4,"[\w\s]+","[\w\s]+",[012].*'))

        test.log.info("3. Check some invalid value, error should be output")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",3",".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",abc", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",@$#", ".*ERROR.*"))

        test.log.info("4. Restart module and check setting is not in NV")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_switch_ue_to_normal_functionality_level())
        test.expect(test.dut.at1.send_and_verify("AT^SIND?",'(?s)SIND: eons,0.*'))

    def cleanup(test):
        pass

if __name__=='__main__':
    unicorn.main()
