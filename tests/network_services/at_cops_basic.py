# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091860.001

import unicorn

from core.basetest import BaseTest

from dstl.status_control import extended_indicator_control
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import check_urc
from dstl.security import lock_unlock_sim
from dstl.network_service import network_access_type
from dstl.network_service import operator_selector
from dstl.network_service import customization_cops_properties

import re


class Test(BaseTest):
    '''
    TC0091860.001 - TpAtCopsBasic
    This procedure provides the possibility of basic tests for the test and write command of +COPS.
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.log.info("Wait for enough time for SIM loading.")
        test.sleep(10)

    def run(test):
        # Response preparation
        test_res_after_pin = test.dut.dstl_customized_cops_test_response()
        read_res_after_pin = "\+COPS: \d,\d,\".+\",\d"
        cops_pin_protected = test.dut.dstl_customized_cops_pin_protected()
        ok_or_error = "\s+(OK|ERROR)"
        test_time_out = 120

        test.log.step("1. Test commands before pin")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        commands_to_check = ['AT+COPS=?', 'AT+COPS?', 'AT+COPS=', 'AT+COPS=2', 'AT+COPS=0']
        for command in commands_to_check:
            if command in cops_pin_protected:
                res_before_pin = "ERROR" if cops_pin_protected[command] else "OK"
            else:
                res_before_pin = "OK"
                test.log.error(
                    f"{command} is pin protected or not is not configured in dstl_customized_cops_pin_protected.")
            if command == "AT+COPS=?" and res_before_pin == "OK":
                res_before_pin = "\+COPS: [0-4]"
            test.expect(test.dut.at1.send_and_verify(command, res_before_pin, wait_for=ok_or_error,
                                                     timeout=test_time_out))

        test.log.step("2. Test commands after pin")
        test.dut.dstl_set_network_max_modes()
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.at1.send_and_verify, "AT+COPS?", read_res_after_pin,
                     wait_for=ok_or_error, retry=10, sleep=5)
        test.log.info("Wait until module is idle then searching operator info.")
        test.attempt(test.dut.at1.send_and_verify, "AT^SMONI", "NOCONN",
                     wait_for=ok_or_error, retry=5, sleep=30)
        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=?", test_res_after_pin,
                     wait_for=ok_or_error, timeout=test_time_out, retry=3, sleep=5)
        cops_response = test.dut.at1.last_response
        operator_name_long, operator_name_short, operator_name_num, current_net_type = test._read_operator_info(
            cops_response, '2')

        test.log.step("3. Test automatically register with format change")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,1", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                 f"\+COPS: 0,1,\"{operator_name_short}\",{current_net_type}",
                                                 wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,2", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                 f"\+COPS: 0,2,\"{operator_name_num}\",{current_net_type}",
                                                 wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,0", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                 f"\+COPS: 0,0,\"{operator_name_long}\",{current_net_type}",
                                                 wait_for=ok_or_error))

        test.log.step("4. Test deregister and re-register automatically")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                 f"\+COPS: 0,0,\"{operator_name_long}\",{current_net_type}",
                                                 wait_for=ok_or_error))
        test.log.step("4.1. When module is deresigstered, no operator should be in status 2.")
        test.log.info("Added for Viper IPIS100324011.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error))
        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=?", test_res_after_pin,
                     wait_for=ok_or_error, timeout=test_time_out, retry=3, sleep=5)
        cops_response = test.dut.at1.last_response
        op_name_long, op_name_short, op_name_num, net_type = test._read_operator_info(cops_response,
                                                                                     '2')
        test.expect(op_name_long == "none",
                    msg="No operator should be in status 2 when module is deregistered.")

        test.log.step("5. Test another valid network type can be manually registered")
        valid_operator_info = test.dut.dstl_get_available_operator_rats(cops_response, format_number="1",
                                                                        for_current_provider=True)
        if valid_operator_info:
            operator_name_num, net_type = valid_operator_info[0].split(',')
            test.expect(
                test.dut.at1.send_and_verify(f"AT+COPS=1,2,\"{operator_name_num}\",{net_type}",
                                             "OK", wait_for=ok_or_error, timeout=test_time_out))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                     f"\+COPS: 1,2,\"{operator_name_num}\",{net_type}",
                                                     wait_for=ok_or_error))
        else:
            test.log.error(
                "Cannot parse supported operator information from response, step skipped: Step 5. Test another valid network type can be manually registered")

        test.log.step("6. Test invalid operator and network cannot be registered")
        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=?", test_res_after_pin,
                     wait_for=ok_or_error, timeout=test_time_out, retry=3, sleep=5)
        cops_response = test.dut.at1.last_response
        invalid_operator_info = test.dut.dstl_get_forbidden_operators(cops_response,
                                                                      format_number="2")
        if invalid_operator_info:
            invalid_op_name_num, invalid_op_net_type = invalid_operator_info[0].split(',')
            test.expect(test.dut.at1.send_and_verify(
                f"AT+COPS=1,2,\"{invalid_op_name_num}\",{invalid_op_net_type}", "ERROR",
                wait_for=ok_or_error, timeout=test_time_out))
        else:
            test.log.error(
                "Cannot parse invalid operator information from response, step skipped: Step 6. Test invalid operator and network cannot be registered")

        test.log.step("7. Test deregister and re-register manually")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error))

        test.attempt(test.dut.at1.send_and_verify, "AT+COPS=?", test_res_after_pin,
                     wait_for=ok_or_error, timeout=test_time_out, retry=3, sleep=5)
        if valid_operator_info:
            test.expect(
                test.dut.at1.send_and_verify(f"AT+COPS=1,2,\"{operator_name_num}\",{net_type}",
                                             "OK", wait_for=ok_or_error))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?",
                                                     f"\+COPS: 1,2,\"{operator_name_num}\",{net_type}",
                                                     wait_for=ok_or_error))

        test.log.step("8. Test format can be save and restored from user profile")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,0", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,0,\"(\w|\s)+?\",\d"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,2", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,2,\"\d{5}\",\d"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,0,\"(\w|\s)+?\",\d"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,1", "OK", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,1,\"(\w|\s)+?\",\d"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,1,\"(\w|\s)+?\",\d"))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\+COPS: 0,0,\"(\w|\s)+?\",\d"))

        test.log.step("9. Test invalid parameters")
        test.log.step("9.1. Test invalid value format")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=-1", "ERROR", wait_for=ok_or_error))

        if test.dut.project is "SERVAL" or test.dut.project is "VIPER":
            # it does not make sense to discuss such errors with the project
            # no chance to get it repaired, so we ignore the fact that this is wrong:
            test.expect(test.dut.at1.send_and_verify("AT+COPS"))   # execute cmd should return ERROR!
        else:
            test.expect(test.dut.at1.send_and_verify("AT+COPS", "ERROR", wait_for=ok_or_error))

        test.log.step("9.2. Test unsupported value")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=5", "ERROR", wait_for=ok_or_error))
        test.log.step("9.3. Test unallowed value combinations")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=1,0", "ERROR", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=1,1", "ERROR", wait_for=ok_or_error))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "OK", wait_for="(OK|ERROR)"))
        if "COPS: 2" in test.dut.at1.last_response:
            test.expect(
                test.dut.at1.send_and_verify("AT+COPS=0", "OK", wait_for="(OK|ERROR)", timeout=30))

    def _read_operator_info(test, cops_response, op_status):
        operator_info = None
        regex = re.compile(
            "\+COPS: .*?\(({op_status},.+?,.+?,.+?,\d)\).*".format(op_status=op_status))
        match_groups = regex.findall(cops_response)
        if match_groups:
            operator_info = match_groups[0].split(',')
        else:
            operator_info = ['none', 'none', 'none', 'none', 'none']
        operator_name_long = operator_info[1].strip().strip('"')
        operator_name_short = operator_info[2].strip().strip('"')
        operator_name_number = operator_info[3].strip().strip('"')
        net_type = operator_info[4].strip()

        return operator_name_long, operator_name_short, operator_name_number, net_type


if __name__ == '__main__':
    unicorn.main()
