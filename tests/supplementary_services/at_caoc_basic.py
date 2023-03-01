#author: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091808.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.security import unlock_sim_pin2

class Test(BaseTest):
    """
    TC0091808.001 - TpAtCaocBasic
    Intention:
    This procedure provides basic tests for the test and write command of AT+CAOC.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        test.log.step('1. test without PIN')
        test.expect(test.dut.at1.send_and_verify('at+caoc=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+caoc?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+caoc', 'CME ERROR: SIM PIN required'))

        test.log.step('2. test with PIN')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+caoc', '.*CAOC: \"[0-9A-F]{6}\".*'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=?', 'CAOC: \\(0-2\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=0', '.*CAOC: \"[0-9A-F]{6}\".*'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+caoc?', '.*CAOC: 2.*'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+caoc?', '.*CAOC: 1.*'))

        test.log.step('3. check all parameters and also with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+caoc=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+caoc=3', 'ERROR'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()