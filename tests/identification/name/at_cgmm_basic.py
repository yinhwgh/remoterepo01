#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091794.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary.write_json_result_file import *

class TpAtCgmmBasic(BaseTest):
    """
     TC0091794.001 -  	TpAtCgmmBasic
     This procedure provides the possibility of basic tests for the exec command of AT+Cgmm.
     Debugged: Serval
    """
    def setup(test):
        # Restart to make pin locked
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")

    def run(test):
        # Regular expression of module type, e.g. "\s+EXS82-W\s+OK\s+"
        module_type = f"{test.dut.product}-{test.dut.variant}\s+OK\s+"
        expected_module_type = module_type
        # 1. Valid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmm=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm", expected_module_type))
        # 2. Invalid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmm?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm0", ".*ERROR.*"))
        # 3. Valid parameters with pin
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+cgmm=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm", expected_module_type))
        # 4. Invalid parameters with pin
        test.expect(test.dut.at1.send_and_verify("at+cgmm?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmm0", ".*ERROR.*"))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
