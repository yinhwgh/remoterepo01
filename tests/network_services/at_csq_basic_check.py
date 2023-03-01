#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091862.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_voice_call_supported
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    '''
    TC0091862.001 - TpAtCsqBasic
    Subscriber :2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):

        test.log.info('1.Test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))
        if test.dut.platform=='QCT':
            test.expect(test.dut.at1.send_and_verify('AT+CSQ=?', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'ERROR'))
        else:
            test.expect(test.dut.at1.send_and_verify('AT+CSQ=?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'OK'))

        test.log.info('2.Test with pin')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'CSQ: \d{1,2},\d{1,2}.*OK.*'))

        test.log.info('3.Test invalid parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=99', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CSQ=11,11', 'ERROR'))

        if test.dut.dstl_is_voice_call_supported():
            test.r1.dstl_register_to_network()
            phonenum = test.r1.sim.nat_voice_nr
            test.dut.at1.send_and_verify('at^sm20=0', 'OK|ERROR')
            test.expect(test.dut.at1.send_and_verify('ATD{};'.format(phonenum), 'OK'))
            test.r1.at1.wait_for('RING')
            test.sleep(3)
            test.r1.at1.send_and_verify('ata')
            test.sleep(3)
            test.expect(test.dut.at1.send_and_verify('AT+CLCC', '.*CLCC: 1,0,0,0,0'))
            test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'CSQ: \d{1,2},\d{1,2}.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CHUP', 'OK'))


    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
