#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091861.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    '''
    TC0091861.001 - TpAtCregBasic
    Subscriber :1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):
        test.log.info('1.Test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=?', '.*\\+CREG: \\(0-2\\).*OK.*||.*\\+CREG: \\(0,1,2\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\\+CREG: [012],0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', '.*OK.*'))

        test.log.info('2.Test with pin')
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('AT+CREG=?', '.*\\+CREG: \\(0-2\\).*OK.*||.*\\+CREG: \\(0,1,2\\).*OK.*'))
        test.dut.at1.wait_for('CREG: 1',timeout=30)
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\\+CREG: 1,1.*OK.*'))

        test.log.info('3.Check for invalid parameters')
        test.expect(test.dut.at1.send_and_verify('AT+CREG', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=-0', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=a', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=5', '.*ERROR.*'))

        test.log.info('4.Check functionality  with manual de- and re-registering')
        test.expect(test.dut.at1.send_and_verify('AT+CREG=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('CREG: 0', timeout=30)==False)
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*'))
        test.expect(
            test.dut.at1.wait_for('CREG: 1', timeout=30)==False)

        test.expect(test.dut.at1.send_and_verify('AT+CREG=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', expect='.*CREG: 0.*',wait_for='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='.*CREG: 1.*',wait_for='OK'))

        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', expect='.*CREG: 0.*', wait_for='OK'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='.*CREG: 1,.*', wait_for='OK'))

        test.log.info('5.Check behaviour with AT&W')
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&V', '.*CREG: 2.*'))
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&V', '.*CREG: 0.*'))



    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
