# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0103449.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

import re


class Test(BaseTest):
    """
    TC0103449.001 - DSRFunctionModeConf
    Checking possibilities of configuration DSR line using AT&S.
    """
    # If module supports different value, parameter should be moved to product.cfg
    # Key-state pair:key is AT&S value, state is DSR line status: True->ON, False->OFF
    # The first key should be configured to default value
    DSR_VALUE_STATE={"0": True, "1": False}

    def setup(test):
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("AT^SCFG?")
        response = test.dut.at1.last_response
        dsr_format = re.compile('"GPIO/mode/DSR0","(.*)"', re.IGNORECASE)
        find_dsr = re.search(dsr_format, response)
        if find_dsr and find_dsr.group(1) != "std":
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/mode/DSR0\",\"std\""))
            test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())

    def run(test):
        test.log.info(f"Test for all valid DSR value: {test.DSR_VALUE_STATE}")
        for i in range(len(test.DSR_VALUE_STATE)):
            set_step = "Step 1. Set AT&S to one supported value"
            check_step = "Step 2. Query the current value of AT&S by AT&V and check state of DSR line"
            dsr_value = list(test.DSR_VALUE_STATE.keys())[i]
            test.set_dsr_and_check(dsr_value, test.DSR_VALUE_STATE[dsr_value], set_step, check_step)

            test.log.info("Step 3. Store AT&S to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            set_step = "Step 4. Set other supported value by AT&S command."
            check_step = "Step 5. Query the current value of AT&S by AT&V and check state of DSR line."
            other_dsr_value = list(test.DSR_VALUE_STATE.keys())[i-1]
            test.set_dsr_and_check(other_dsr_value, test.DSR_VALUE_STATE[other_dsr_value], set_step, check_step)

            test.log.info("Step 6. Restore AT&S value from profile by ATZ")
            test.expect(test.dut.at1.send_and_verify("ATZ", "OK"))

            check_step = "Step 7. Query the current value of AT&S by AT&V and check state of DSR line."
            test.check_dsr_and_state(dsr_value, test.DSR_VALUE_STATE[dsr_value], check_step)

            set_step = "Step 8. Set other supported value by AT&S command."
            check_step = "Step 9. Query the current value of AT&S by AT&V and check state of DSR line."
            test.set_dsr_and_check(other_dsr_value, test.DSR_VALUE_STATE[other_dsr_value], set_step, check_step)

            test.log.info("Step 10. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)

            check_step = "Step 11. Query the current value of AT&S by AT&V and check state of DSR line."
            test.check_dsr_and_state(dsr_value, test.DSR_VALUE_STATE[dsr_value], check_step)

            set_step = "Step 12. Set other supported value by AT&S command."
            check_step = "Step 13. Query the current value of AT&S by AT&V and check state of DSR line."
            test.set_dsr_and_check(other_dsr_value, test.DSR_VALUE_STATE[other_dsr_value], set_step, check_step)

            test.log.info("Step 14. Store another value of AT&S to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            test.log.info("Step 15. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            
            check_step = "Step 16. Query the current value of AT&S by AT&V and check state of DSR line."
            test.check_dsr_and_state(other_dsr_value, test.DSR_VALUE_STATE[other_dsr_value], check_step)

            check_step = "Step 17. Factory value is recovered after executing AT&F"
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
            factory_value = list(test.DSR_VALUE_STATE.keys())[0]
            test.check_dsr_and_state(factory_value, test.DSR_VALUE_STATE[factory_value], check_step)

            
            test.log.info("Step 18. Restart module and enter SIM pin, current value is the one stored in profile")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            test.check_dsr_and_state(other_dsr_value, test.DSR_VALUE_STATE[other_dsr_value])
            
    
    def set_dsr_and_check(test, dsr_value, expect_state, set_step="", check_step=""):
        if set_step:
            test.log.info(set_step)
        test.expect(test.dut.at1.send_and_verify("AT&S{}".format(dsr_value), "OK"))
        test.check_dsr_and_state(dsr_value, expect_state, check_step)
    
    def check_dsr_and_state(test, dsr_value, expect_state, check_step=""):
        if check_step:
            test.log.info(check_step)
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*&S{}.*".format(dsr_value)))
        test.expect(test.dut.at1.connection.dsr == expect_state, msg=f"Expect {expect_state}, actual {test.dut.at1.connection.dsr}")

    def cleanup(test):
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

if "__main__" == __name__:
    unicorn.main()