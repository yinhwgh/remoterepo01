#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091805.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0091805.001 - TpAtClirBasic
    Intention: This procedure provides the possibility of basic tests for the test and write command of +CLIR.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.sleep(3)

    def run(test):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr

        test.log.step('1. Check command without PIN.')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+clir=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+clir=1', 'CME ERROR: SIM PIN required'))

        test.log.step('2. Check command with PIN.')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+clir=?', '.*\+CLIR: \(0-2\)\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: [012],[04].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 2,[04].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 1,[04].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 0,[04].*OK.*'))


        test.log.step('3. Functional test.')
        test.expect(test.dut.at1.send_and_verify('at+clir=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 2,.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('at+clip=1', '.*OK.*'))

        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};', ''))
        test.expect(test.r1.at1.wait_for(f'.*\+CLIP: "{nat_dut_phone_num}",.*'))

        test.expect(test.dut.dstl_release_call())
        test.sleep(6)
        test.expect(test.dut.at1.send_and_verify('at+clir=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 1,.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.send_and_verify('at+clcc', '.*OK.*'))
        test.expect(f'{nat_dut_phone_num}' not in test.r1.at1.last_response)

        test.expect(test.dut.dstl_release_call())
        test.sleep(6)
        test.expect(test.dut.at1.send_and_verify('at+clir=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir?', '.*\+CLIR: 0,.*OK.*'))

        test.expect(test.r1.at1.send_and_verify('at+clip=0', '.*OK.*'))

        test.log.step('3. Negative test.')
        test.expect(test.dut.at1.send_and_verify('at+clir=-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=3', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+clir=0,1', '.*ERROR.*'))


    def cleanup(test):
        pass



if "__main__" == __name__:
    unicorn.main()

