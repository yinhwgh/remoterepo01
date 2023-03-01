#responsible: matthias.reissner@thalesgroup.com
#location: Berlin
#TC0094652.001

import unicorn
import random
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module


class Test(BaseTest):
    '''
    TC0094652.001 - StabilityTest_cfun_1_1
    Intention: Check stability after several SW restarts with at+cfun=1,1
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        time_sleep = random.randint(5, 60) * 60  # 5 - 60 minutes
        for i in range(10):
            test.expect(restart_module.dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify('ati', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+gsn', 'OK'))   
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.dut.dstl_check_network_status())
            test.expect(test.dut.at1.send_and_verify('at+cimi', '\d+.*OK'))
            test.expect(test.dut.at1.send_and_verify('at^spic', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cnmi?', 'CNMI: \d,\d,\d,\d,\d.*OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpms?', 'CPMS: .*OK'))
            test.expect(test.dut.at1.send_and_verify('at+cfun?', 'CFUN: 1.*OK'))
            test.sleep(time_sleep)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
