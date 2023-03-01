#responsible: baris.kildi@thalesgroup.com
#location: Berlin
# tests for JIRA

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.at1.send_and_verify('at+cpin?')
        if 'READY' in test.dut.at1.last_response:
            test.dut.dstl_lock_sim()


    def run(test):

        test.dut.dstl_restart()
        test.log.info('1.Check command without pin')
        if (test.dut.project == "COUGAR"):
            test.expect(test.dut.at1.send_and_verify('at+copn=?', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+copn', '.*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+copn=?', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('at+copn', '.*ERROR.*'))

        test.log.info('2.Check command with pin')
        test.dut.dstl_enter_pin()
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+copn=?', '.*\sOK\s.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn', '.*\sOK\s.*', timeout=10))

        test.log.info('3.Check for invalid parameter')
        test.expect(test.dut.at1.send_and_verify('at+copn?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=-0', '.*ERROR.*'))

        test.log.info('4.Check output of +COPN ')
        test.expect(test.dut.at1.send_and_verify('at+copn', '.*\sOK\s.*', timeout=10))



    def cleanup(test):
        pass
if "__main__" == __name__:
    unicorn.main()
