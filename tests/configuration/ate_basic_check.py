# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091870.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.security import set_sim_waiting_for_pin1
from dstl.auxiliary.write_json_result_file import *


class TpAtEBasic(BaseTest):
    '''
    TC0091870.001 - TpAtEBasic
    This procedure provides basic tests for the test and write command of ATE.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))

    def run(test):
        test.log.info('1.check command without and with PIN &2. check functionality without/with echo')
        test.log.info('1.1 check command without PIN.')
        test.expect(test.dut.at1.send_and_verify('ate0', 'OK'))
        test.expect(test.send_command_and_check_echo('at+cpin?', False, 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('ate1', 'OK'))
        test.expect(test.send_command_and_check_echo('at+cpin?', True, 'SIM PIN'))
        test.sleep(5)

        test.log.info('1.2 check command with PIN.')
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('ate0', 'OK'))
        test.expect(test.send_command_and_check_echo('at+cpin?', False, 'READY'))
        test.expect(test.dut.at1.send_and_verify('ate1', 'OK'))
        test.expect(test.send_command_and_check_echo('at+cpin?', True, 'READY'))

        test.log.info('3. check setting for AT&V output.')
        test.expect(test.dut.at1.send_and_verify('ate0', 'OK'))
        test.expect(test.send_command_and_check_echo('at&v', False, 'E0'))
        test.expect(test.dut.at1.send_and_verify('ate1', 'OK'))
        test.expect(test.send_command_and_check_echo('at&v', True, 'E1'))

        test.log.info('4. check setting for AT&F.')
        test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT&V', 'E1'))

        test.log.info('5. check for invalid parameters.')
        test.expect(test.dut.at1.send_and_verify('ATE4', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATEFG', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATE=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATE=256', 'ERROR'))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

    def send_command_and_check_echo(test, command, echo, expect_response='OK'):
        test.expect(test.dut.at1.send_and_verify(command, expect_response))
        if echo == True:
            if command in test.dut.at1.last_response:
                test.log.info('Echo message show, correct')
                return True
            else:
                test.log.error('Echo message should show but not')
                return False
        else:
            if command in test.dut.at1.last_response:
                test.log.error('Echo message should not show')
                return False
            else:
                test.log.info('Echo message not show, correct')
                return True


if "__main__" == __name__:
    unicorn.main()
