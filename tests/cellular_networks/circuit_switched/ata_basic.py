#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091842.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0091842.001 - TpAtABasic
    Intention: This procedure provides basic tests for the exec command of AtA.
    Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_register_to_network()

    def run(test):
        dut_phone_num = test.dut.sim.int_voice_nr
        r1_phone_num = test.r1.sim.int_voice_nr

        test.log.info('***Test Start***')
        test.log.info('1. test without pin ')
        test.expect(test.dut.at1.send_and_verify('at+cpin?','SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('ata', '.*NO CARRIER.*|ERROR', wait_for='.*NO CARRIER.*|ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata=1', 'ERROR'))
        test.log.info('2. test with pin')
        test.dut.dstl_register_to_network()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('ata', '.*NO CARRIER.*|ERROR', wait_for='.*NO CARRIER.*|ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata=?', '.*NO CARRIER.*|ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata?', '.*NO CARRIER.*|ERROR'))
        test.expect(test.dut.at1.send_and_verify('ata=1', '.*NO CARRIER.*|ERROR'))

        test.log.info('3. Function test')
        test.log.info('3.1 MT voice call test')
        test.r1.at1.send_and_verify('at^sm20=0', 'O')
        test.expect(test.r1.dstl_voice_call_by_number(test.dut,dut_phone_num))
        test.sleep(3)
        test.expect(test.r1.at1.send_and_verify('at+clcc','.*CLCC: 1,0,0,0,0.*OK.*'))
        test.expect(test.r1.dstl_release_call())
        test.expect(test.dut.at1.wait_for('.*NO CARRIER.*'))

        if test.dut.dstl_is_data_call_supported():
            test.log.info('3.2 MT data call test')
            test.log.info('As current product not support data call, pending for implement.')


    def cleanup(test):
       test.log.info('***Test End***')



if "__main__" == __name__:
    unicorn.main()
