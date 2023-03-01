#responsible: jun.chen@thalesgroup.com
#location: Beijing
#SRV03-4738

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary.write_json_result_file import *
from dstl.packet_domain import cereg_test_response

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.sleep(2)

    def run(test):
        test.cereg_read_response_n = test.dut.dstl_get_cereg_expected_read_response_n()

        for i in test.cereg_read_response_n:
            test.log.info(f'Start test parameter <n> = {i}')
            test.check_n(i)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CPSMS=2'))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

    def check_n(test, n):
        timeout_value = 10
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_enter_pin()
        test.sleep(2)

        test.expect(test.dut.at1.send_and_verify(f'AT+CEREG={n}'))
        if n == 0:
            test.log.info('Check URC will not pop up when n=0.')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG:.*', timeout=timeout_value, append=True) == False)
            test.expect(test.dut.at1.send_and_verify('AT+CEREG?', '\\+CEREG: 0,1'))

        elif n == 1:
            test.log.info('Check URC format +CEREG:<stat> will be prompted after register successfully.')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG: 1', timeout=timeout_value, append=True))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,[79].*OK.*"))

        elif n == 2:
            test.log.info('Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>]] will be prompted after register successfully.')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*',timeout=timeout_value, append=True))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,[79].*OK.*"))

        elif n == 3:
            test.log.info(
                'Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,<cause_type>,<reject_cause>]] will be prompted after register successfully.')
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*',timeout=timeout_value, append=True))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,[79].*OK.*"))

        elif n == 4:
            test.log.info(
                '12.Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,,[,[<Active-Time>],[<Periodic-TAU>]]]] will be prompted after register successfully.')
            test.expect(test.dut.at1.send_and_verify('AT+CPSMS=1'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for(
                '.*\\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,\"?[0-9]{1}\"?,,,\"?[01]{8}\"?,\"?[01]{8}\"?.*',timeout=timeout_value, append=True))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,[79].*OK.*"))

        elif n == 5:
            test.log.info(
                '15.Check URC format +CEREG:<stat>[,[<tac>],[<ci>],[<AcT>][,[<cause_type>],[<reject_cause>][,[<Active-Time>],[<Periodic-TAU>]]]] will be prompted after register successfully.')
            test.expect(test.dut.at1.send_and_verify('AT+CPSMS=1'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2'))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0'))
            test.expect(test.dut.at1.wait_for(
                '.*\+CEREG: 1,"?[0-9,a-f,A-F]{4}"?,"?[0-9,a-f,A-F]{8}"?,"?[0-9]{1}"?,,,"?[0-1]{8}"?,"?[0-1]{8}"?.*',timeout=timeout_value, append=True))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,[79].*OK.*"))

if "__main__" == __name__:
    unicorn.main()
