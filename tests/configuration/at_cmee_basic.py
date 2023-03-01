#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091677.002 - TpAtCmeeBasic

import unicorn
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary.write_json_result_file import *

class TpAtCmeeBasic(BaseTest):

    def setup(test):

        test.log.info("*******************************************************************")
        test.log.info("Setup_1: Initiate module and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))

        test.log.info("*******************************************************************")
        test.log.info("Setup_2. Enable SIM PIN lock before testing")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.sleep(2)


    def run(test):

        simPINLOCKstatus = ["before","after"]

        for simPINLOCK in simPINLOCKstatus:
            test.log.info("*******************************************************************")
            test.log.info("Run_Test_1: test: Check CMEE Test and Read command {} input PIN ".format(simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=?', r'.*\+CMEE: \(0,1,2\)[\s\S]*OK.*'))
            if test.dut.platform == "QCT":
                test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: {}[\S\s]*OK.*'.format(2)))
            else:
                test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: {}[\S\s]*OK.*'.format(0)))

            test.log.info("*******************************************************************")
            test.log.info("Run_Test_2: test: Check CMEE Write and Execute command {} input PIN ".format(simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: 1[\s\S]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: 2[\S\s]*OK.*'))


            test.log.info("*******************************************************************")
            test.log.info("Run_Test_3: Set incorret value  of AT+CMEE {} input PIN ".format(simPINLOCK))
            test.log.info("*******************************************************************")
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=-1', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=A', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=b', r'.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=/n', r'.*ERROR.*'))


            if simPINLOCK == "without":
                test.expect(test.dut.dstl_enter_pin())
                test.log.info("Wait a while after input PIN code")

        test.log.info("*******************************************************************")
        test.log.info("Run_Test_4. Check functionalality with some error codes")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=0', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: 0[\S\s]*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: 1[\S\s]*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=-1', '\+CME ERROR: \d+'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=2', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', '.*\+CMEE: 2[\s\S]*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=-1', '\+CME ERROR: \w+'))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if (__name__ == "__main__"):
    unicorn.main()
