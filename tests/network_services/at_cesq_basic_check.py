#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093912.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.security import set_sim_waiting_for_pin1
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    '''
    TC0093912.001 - TpAtCesqBasic
    Subscriber :2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.sleep(10)

    def run(test):
        test.log.info('1.Test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))

        test.expect(test.dut.at1.send_and_verify('AT+CESQ=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ', 'ERROR'))

        test.log.info('2.Test with pin')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('AT+CESQ=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*\d+,\d+,\d+,\d+,\d+,\d+.*OK.*'))

        test.log.info('3.Test invalid parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CESQ=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ=1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ=19,19', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CESQ?', 'ERROR'))

        test.log.info('4.Function check')
        if test.dut.dstl_is_gsm_supported():
            test.log.info('Test 2G network') #
            test.expect(test.dut.dstl_register_to_gsm())
            test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*\d+,\d+,255,255,255,255.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMONI', '\^SMONI: 2G,.*OK.*'))
            if test.dut.dstl_is_voice_call_supported():
                test.r1.dstl_register_to_network()
                phonenum = test.r1.sim.nat_voice_nr
                test.dut.at1.send_and_verify('at^sm20=0', 'OK|ERROR')
                test.expect(test.dut.at1.send_and_verify('ATD{};'.format(phonenum), 'OK'))
                test.r1.at1.wait_for('RING')
                test.sleep(3)
                test.r1.at1.send_and_verify('ata')
                test.sleep(3)
                test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*\d+,\d+,\d+,\d+,\d+,\d+.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('AT+CHUP', 'OK'))

        if test.dut.dstl_is_umts_supported():
            test.log.info('Test 3G network')
            test.expect(test.dut.dstl_register_to_umts())
            test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*99,99,\d+,\d+,255,255.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMONI', '\^SMONI: 3G.*OK.*'))

        if test.dut.dstl_is_lte_supported():
            test.log.info('Test 4G network')
            test.expect(test.dut.dstl_register_to_lte())
            test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*99,99,255,255,\d+,\d+.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMONI', '\^SMONI: 4G,.*OK.*'))

        if test.dut.dstl_is_nbiot_supported():
            test.log.info('Test NB IOT network')
            test.dut.dstl_register_to_nbiot()
            test.expect(test.dut.at1.send_and_verify('AT+CESQ', '\+CESQ: .*99,99,255,255,\d+,\d+.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SMONI', '\^SMONI: NB-IoT,.*OK.*'))


    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
