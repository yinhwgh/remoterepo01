#responsible: grzegorz.brzyk@globallogic.com
#location: Wroclaw
#TC0091882.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC0091882.001 - AtCgsmsBasic    test procedure version: 1.4

    INTENTION
    This procedure provides the possibility of basic tests for the test, read and write command of +CGSMS.
    Functional tests are not done here (i.E. verify which service for MO-SMS is used)

    PRECONDITION
    none.
    """

    def setup(test):
        test.time_value = 10
        test.log.step("0. Prepare module")
        test.attempt(test.dut.at1.send_and_verify, "AT", "", retry=5, timeout=test.time_value)
        test.dut.at1.send_and_verify("ATE1", ".*OK.*", timeout=test.time_value)
        dstl_detect(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=test.time_value))
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*", timeout=test.time_value))

    def run(test):
        project = test.dut.project.upper()
        if project == "BOBCAT" or project == "VIPER":
            test_regex = r".*\+CGSMS: \((0-3)|(0,1,2,3)\).*"
            servicelist = ["0", "1", "2", "3"]
            invalidlist = ["-1", "4", "a", "22", "3a", "666", "aaa", "Ez 25:17"]
            tc_steps_without_pin(test)
            tc_steps_with_pin(test, servicelist, invalidlist, test_regex)
        elif project == "SERVAL":
            test_regex = r".*\+CGSMS: \(1,3\).*"
            servicelist = ["1", "3"]
            invalidlist = ["0", "2", "-1", "4", "a", "22", "3a", "666", "aaa", "Ez 25:17"]
            tc_steps_without_pin(test)
            tc_steps_with_pin(test, servicelist, invalidlist, test_regex)
        else:
            test.expect(False, critical=True, msg="Test procedure need be implemented for product.")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS=1", ".*OK.*", timeout=test.time_value))


def tc_steps_without_pin(test):
    test.log.step("Step 1 Check command without and with PIN.")
    test.log.step("Step 1.1 Check command without PIN authentication "
                  "- test, read and write commands should not work without PIN")
    test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "+CPIN: SIM PIN", timeout=test.time_value))
    test.expect(test.dut.at1.send_and_verify("AT+CGSMS=?", ".*CME ERROR: SIM PIN required.*", timeout=test.time_value))
    test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*CME ERROR: SIM PIN required.*", timeout=test.time_value))
    test.expect(test.dut.at1.send_and_verify("AT+CGSMS=1", ".*CME ERROR: SIM PIN required.*", timeout=test.time_value))


def tc_steps_with_pin(test, servicelist, invalidlist, test_regex):
    test.log.step("Step 1.2  Check command with PIN authentication.")
    test.expect(dstl_enter_pin(test.dut))
    test.expect(test.dut.at1.send_and_verify("AT+CGSMS=?", test_regex, timeout=test.time_value))
    for service in servicelist:
        test.log.info("===== Check command with service : {} =====".format(service))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS={}".format(service), ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*CGSMS: {}.*OK.*".format(service), timeout=test.time_value))

    test.log.step("Step 2  Check for invalid parameters.")
    for invalid_param in invalidlist:
        test.log.info("===== Check command with service : {} =====".format(invalid_param))
        test.expect(
            test.dut.at1.send_and_verify("AT+CGSMS={}".format(invalid_param), ".*CME ERROR.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*CGSMS: 3.*OK.*", timeout=test.time_value))


if  "__main__" == __name__:
    unicorn.main()