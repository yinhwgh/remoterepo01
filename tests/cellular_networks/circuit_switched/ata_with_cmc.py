#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087916.002


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0087916.002 - TpCAta
    Intention: This test is provided to test command: Call Answer ATA.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r2.dstl_detect()
        test.r2.dstl_register_to_network()

    def run(test):
        dut_num_nat = test.dut.sim.nat_voice_nr
        ignore_char=',TP!W@'
        testnum_1=dut_num_nat+ignore_char
        testnum_2=dut_num_nat[0:3]+"@"+dut_num_nat[3:6]+"!T"+dut_num_nat[6:9]+\
                                     "W,"+dut_num_nat[9:11]+'PP'

        test.log.info('***Test Start***')
        test.log.info('***Notice: Only test voice call temporary***')
        test.log.step('0. Initialization')
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at+ccwa=1,1', 'OK'))

        test.log.step('1. Deactivated CLIR')
        test.expect(test.dut.at1.send_and_verify('at+clir=2', 'OK'))
        test.expect(test.r1.dstl_voice_call_by_number(test.dut, testnum_1))
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(False, 0))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.at1.wait_for('.*NO CARRIER.*'))
        test.sleep(3)

        test.log.step('2. Activated CLIP')
        test.expect(test.dut.at1.send_and_verify('at+clip=1', 'OK'))
        test.expect(test.r1.dstl_voice_call_by_number(test.dut, testnum_2))
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(False, 0))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.at1.wait_for('.*NO CARRIER.*'))

        test.log.step('3.Try to answer a waiting call and then '
                      'switch from the waiting to the incoming state of call and answer it')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut, testnum_1))
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(False, 0))
        test.r2.at1.send_and_verify(f'atd{testnum_2};')
        test.expect(test.dut.at1.wait_for('\+CCWA:'))
        test.sleep(2)
        test.log.info('3.1 Should fail to answer the waiting call by ata')
        test.expect(test.dut.at1.send_and_verify('ata','NO CARRIER', wait_for='NO CARRIER'))
        test.log.info('3.2 After r1 disconnect, can answer call from r2 by ata')
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.at1.wait_for('RING'))
        test.expect(test.dut.at1.send_and_verify('ata', 'OK'))
        test.expect(test.r2.dstl_check_voice_call_status_by_clcc(True, 0))
        test.expect(test.r2.dstl_release_call())

    def cleanup(test):
       test.log.info('***Test End***')



if "__main__" == __name__:
    unicorn.main()
