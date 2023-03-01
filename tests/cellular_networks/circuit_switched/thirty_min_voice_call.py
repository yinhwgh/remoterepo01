# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0010934.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0010934.001 - 30minVoiceCal
    Intention: test a long call
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_register_to_network()
        test.r1.dstl_restart()
        test.sleep(10)
        test.r1.dstl_register_to_network()

    def run(test):
        r1_phone_num = test.r1.sim.nat_voice_nr

        test.log.info('***Test Start***')

        test.log.info('30 min voice call test')
        test.dut.at1.send_and_verify('at^sm20', 'O')
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata'))
        test.sleep(2)
        time_left = 1800
        while (time_left > 0):

            test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,0,0,0,\"{}\".*OK.*'.format(r1_phone_num)))
            test.sleep(30)
            time_left = time_left - 30
            test.log.info('Test time left :{} sec'.format(time_left))
        test.expect(test.dut.at1.send_and_verify('at+chup'))
        test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))

    def cleanup(test):
        test.log.info('***Test End***')


if "__main__" == __name__:
    unicorn.main()
