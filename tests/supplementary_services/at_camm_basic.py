#author: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091807.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.security import unlock_sim_pin2

class Test(BaseTest):

    """
    TC0091807.001 - TpAtCammBasic
    Intention:
    This procedure provides basic tests for the test and write command of +CAMM.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        pin2= test.dut.sim.pin2
        test.log.step('1. test without PIN')
        test.expect(test.dut.at1.send_and_verify('at+camm?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+camm=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify(f'at+camm="111111","{pin2}"', 'CME ERROR: SIM PIN required'))

        test.log.step('2. test with PIN')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+camm=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+camm?', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'at+camm="FFFFFF","{pin2}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+camm?', '"FFFFFF"'))
        test.expect(test.dut.at1.send_and_verify(f'at+camm="000000","{pin2}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+camm?', '"000000"'))

        test.log.step('3. check invalid values')
        test.expect(test.dut.at1.send_and_verify(f'at+camm="1000000","{pin2}"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+camm?', '"000000"'))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()