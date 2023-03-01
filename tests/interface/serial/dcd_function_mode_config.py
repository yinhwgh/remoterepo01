# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0103451.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

import re


class Test(BaseTest):
    """
    TC0103451.001 - DCDFunctionModeConf
    Checking possibilities of configuration DCD line using AT&C.
    """
    # If module supports different value, parameter should be moved to product.cfg
    # Key-state pair:key is AT&C value, state is dcd line status: True->ON, False->OFF
    # The first key should be configured to default value
    DCD_VALUE_STATE={"1": False, "0": True, "2": False}

    def setup(test):
        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("AT^SCFG?")
        response = test.dut.at1.last_response
        dcd_format = re.compile('"GPIO/mode/DCD0","(.*)"', re.IGNORECASE)
        find_dsr = re.search(dcd_format, response)
        if find_dsr and find_dsr.group(1) != "std":
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/mode/DCD0\",\"std\""))
            test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.info(f"Test for all valid DCD value: {test.DCD_VALUE_STATE.keys()}")
        for i in range(len(test.DCD_VALUE_STATE)):
            dcd_value = list(test.DCD_VALUE_STATE.keys())[i]
            set_step = f"DCD {dcd_value} - Step 1. Set AT&C to one supported value"
            check_step = f"DCD {dcd_value} - Step 2. Query the current value of AT&C by AT&V and check state of dcd line: {test.DCD_VALUE_STATE[dcd_value]}"
            test.set_dcd_and_check(dcd_value, test.DCD_VALUE_STATE[dcd_value], set_step, check_step)

            test.log.info(f"DCD {dcd_value} - Step 3. Store AT&C to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            set_step = f"DCD {dcd_value} - Step 4. Set other supported value by AT&C command."
            check_step = f"DCD {dcd_value} - Step 5. Query the current value of AT&C by AT&V and check state of dcd line."
            other_dcd_index = i - 1
            other_dcd_value = list(test.DCD_VALUE_STATE.keys())[other_dcd_index]
            test.set_dcd_and_check(other_dcd_value, test.DCD_VALUE_STATE[other_dcd_value], set_step, check_step)

            test.log.info(f"DCD {dcd_value} - Step 6. Restore AT&C value from profile by ATZ")
            test.expect(test.dut.at1.send_and_verify("ATZ", "OK"))

            check_step = f"DCD {dcd_value} - Step 7. Query the current value of AT&C by AT&V and check state of dcd line."
            test.check_dcd_and_state(dcd_value, test.DCD_VALUE_STATE[dcd_value], check_step)

            set_step = f"DCD {dcd_value} - Step 8. Set other supported value by AT&C command."
            check_step = f"DCD {dcd_value} - Step 9. Query the current value of AT&C by AT&V and check state of dcd line."
            test.set_dcd_and_check(other_dcd_value, test.DCD_VALUE_STATE[other_dcd_value], set_step, check_step)

            test.log.info(f"DCD {dcd_value} - Step 10. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)

            check_step = f"DCD {dcd_value} - Step 11. Query the current value of AT&C by AT&V and check state of dcd line."
            test.check_dcd_and_state(dcd_value, test.DCD_VALUE_STATE[dcd_value], check_step)

            set_step = f"DCD {dcd_value} - Step 12. Set other supported value by AT&C command."
            check_step = "Step 13. Query the current value of AT&C by AT&V and check state of dcd line."
            test.set_dcd_and_check(other_dcd_value, test.DCD_VALUE_STATE[other_dcd_value], set_step, check_step)

            test.log.info(f"DCD {dcd_value} - Step 14. Store another value of AT&C to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            test.log.info(f"DCD {dcd_value} - Step 15. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            
            check_step = f"DCD {dcd_value} - Step 16. Query the current value of AT&C by AT&V and check state of dcd line."
            test.check_dcd_and_state(other_dcd_value, test.DCD_VALUE_STATE[other_dcd_value], check_step)

            check_step = f"DCD {dcd_value} - Step 17. Factory value is recovered after executing AT&F"
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
            factory_value = list(test.DCD_VALUE_STATE.keys())[0]
            test.check_dcd_and_state(factory_value, test.DCD_VALUE_STATE[factory_value], check_step)

            
            test.log.info(f"DCD {dcd_value} - Step 18. Restart module and enter SIM pin, current value is the one stored in profile")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            test.check_dcd_and_state(other_dcd_value, test.DCD_VALUE_STATE[other_dcd_value])
            
    
    def set_dcd_and_check(test, dcd_value, expect_state, set_step="", check_step=""):
        if set_step:
            test.log.info(set_step)
        test.expect(test.dut.at1.send_and_verify("AT&C{}".format(dcd_value), "OK"))
        test.check_dcd_and_state(dcd_value, expect_state, check_step)
    
    def check_dcd_and_state(test, dcd_value, expect_state, check_step=""):
        if check_step:
            test.log.info(check_step)
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*&C{}.*".format(dcd_value)))
        test.expect(test.dut.at1.connection.cd == expect_state, msg=f"Expect {expect_state}, actual {test.dut.at1.connection.cd}")

    def cleanup(test):
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

if "__main__" == __name__:
    unicorn.main()