#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091804.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0091804.001 - TpAtColpBasic
    Intention: This procedure provides the possibility of basic tests for the test and write command of +COLP.
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
        test.expect(test.dut.at1.send_and_verify('at+colp=?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+colp?', 'CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+colp=1', 'CME ERROR: SIM PIN required'))


        test.log.step('2. Check command with PIN.')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+colp=?', '.*\+COLP: \(0[,-]1\).*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=0', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 0,[012]\s+.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=1', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 1,[012]\s+.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 0,[012]\s+.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp=1', '.*OK.*', timeout=15))
        test.expect(test.dut.at1.send_and_verify('at+colp?', '.*\+COLP: 1,1\s+.*OK.*', timeout=15))

        test.log.step('3. Functional test.')

        test.expect(test.dut.at1.send_and_verify(f'atd{nat_r1_phone_num};', ''))
        test.expect(test.r1.at1.wait_for('RING'))
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.expect(test.dut.at1.wait_for(f'.*\+COLP: .*{nat_r1_phone_num}.*'))
        test.expect(test.dut.at1.send_and_verify('at+clcc','.*\+CLCC: 1,0,0,0,0.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.at1.send_and_verify('at+colp=0', '.*OK.*', timeout=15))

        test.log.step('4. Negative test.')
        test.expect(test.dut.at1.send_and_verify('at+colp=-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+colp=2', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+colp=1,1', '.*ERROR.*'))

    def cleanup(test):
        pass



if "__main__" == __name__:
    unicorn.main()

