#author: yuan.gao@thalesgroup.com
#location: Dalian
#TC0095176.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module

class Test(BaseTest):
    '''
    TC0095176.001 - sindeonsbasicchecking
    Check the status of indicator +CIEV: "eons" (Enhanced Operator Name String) before and after module registering to network.
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.info("1. Check SIM lock status")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*"))

        test.log.info("2. Check SIND status for eons")
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", '(?s)SIND: eons,0,0,"","",0.*'))

        test.log.info("3. Enable the eons indicator: AT^SIND=eons,1 on the module")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"eons\",1", '(?s)SIND: eons,1,0,"","",0.*'))

        test.log.info("4. Enable creg indication with at+creg=2")
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))

        test.log.info("5. Enter Sim PIN and wait for module registering to network.")
        test.expect(test.dut.dstl_enter_pin())

        test.log.info("6. Check for +CIEV: eons, ,, URC on AT interface")
        test.expect(test.dut.at1.wait_for(".*\+CIEV: eons,4,\".*", timeout=20))

        test.log.info("7-8. Deregister module from network with at+cops=2.Check for +CIEV: eons,0,"","",0 URC")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*\+CIEV: eons,0,\"\",\"\",0.*", timeout=20))

        test.log.info("9. Disable the eons indicator: AT^SIND=eons,0 on the module")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=eons,0", ".*\^SIND: eons,0,.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if '__main__' == __name__:
    unicorn.main()
