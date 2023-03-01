# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091801.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0091801.001 - TpAtCcwaBasic
    This procedure provides the possibility of basic tests for the test and write command of +CCWA.
    Subscriber: 3
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r2.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.sleep(3)

        test.int_dut_phone_num = test.dut.sim.int_voice_nr
        test.int_r1_phone_num = test.r1.sim.int_voice_nr
        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr
        if test.nat_r2_phone_num.startswith('0'):
            test.r2_phone_num_regexpr = ".*" + test.nat_r2_phone_num[1:]

    def run(test):
        test.log.step('1. test write and read commands without pin')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1', '\+CME ERROR: SIM PIN required'))

        test.log.step('2. test with pin')
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,0,255', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=?', '.*\+CCWA: \(0[,-]1\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('aat+ccwa=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('aat+ccwa?', '.*\+CCWA: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,2', '.*\+CCWA: 1,1.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,0,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,2', '.*\+CCWA: 0,(1|255).*OK'))

        test.log.step('3. test with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,3', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,2,-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,2,256', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,2,255', '.*\+CCWA: 0,(1|255).*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,2,1', '.*\+CCWA: 0,(1|255).*OK.*'))

        test.log.step('4. function checks')
        test.expect(test.dut.at1.send_and_verify('at+CCFC=4,0', 'OK|ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,2', '.*\+CCWA: 1,1.*OK'))

        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.int_r1_phone_num))
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.int_dut_phone_num};','.*'))
        test.expect(test.dut.at1.wait_for(f".*\+CCWA:.*{test.r2_phone_num_regexpr}.*"))

        test.expect(test.r2.dstl_release_call())
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())

        test.expect(test.dut.at1.send_and_verify('at+ccwa=,0,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccwa=,2', '.*\+CCWA: 0,(1|255).*OK'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
