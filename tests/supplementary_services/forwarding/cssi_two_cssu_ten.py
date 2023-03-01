# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0084444.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    '''
   TC0084444.001 - TpCcssiTwoCssuTen
    Intention: Cssn functional test
    Subscriber: 4
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r2.dstl_detect()
        test.r3.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.expect(test.r3.dstl_register_to_network())
        test.sleep(3)
        test.nat_dut_phone_num = test.dut.sim.nat_voice_nr
        test.nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr
        test.nat_r3_phone_num = test.r3.sim.nat_voice_nr

    def run(test):
        test.set_cssn(0, 0)
        test.cssi_two_check(False)
        test.cssu_ten_check(False)
        test.set_cssn(0, 1)
        test.cssi_two_check(False)
        test.cssu_ten_check(True)
        test.set_cssn(1, 0)
        test.cssi_two_check(True)
        test.cssu_ten_check(False)
        test.set_cssn(1, 1)
        test.cssi_two_check(True)
        test.cssu_ten_check(True)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', 'OK'))

    def set_cssn(test, n, m):
        test.expect(test.dut.at1.send_and_verify(f'AT+CSSN={n},{m}', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSSN?', f'\+CSSN: {n},{m}.*OK.*'))

    def cssi_two_check(test, cssn_n):
        test.log.info('Test URC CSSI: 2')
        test.expect(test.r1.at1.send_and_verify(f'AT+CCFC=0,3,"{test.nat_r2_phone_num}"', 'OK'))
        test.dut.at1.send_and_verify(f'ATD{test.nat_r1_phone_num};')
        test.expect(test.r2.at1.wait_for('RING'))
        if cssn_n:
            test.log.info('CSSI URC should appear')
            test.expect(test.dut.at1.wait_for('CSSI: 2'))
        else:
            test.log.info('CSSI URC should not appear')
            test.expect(test.dut.at1.wait_for('.*CSSI.*') == False)

        test.dut.dstl_release_call()
        test.expect(test.r1.at1.send_and_verify('AT+CCFC=4,4', 'OK'))

    def cssu_ten_check(test, cssn_m):
        test.log.info('Test URC CSSU: 10')
        test.expect(test.dut.at1.send_and_verify(f'AT+CCFC=0,3,"{test.nat_r3_phone_num}"', 'OK'))
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.nat_r1_phone_num))

        test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};')
        if cssn_m:
            test.log.info('CSSU URC should appear')
            test.expect(test.dut.at1.wait_for('CSSU: 10'))
        else:
            test.log.info('CSSU URC should not appear')
            test.expect(test.dut.at1.wait_for('.*CSSU.*') == False)
        test.expect(test.r3.at1.wait_for('RING'))
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.r2.dstl_release_call()
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', 'OK'))


if "__main__" == __name__:
    unicorn.main()
