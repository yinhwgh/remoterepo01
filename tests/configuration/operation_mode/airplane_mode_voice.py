# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0010870.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import functionality_modes
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0010870.001 - TpAirplaneModeVoice
    Collision between airplane mode and voice call.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

    def run(test):
        exp_atd_airplane_error = 'NO CARRIER'
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr

        if test.dut.project is 'VIPER' or test.dut.project is 'MIAMI':
            exp_atd_airplane_error = '\+CME ERROR: operation not supported'

        test.log.step('1.Subscriber1 makes a voice call to subscriber 2 - sub 2 answers the call')
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, nat_r1_phone_num))

        test.log.step('2.Subscriber1 try to enter airplane mode, should return appropriate error message')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.r1.at1.wait_for('NO CARRIER'))

        test.log.step('3.Subscriber1 enter airplane mode,make call, should return appropriate error message')
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};',
                                                 expect=exp_atd_airplane_error, wait_for=exp_atd_airplane_error))

        test.log.step('4.Subscriber 2 makes a voice call to subscriber 1, should return NO CARRIER')
        test.expect(test.r1.at1.send_and_verify(f'atd{nat_dut_phone_num};',
                                                expect='', wait_for='NO CARRIER', timeout=60))
        test.expect(test.r1.at1.send_and_verify('at+chup', 'OK'))

        test.log.step('5.try to send Emergency call')
        test.expect(test.dut.at1.send_and_verify('atd112;', exp_atd_airplane_error))

        test.log.step('6.deactivate airplane mode')
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.dut.dstl_register_to_network()
        test.sleep(3)

        test.log.step('7.Subscriber1 makes a voice call to subscriber 2, it is possible')
        ret = test.expect(test.dut.dstl_voice_call_by_number(test.r1, nat_r1_phone_num))
        test.sleep(3)
        if ret is True:
            test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,0,0,0,.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+chup', 'OK'))
            test.expect(test.r1.at1.wait_for('NO CARRIER'))
        else:
            test.dut.at1.send_and_verify('at+clcc', 'OK')
            test.dut.at1.send_and_verify('at^smoni', 'OK')

    def cleanup(test):
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.dut.dstl_register_to_network()
        pass


if "__main__" == __name__:
    unicorn.main()
