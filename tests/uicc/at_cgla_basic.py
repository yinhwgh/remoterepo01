#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0092858.001

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network
from dstl.usim import get_df_name
from dstl.configuration import functionality_modes
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.auxiliary.write_json_result_file import *
df_name=""

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(5)
        global df_name
        df_name = test.dut.dstl_get_df_name('01')
        return


    def run(test):
        test.log.info('***Test start***')
        test.log.info('1.Check test and write command without PIN.')
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.basic_test()
        test.log.info('2.Check test and write command with PIN.')
        test.expect(test.dut.dstl_enter_pin())
        test.basic_test()
        test.log.info('3.Check test and write command in airplane mode.')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.basic_test()
        test.log.info('***Test end***')

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

    def basic_test(test):
        invalid_parameters = ['+', '/', 'at', 'AT', '*', '.', '']
        if test.dut.project == 'VIPER':
            expect_response='.*\+CGLA: \d,"61.*OK' #IPIS100327576
        else:
            expect_response = '.*\+CGLA: 4,"61.*OK'
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=?', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA?', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHO="{}"'.format(df_name), ".*CCHO: .*OK.*"))
        session_id_1 = re.search(r'CCHO: (\d)', test.dut.at1.last_response).group(1)
        test.expect(test.dut.at1.send_and_verify('AT+CCHO="{}"'.format(df_name), ".*CCHO: .*OK.*"))
        session_id_2 = re.search(r'CCHO: (\d)', test.dut.at1.last_response).group(1)
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"00A40004023F00"'.format(session_id_1), expect_response))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_1,session_id_1), expect_response))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGLA={},14,"00A40004023F00"'.format(session_id_2), expect_response))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_2, session_id_2),
                                                 expect_response))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=' + session_id_1, "OK"))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGLA={},14,"00A40004023F00"'.format(session_id_1), '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_1, session_id_1),
                                                 '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_1, session_id_2),
                                                 '.*CME ERROR.*'))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGLA={},14,"00A40004023F00"'.format(session_id_2), expect_response))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_2, session_id_1),
                                                 expect_response))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"0{}A40004023F00"'.format(session_id_2, session_id_2),
                                                 expect_response))
        test.log.info('Check for invalid parameters.')
        test.expect(test.dut.at1.send_and_verify('AT+CGLA=', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={}'.format(session_id_2), ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14'.format(session_id_2), ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGLA={},14,"A0A4000402"'.format(session_id_2), ".*CME ERROR.*"))
        for value in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify('AT+CGLA={}'.format(value), ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CCHC=' + session_id_2, "OK"))
        return True



if (__name__ == "__main__"):
    unicorn.main()
