# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0103450.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

import re


class Test(BaseTest):
    """
    TC0103450.001 - DTRFunctionModeConf
    Checking possibilities of configuration dtr line using AT&D.
    """
    # If module supports different value, parameter should be moved to product.cfg
    # The first value should be configured to default value
    DTR_VALUE_STATE=["2", "0", "1"]

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.dut.at1.send_and_verify("AT^SCFG?")
        response = test.dut.at1.last_response
        dtr_format = re.compile('"GPIO/mode/DTR0","(.*)"', re.IGNORECASE)
        find_dsr = re.search(dtr_format, response)
        if find_dsr and find_dsr.group(1) != "std":
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/mode/DTR0\",\"std\""))
            test.expect(test.dut.dstl_restart())
            test.expect(test.dut.dstl_enter_pin())

    def run(test):
        test.log.info(f"Test for all valid DTR value: {test.DTR_VALUE_STATE}")
        for i in range(len(test.DTR_VALUE_STATE)):
            dtr_value = test.DTR_VALUE_STATE[i]
            set_step = f"DTR {dtr_value} - Step 1. Set AT&D to one supported value"
            check_step = f"DTR {dtr_value} - Step 2. Query the current value of AT&D by AT&V"
            test.set_dtr_and_check(dtr_value, set_step, check_step)

            test.log.info(f"DTR {dtr_value} - Step 3. Store AT&D to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            set_step = f"DTR {dtr_value} - Step 4. Set other supported value by AT&D command."
            check_step = "Step 5. Query the current value of AT&D by AT&V."
            other_dtr_value = test.DTR_VALUE_STATE[i-1]
            test.set_dtr_and_check(other_dtr_value, set_step, check_step)

            test.log.info(f"DTR {dtr_value} - Step 6. Restore AT&D value from profile by ATZ")
            test.expect(test.dut.at1.send_and_verify("ATZ", "OK"))

            check_step = f"DTR {dtr_value} - Step 7. Query the current value of AT&D by AT&V."
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(dtr_value)))

            set_step = f"DTR {dtr_value} - Step 8. Set other supported value by AT&D command."
            check_step = f"DTR {dtr_value} - Step 9. Query the current value of AT&D by AT&V."
            test.set_dtr_and_check(other_dtr_value, set_step, check_step)

            test.log.info(f"DTR {dtr_value} - Step 10. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)

            check_step = f"DTR {dtr_value} - Step 11. Query the current value of AT&D by AT&V."
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(dtr_value)))

            set_step = f"DTR {dtr_value} - Step 12. Set other supported value by AT&D command."
            check_step = "Step 13. Query the current value of AT&D by AT&V."
            test.set_dtr_and_check(other_dtr_value, set_step, check_step)

            test.log.info(f"DTR {dtr_value} - Step 14. Store another value of AT&D to user profile by AT&W.")
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            test.log.info(f"DTR {dtr_value} - Step 15. Restart module and enter SIM pin.")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            
            check_step = f"DTR {dtr_value} - Step 16. Query the current value of AT&D by AT&V."
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(other_dtr_value)))

            check_step = f"DTR {dtr_value} - Step 17. Factory value is recovered after executing AT&F"
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
            factory_value = test.DTR_VALUE_STATE[0]
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(factory_value)))

            
            test.log.info(f"DTR {dtr_value} - Step 18. Restart module and enter SIM pin, current value is the one stored in profile")
            test.expect(test.dut.dstl_restart())
            test.attempt(test.dut.dstl_enter_pin, retry=5, sleep=2)
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(other_dtr_value)))
            
    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))
        
    def set_dtr_and_check(test, dtr_value, set_step="", check_step=""):
        if set_step:
            test.log.info(set_step)
        test.expect(test.dut.at1.send_and_verify("AT&D{}".format(dtr_value), "OK"))
        if check_step:
            test.log.info(check_step)
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(dtr_value)))

if "__main__" == __name__:
    unicorn.main()