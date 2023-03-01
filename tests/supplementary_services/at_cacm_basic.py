#author: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091806.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.security import unlock_sim_pin2

class Test(BaseTest):
    """
    TC0091806.001 - TpAtCacmBasic
    Intention:
    This procedure provides basic tests for the test and write command of +CACM.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. test without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cacm=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cacm=', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cacm?', 'CME ERROR: SIM PIN required'))

        test.log.step('2. test with PIN')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+cacm=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cacm="000000"', 'CME ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+cacm?', 'CACM: \"[0-9A-F]{6}\"'))

        test.log.step('3. check all parameters and also with invalid values')
        test.dut.dstl_enter_pin2()

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()