#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091796.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import functionality_modes
from dstl.auxiliary.write_json_result_file import *


class TpAtCgsnBasic(BaseTest):
    """
    TC0091796.001 - TpAtCgsnBasic
    This procedure provides the possibility of basic tests for the exec command of AT+CGSN.
    Debugged: Serval
    """

    def setup(test):
        # Restart to make pin locked
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        time.sleep(2)

    def run(test):
        test.log.info("1. Test and Execute commands work correctly when module is pin protected")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("2. Test and Execute commands work correctly in airplane mode CFUN:4 - pin protected")
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("3. Test and Execute commands work correctly in airplane mode CFUN:0 - pin protected")
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("4. Test and Execute commands work correctly in Pin Ready status")
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.sleep(5)
        test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=1)
        test.attempt(test.dut.at1.send_and_verify, "at+cpin?", expect="READY", wait_for="READY", retry=5, sleep=1)
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("5. Test and Execute commands work correctly in airplane mode CFUN:4 - pin entered")
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("6. Test and Execute commands work correctly in airplane mode CFUN:0 - pin entered")
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn", "\s\d{15}\s"))
        test.log.info("7. Error returns when executing invalid commands in airplane mode CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+cgsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=#", "ERROR"))
        test.log.info("8. Error returns when executing invalid commands in full functionality mode")
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=#", "ERROR"))
        test.log.info("9. Error returns when executing invalid commands in airplane mode CFUN:4")
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.expect(test.dut.at1.send_and_verify("at+cgsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+cgsn=#", "ERROR"))

    def cleanup(test):
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
