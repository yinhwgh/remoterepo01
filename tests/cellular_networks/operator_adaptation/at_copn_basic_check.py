#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091859.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.auxiliary import init

class Test(BaseTest):
    '''
    TC0091859.001 - TpAtCopnBasic
    '''
    def setup(test):
        test.dut.dstl_detect()

    def run(test):

        test.log.info('1.Check command without pin')
        test.dut.dstl_restart()
        test.dut.at1.send_and_verify('at+cpin?')
        if 'READY' in test.dut.at1.last_response:
            test.dut.dstl_lock_sim()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+copn=?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn', '.*ERROR.*'))

        test.log.info('2.Check command with pin')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+copn=?', '.*\sOK\s.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn', '.*\sOK.*', timeout=30))

        test.log.info('3.Check for invalid parameter')
        test.expect(test.dut.at1.send_and_verify('at+copn?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+copn=-0', '.*ERROR.*'))

        test.log.info('4.Check output of +COPN ')
        test.expect(test.dut.at1.send_and_verify('at+copn', '.*\sOK.*', timeout=30))



    def cleanup(test):
        pass
if "__main__" == __name__:
    unicorn.main()
