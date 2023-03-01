#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0095045.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, \
    dstl_set_minimum_functionality_mode, dstl_set_airplane_mode
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.auxiliary.write_json_result_file import *


class Test(BaseTest):
    """
    Intention:
    This procedure provides the possibility of basic tests for the exec command of AT+GSN.

    Description:
	- check command without and with PIN
    - check for invalid parameters
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        time.sleep(2)

    def run(test):
        test.log.info("TC0095045.001 TpAtGsnBasic")
        test.log.info("1. Test and Execute commands work correctly when module is pin protected")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("2. Test and Execute commands work correctly in airplane mode CFUN:4 - "
                      "pin protected")
        test.expect(dstl_set_airplane_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("3. Test and Execute commands work correctly in airplane mode CFUN:0 - "
                      "pin protected")
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(dstl_set_minimum_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("4. Test and Execute commands work correctly in Pin Ready status")
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(3)
        test.attempt(test.dut.at1.send_and_verify, "at+cpin?", expect="READY", wait_for="READY")
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("5. Test and Execute commands work correctly in airplane mode CFUN:4 - "
                      "pin entered")
        test.expect(dstl_set_airplane_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("6. Test and Execute commands work correctly in airplane mode CFUN:0 - "
                      "pin entered")
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(dstl_set_minimum_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+gsn", "\s\d{15}\s"))
        test.log.info("7. Error returns when executing invalid commands in airplane mode CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+gsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=#", "ERROR"))
        test.log.info("8. Error returns when executing invalid commands in full functionality mode")
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=#", "ERROR"))
        test.log.info("9. Error returns when executing invalid commands in airplane mode CFUN:4")
        test.expect(dstl_set_minimum_functionality_mode(test.dut), critical=True)
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify("at+gsn?", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=11", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=A", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("at+gsn=#", "ERROR"))

    def cleanup(test):
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + 'test_key' + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
