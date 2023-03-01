#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0091838.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        return


    def run(test):
        test.log.info('***Test start***')
        test.log.info('1.Check test and write command without PIN.')
        test.dut.dstl_restart()
        time.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.basic_test()
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28423,0,0,09', '.*\+CRSM: 105,130,"".*OK'))
        test.log.info('2.Check test and write command with PIN.')
        test.expect(test.dut.dstl_enter_pin())
        test.basic_test()
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28423,0,0,09', '.*\+CRSM: 144,0,".*OK'))
        test.log.info('3.Check test and write command in airplane mode.')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.basic_test()
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28423,0,0,09', '.*\+CRSM: 144,0,".*OK'))
        test.log.info('***Test end***')

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut))

    def basic_test(test):
        invalid_parameters = ['+', '/', 'at', 'AT', '*', '.', '']
        test.expect(test.dut.at1.send_and_verify('at+crsm=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm?', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=242', '.*\+CRSM: 144,0,"62.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,12258,0,0,10', '.*\+CRSM: 144,0,".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,12037,0,0,1', '.*\+CRSM: 144,0,".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28421,0,0,1', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28486,0,0,17', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28589,0,0,3', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28590,0,0,1', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28599,0,0,3', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,12258,0,0,10', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,12037,0,0,1', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28421,0,0,1', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28486,0,0,17', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28589,0,0,3', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28590,0,0,1', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28599,0,0,3', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28472,0,0,2', '.*\+CRSM:.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=214,28423,0,0,09,"081122334455667788"', '.*\+CRSM: 105,130,"".*OK'))
        test.expect(
            test.dut.at1.send_and_verify('at+crsm=220,28474,01,04,10,"00112233445566778899"', '.*\+CRSM: \d+,\d+,"".*OK'))

        test.log.info('Check for invalid parameters.')
        for i in range(1,300):
            if i==242:
                continue
            else:
                test.expect(test.dut.at1.send_and_verify('at+crsm='+str(i), '.*CME ERROR.*'))

        for value in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify('at+crsm={}'.format(value), ".*CME ERROR.*"))

        return True





if (__name__ == "__main__"):
    unicorn.main()
