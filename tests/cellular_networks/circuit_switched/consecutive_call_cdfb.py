# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0103915.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle


class Test(BaseTest):
    '''
    TC0103915.001 - ConsecutiveCall_CSFB
    Intention: Check module CSFB consecutive call performance.
               Check call failure rate.
               Duration test.
    Subscriber: 2

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.r1.dstl_restart()
        test.sleep(10)
        test.r1.dstl_register_to_network()
        test.r1_phone_num = test.r1.sim.nat_voice_nr

    def run(test):

        test.log.info('*** Test Start ***')
        test.log.info('1.Register to network.')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.dut.dstl_register_to_gsm()
        for i in range(400):
            test.log.info('***  Start loop {} ***'.format(i+1))
            test.log.info('2.Make voice call from DUT to REMOTE.')
            test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.r1_phone_num)))
            test.log.info('3.Accept the call.')
            test.r1.at1.wait_for('RING')
            test.sleep(2)
            test.expect(test.r1.at1.send_and_verify('ata'))
            test.sleep(2)
            test.expect(
                test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,0,0,0,\"{}\".*OK.*'.format(test.r1_phone_num)))
            test.log.info('4.Disconnect the call from DUT.')
            test.expect(test.dut.at1.send_and_verify('at+chup'))
            test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))
            test.log.info('***  End loop {} ***'.format(i + 1))
            test.sleep(3)


    def cleanup(test):
        test.log.info('*** Test End ***')



if "__main__" == __name__:
    unicorn.main()
