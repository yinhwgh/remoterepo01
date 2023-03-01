#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0084780.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0084780.001 - TpCclirFunc
    Intention: This procedure provides function tests for the test and write command of +CLIR.
    Subscriber: 3
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r2.dstl_detect()
        test.r2.dstl_register_to_network()
        test.sleep(3)
        test.nat_dut_phone_num = test.dut.sim.nat_voice_nr
        test.nat_r1_phone_num = test.r1.sim.nat_voice_nr
        test.nat_r2_phone_num = test.r2.sim.nat_voice_nr

    def run(test):

        test.clir_voice_call()
        test.clir_multiparty_call()
        test.invalid_value_check()

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at+ccwa=0,0', '.*OK.*'))

    def clir_voice_call(test):
        test.log.info('clir=0, should display number')
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: [012],[04].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ATD*#77#;', '.*\+COLR: 0,0.*'))
        test.expect(test.dut.at1.send_and_verify(f'ATD{test.nat_r1_phone_num};'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', f'.*\+CLCC: 1,1,4,0,0,"{test.nat_dut_phone_num}",.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.log.info('clir=1, should not display number')
        test.expect(test.dut.at1.send_and_verify('at+clir=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ATD*#77#;', '.*\+COLR: 0,0.*'))
        test.expect(test.dut.at1.send_and_verify(f'ATD{test.nat_r1_phone_num};'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', 'OK'))
        test.expect(f'{test.nat_dut_phone_num}' not in test.r1.at1.last_response)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.log.info('clir=2, should display number')
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: [012],[04].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ATD*#77#;', '.*\+COLR: 0,0.*'))
        test.expect(test.dut.at1.send_and_verify(f'ATD{test.nat_r1_phone_num};'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', f'.*\+CLCC: 1,1,4,0,0,"{test.nat_dut_phone_num}",.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.log.info('suppress clir, should display number')
        test.expect(test.dut.at1.send_and_verify(f'atd*31#{test.nat_r1_phone_num};'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', f'.*\+CLCC: 1,1,4,0,0,"{test.nat_dut_phone_num}",.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.log.info('active clir, should not display number')
        test.expect(test.dut.at1.send_and_verify(f'atd#31#{test.nat_r1_phone_num};'))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', 'OK'))
        test.expect(f'{test.nat_dut_phone_num}' not in test.r1.at1.last_response)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())

    def clir_multiparty_call(test):

        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,1,1', '.*OK.*'))
        test.log.info('r2 suppress clir, should display number')
        test.expect(test.r2.at1.send_and_verify('at+clir=1', '.*OK.*'))
        test.log.info('r1 active clir, should not display number')
        test.expect(test.r1.at1.send_and_verify('at+clir=0', '.*OK.*'))
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};'))
        test.expect(test.dut.at1.wait_for('RING'))
        test.expect(test.dut.at1.send_and_verify('ata', '.*OK.*'))
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify(f'ATD{test.nat_dut_phone_num};'))
        test.expect(test.dut.at1.wait_for('CCWA'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', 'OK'))
        test.expect(f'{test.nat_r1_phone_num}'  in test.dut.at1.last_response)
        test.expect(f'{test.nat_r2_phone_num}' not in test.dut.at1.last_response)

        test.expect(test.dut.at1.send_and_verify('at+chld=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clcc', 'OK'))
        test.expect(f'{test.nat_r1_phone_num}' in test.dut.at1.last_response)
        test.expect(f'{test.nat_r2_phone_num}' not in test.dut.at1.last_response)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.expect(test.r2.at1.send_and_verify('at+clir=0', '.*OK.*'))


    def invalid_value_check(test):
        test.expect(test.dut.at1.send_and_verify('at+clir=A', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=3', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=2,4', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=-1', '.*ERROR.*'))


if "__main__" == __name__:
    unicorn.main()

