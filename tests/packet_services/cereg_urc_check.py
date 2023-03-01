# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0096309.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.write_json_result_file import *


class Test(BaseTest):
    '''
    TC0096309.001 - Cereg_URC_check
    Subscriber :1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(2)
        test.check_para = []

    def run(test):
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=?'))
        if 'CEREG: (0-2,4)' in test.dut.at1.last_response:
            test.check_para = [0, 1, 2, 4]

        elif 'CEREG: (0-2)' in test.dut.at1.last_response:
            test.check_para = [0, 1, 2]

        elif 'CEREG: (0-5)' in test.dut.at1.last_response:
            test.check_para = [0, 1, 2, 3, 4, 5]

        for i in test.check_para:
            test.log.info(f'Start test parameter <n> = {i}')
            test.check_n(i)

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

    def check_n(test, n):
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_enter_pin()
        test.sleep(2)

        test.expect(test.dut.at1.send_and_verify(f'AT+CEREG={n}'))
        if n == 0:
            test.log.info('Check URC will not pop up when n=0.')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG:.*', timeout=60, append=True) == False)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '\\+CEREG: 0,1'))

        elif n == 1:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.log.info('Check URC format +CEREG:<stat> will be prompted after register successfully.')
            test.expect(test.dut.at1.wait_for('.*\\+CEREG: 1', timeout=60, append=True))
        elif n == 2:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.log.info(
                'Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>]] will be prompted after register successfully.')
            test.expect(
                test.dut.at1.wait_for('.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*',
                                      timeout=60, append=True))
        elif n == 3:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.log.info(
                'Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,<cause_type>,<reject_cause>]] will be prompted after register successfully.')
            test.expect(test.dut.at1.wait_for('.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*',
                                              timeout=60, append=True))
        elif n == 4:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.log.info(
                '12.Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,,[,[<Active-Time>],[<Periodic-TAU>]]]] will be prompted after register successfully.')
            test.expect(
                test.dut.at1.wait_for(
                    '.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,\"?[0-9]{1}\"?,,,\"?[0-1]{8}\"?,\"?[0-1]{8}\"?.*',
                    timeout=60, append=True))

        elif n == 5:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.log.info(
                '15.Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,[<cause_type>],[<reject_cause>][,[<Active-Time>],[<Periodic-TAU>]]]] will be prompted after register successfully.')
            test.expect(
                test.dut.at1.wait_for(
                    '.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,\"?[0-9]{1}\"?,,,\"?[0-1]{8}\"?,\"?[0-1]{8}\"?.*',
                    timeout=60))


if "__main__" == __name__:
    unicorn.main()
