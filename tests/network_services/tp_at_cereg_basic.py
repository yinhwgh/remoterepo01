#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0093915.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_lte
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    TC0093915.001 - TpAtCeregBasic    #test procedure version: 0.7

    INTENTION
    This procedure provides basic tests for the test and write command of +CEREG.
    Functional tests are not done here.

    PRECONDITION
    none.
    """

    def setup(test):
        test.log.step("Prepare module")
        dstl_detect(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*"))
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        project = test.dut.project.upper()
        if project == "SERVAL":
            n_value_list = ["0", "1", "2", "4"]
            invalid_n_list = ["-1", "3", "5", "9", "a", "aaa", "Ez25:17"]
            test_regex = r".*\+CEREG: \((0-2),4|(0,1,2,4)\).*"
            stat = "([0-5])"
            act = "([7-9])"
            test.execute_steps_without_pin()
            test.execute_steps_with_pin(n_value_list, invalid_n_list, test_regex, stat, act)
        else:
            n_value_list = ["0", "1", "2"]
            invalid_n_list = ["-1", "3", "9", "a", "aaa", "Ez25:17"]
            test_regex = r".*\+CEREG: \((0-2)|(0,1,2)\).*"
            stat = "([0-5])"
            act = "([6-9])"
            test.execute_steps_without_pin()
            test.execute_steps_with_pin(n_value_list, invalid_n_list, test_regex, stat, act)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def execute_steps_without_pin(test):
        test.log.step("Step 1 Check command without and with PIN")
        test.log.step("- Check command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CEREG=?", ".*CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG", ".*CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG=1", ".*CME ERROR: SIM PIN required.*"))

    def execute_steps_with_pin(test, n_value_list, invalid_n_list, test_regex, stat, act):
        test.log.step("- Check command with PIN")
        test.expect(dstl_register_to_lte(test.dut))
        test.log.info("===== Check test command response =====")
        test.expect(test.dut.at1.send_and_verify("AT+CEREG=?", "{}[\r\n]{{2}}.*OK.*".format(test_regex)))
        test.log.info("===== Check read command response =====")
        test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*\+CEREG: 0,([0-5])[\r\n]{2}.*OK.*"))
        test.log.info("===== Check exec command response =====")
        test.expect(test.dut.at1.send_and_verify("AT+CEREG", ".*OK.*"))
        test.log.info("===== Check write command response =====")
        test.expect(test.dut.at1.send_and_verify("AT+CEREG=1", ".*OK.*"))

        test.log.step("Step 2 Check all parameters and also with invalid values.")
        test.log.info("===== Check all parameters - valid values: {} =====".format(n_value_list))
        for n_value in n_value_list:
            test.set_valid_parameter(n_value, stat, act)
        test.log.info("===== Execute AT&F and check CEREG -> expected: <n>=0 =====")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG?", r".*\+CEREG: 0,.*OK.*"))

        test.log.info("===== Check invalid values: {} =====".format(invalid_n_list))
        for invalid_n in invalid_n_list:
            test.set_invalid_parameter(invalid_n)

        test.log.step("Step 3 Check functionality with manual de-/reregisteration of the module.")
        for n_value in n_value_list:
            test.set_valid_parameter(n_value, stat, act)
            test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
            test.check_parameter_deregistered(n_value)
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*COPS: 2.*"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*"))
            test.check_parameter_registered(n_value, act)

    def set_valid_parameter(test, n_value, stat, act):
        test.log.info("===== Check valid parameter <n> value: {} =====".format(n_value))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG={}".format(n_value), ".*OK.*"))
        if n_value == "0":
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", r".*\+CEREG: {},{}[\r\n]{{2}}.*OK.*".format(n_value, stat)))
        if n_value == "1":
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", r".*\+CEREG: {},{}[\r\n]{{2}}.*OK.*".format(n_value, stat)))

        if n_value == "2":
            n2_regex_1 = r".*\+CEREG: {},{}(\s+){{2}}.*OK.*".format(n_value, stat)
            n2_regex_2 = r".*\+CEREG: {},{},\".*\",\".*\",{}(\s+){{2}}.*OK.*".format(n_value, stat, act)
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*CEREG:.*"))
            test.expect(re.search(n2_regex_1, test.dut.at1.last_response) or re.search(n2_regex_2, test.dut.at1.last_response))

        if n_value == "4":
            n4_regex_1 = r".*\+CEREG: {},{}(\s+){{2}}.*OK.*".format(n_value, stat)
            n4_regex_2 = r".*\+CEREG: {},{},\".*\",\".*\",{}(\s+){{2}}.*OK.*".format(n_value, stat, act)
            n4_regex_3 = r".*\+CEREG: {},{},\".*\",\".*\",{},,,\".*\",\".*\",\".*\"(\s+){{2}}.*OK.*".format(n_value, stat, act)
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*CEREG:.*"))
            test.expect(re.search(n4_regex_3, test.dut.at1.last_response) or re.search(n4_regex_2, test.dut.at1.last_response)
                        or re.search(n4_regex_1, test.dut.at1.last_response))

    def set_invalid_parameter(test, invalid_n):
        test.log.info("===== Check invalid parameter <n> value: {} =====".format(invalid_n))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG={}".format(invalid_n), ".*CME ERROR:.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CEREG?", r".*\+CEREG: 0,.*OK.*"))

    def check_no_urc(test):
        test.wait(30)
        test.dut.at1.read(append=True)
        if re.search(".*CEREG.*", test.dut.at1.last_response):
            test.log.error(f"URC .*CEREG.* occurred, Test Failed")
            return False
        else:
            test.log.info(f"URC .*CEREG.* NOT occurred, Test Passed")
            return True

    def check_parameter_deregistered(test, n_value):
        if n_value == "0":
            test.log.info("For CEREG <n> = 0 URC should not occur.")
            test.expect(test.check_no_urc())
        else:
            test.expect(dstl_check_urc(test.dut, r".*\+CEREG: 0.*"))

    def check_parameter_registered(test, n_value, act):
        check_regex_1 = r"\+CEREG: 1"
        if n_value == "0":
            test.log.info("For CEREG <n> = 0 URC should not occur.")
            test.expect(test.check_no_urc())
        elif n_value == "2":
            check_n2_regex_2 = r"\+CEREG: 1,\".*\",\".*\",{}".format(act)
            if test.expect(dstl_check_urc(test.dut, check_regex_1)):
                if re.search(check_n2_regex_2, test.dut.at1.last_response):
                    test.log.info("regex: {} found".format(check_n2_regex_2))
                else:
                    test.log.info("regex: {} found".format(check_regex_1))
            else:
                test.expect(False, msg="regex {} NOT found".format(check_regex_1))
        elif n_value == "4":
            check_n4_regex_2 = r"\+CEREG: 1,\".*\",\".*\",{}".format(act)
            check_n4_regex_3 = r"\+CEREG: 1,\".*\",\".*\",{},,,\".*\",\".*\",\".*\"".format(act)
            if test.expect(dstl_check_urc(test.dut, check_regex_1)):
                if re.search(check_n4_regex_3, test.dut.at1.last_response):
                    test.log.info("regex: {} found".format(check_n4_regex_3))
                elif re.search(check_n4_regex_2, test.dut.at1.last_response):
                    test.log.info("regex: {} found".format(check_n4_regex_2))
                else:
                    test.log.info("regex: {} found".format(check_regex_1))
            else:
                test.expect(False, msg="regex {} NOT found".format(check_regex_1))
        else:
            test.expect(test.dut.dstl_check_urc(check_regex_1))


if "__main__" == __name__:
    unicorn.main()