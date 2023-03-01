#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091795.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.identification import get_identification
from dstl.auxiliary.write_json_result_file import *

class TpAtCgmrBasic(BaseTest):
    """
    TC0091795.001 - TpAtCgmrBasic
    This procedure provides the possibility of basic tests with AT+GMR or AT+CGMR
    Debugged: Serval
    """

    def setup(test):
        # Restart to make pin locked
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")


    def run(test):
        # Regular expression of firmware version, e.g. ".*REVISION\s+\d{2}[.]\d{3}.*"
        revision_format = test.dut.dstl_get_defined_sw_revision()
        # 1. Valid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmr=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr", revision_format))
        # 2. Invalid parameters without pin
        test.expect(test.dut.at1.send_and_verify("at+cgmr?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr0", ".*ERROR.*"))
        # 3. Valid parameters with pin
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+cgmr=?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr", revision_format))
        # 4. Invalid parameters with pin
        test.expect(test.dut.at1.send_and_verify("at+cgmr?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr=1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("at+cgmr0", ".*ERROR.*"))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
