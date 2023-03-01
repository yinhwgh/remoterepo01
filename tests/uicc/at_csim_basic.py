#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0091839.001

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

df_name=""

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
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

    def basic_test(test):
        invalid_parameters = ['+', '/', 'at', 'AT', '*', '.', '']

        test.expect(test.dut.at1.send_and_verify('AT+CSIM=?', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM?', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004023F00"', '.*\+CSIM: 4,"61.*OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000C023F00"', '.*\+CSIM: 4,"9000"\s+OK'))

        test.log.info('Check for invalid parameters.')
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=', ".*CME ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000402"', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004023F007F20"', '.*CME ERROR.*'))
        for value in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify('AT+CSIM={}'.format(value), ".*CME ERROR.*"))


if (__name__ == "__main__"):
    unicorn.main()
