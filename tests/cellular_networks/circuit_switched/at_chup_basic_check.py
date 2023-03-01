#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091851.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported
class Test(BaseTest):
    '''
    TC0091851.001 - TpAtChupBasic
    Intention: This procedure provides basic tests for the exec command of AtChup.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()

    def run(test):
        dut_phone_num = test.dut.sim.int_voice_nr
        r1_phone_num = test.r1.sim.int_voice_nr

        test.log.info('***Test Start***')
        test.log.info('1. test without pin ')
        test.expect(test.dut.at1.send_and_verify('at+cpin?','SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+chup', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+chup=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+chup?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chup=1', 'ERROR'))
        test.log.info('2. test with pin')
        test.dut.dstl_register_to_network()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at+chup', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+chup=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+chup?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+chup=1', 'ERROR'))

        test.log.info('3.1 MT voice call test')
        test.r1.at1.send_and_verify('at^sm20', 'O')
        test.expect(test.r1.at1.send_and_verify('atd{};'.format(dut_phone_num),'',wait_for=''))
        test.dut.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('ata'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+clcc','.*CLCC: 1,1,0,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+chup'))


        if test.dut.dstl_is_data_call_supported():
            test.log.info('3.2 MT data call test')
            test.expect(test.r1.at1.send_and_verify('atd{}'.format(dut_phone_num),'',wait_for=''))
            test.dut.wait_for('RING')
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify('ata','CONNECT'))
            test.expect(test.r1.at1.wait_for('CONNECT'))
            test.dut.at1.send('+++',end='')
            test.dut.at1.wait_for('OK')

            test.expect(test.dut.at1.send_and_verify('at+clcc', '.*CLCC: 1,0,0,1,0.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+chup'))
            test.expect(test.r1.at1.wait_for('.*NO CARRIER.*'))



    def cleanup(test):
       test.log.info('***Test End***')



if "__main__" == __name__:
    unicorn.main()

