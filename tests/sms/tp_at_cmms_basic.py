#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0091829.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """TC0091829.001   TpAtCmmsBasic
    This procedure provides the possibility of basic tests for the exec command of AT+Cmms.
    Description:
    1. check command without and with PIN
    2. check all parameters and also with invalid values a functional test is not done here
    """

    def setup(test):
        test.log.h2("Executing script for test case TC0091829.001 TpAtCmmsBasic")
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
        if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
            test.log.info("=== SIM PIN code locked - checking if command is PIN protected could be realized ===")
        else:
            test.log.info("SIM PIN entered - restart is needed")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
            if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
                test.log.info("=== SIM PIN code locked - checking if command is PIN protected could be realized ===")
            else:
                test.log.info("=== SIM PIN code unlocked - must be locked for checking if command is PIN protected ===")
                test.expect(dstl_lock_sim(test.dut))
                test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("Step 1. check command without and with PIN")
        test.log.info("===== Tests without PIN authentication =====")
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM PIN.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("AT+CMMS=?", r".*\+CMS ERROR: SIM PIN required.*", timeout=60))
        test.expect(test.dut.at1.send_and_verify("AT+CMMS?", r".*\+CMS ERROR: SIM PIN required.*", timeout=60))
        test.expect(test.dut.at1.send_and_verify("AT+CMMS=1", r".*\+CMS ERROR: SIM PIN required.*", timeout=60))

        test.log.info("===== Tests with PIN authentication =====")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)  # Timeout for SIM card initialization
        test.expect(test.dut.at1.send_and_verify("AT+CMMS=?", r".*\+CMMS: \(0-2\).*OK.*", timeout=60))
        for mode in [0, 1, 2]:
            test.expect(test.dut.at1.send_and_verify("AT+CMMS={}".format(mode), ".*OK.*", timeout=60))
            test.expect(test.dut.at1.send_and_verify("AT+CMMS?", r".*\+CMMS: {}.*OK.*".format(mode), timeout=60))
            test.sleep(10)  # According to ATC:
                            # After read command usage a delay of 5-10 seconds is required before issuing the write
                            # command, otherwise the "+CMS ERROR: 500" may appear

        test.log.step("Step 2. check all parameters and also with invalid values a functional test is not done here")
        test.log.info("===== Tests invalid values and CMMS command syntax =====")
        invalid_values = ["", "=", "=-1", "=3", "=10"]
        for i in invalid_values:
            test.expect(test.dut.at1.send_and_verify("AT+CMMS{}".format(i), ".*CMS ERROR.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CMMS=0", ".*OK.*", timeout=60))
        test.expect(test.dut.at1.send_and_verify("AT+CMMS?", r".*\+CMMS: 0.*OK.*", timeout=60))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()