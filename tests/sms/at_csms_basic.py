# responsible: aleksander.denis@globallogic.com
# location: Wroclaw
# TC0091836.001

import re

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.select_message_service import dstl_set_message_service, dstl_read_message_service, \
    dstl_check_supported_settings_of_message_service


class Test(BaseTest):
    """
    TC0091836.001    AtCsmsBasic

    This procedure provides the possibility of basic tests for the test, read and write command of
    +CSMS.

    1. check command without and with PIN
    1.1 scenario without PIN: test, read and write commands should be PIN protected
    1.2 scenario with PIN
        - check test command response
        - check response for write command - service set to value 0
        - read the actual settings - service should be setting to: 0
        - check response for write command - service set to value 1
        - read the actual settings - service should be setting to: 1
        - reset settings to factory value by AT&F
        - read the actual settings
    2. check all parameters and also with invalid values
        - check EXEC command
        - check test command invalid value
        - check read command invalid value
        - try to set not supported value for service parameter: -1, 2, 3, 255
        - try to set empty write command
        - try to set service parameter value not as a number
        - try to set write command with more than 1 parameter
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)

    def run(test):
        test.log.h2("Executing script for test case TC0091836.001 - AtCsmsBasic")
        test.log.step("Step 1. check command without and with PIN")
        test.log.step("Step 1.1 scenario without PIN: test, read and write commands should be PIN"
                      " protected")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))
        test.expect(dstl_set_error_message_format(test.dut))
        test.sleep(10)
        test.expect(not dstl_check_supported_settings_of_message_service(test.dut))
        test.expect(re.search(r".*\+CMS ERROR: SIM PIN required.*", test.dut.at1.last_response))
        test.expect(not dstl_read_message_service(test.dut))
        test.expect(re.search(r".*\+CMS ERROR: SIM PIN required.*", test.dut.at1.last_response))
        test.expect(dstl_set_message_service(test.dut, "1", exp_resp="\+CMS ERROR: SIM PIN "
                                                                         "required"))

        test.log.step("Step 1.2 scenario with PIN")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("- check test command response")
        test.expect(dstl_check_supported_settings_of_message_service(test.dut))

        test.log.step("- check response for write command - service set to value 0")
        test.expect(dstl_set_message_service(test.dut, "0"))

        test.log.step("- read the actual settings - service should be setting to: 0")
        test.expect(dstl_read_message_service(test.dut, "0"))

        test.log.step("- check response for write command - service set to value 1")
        test.expect(dstl_set_message_service(test.dut, "1"))

        test.log.step("- read the actual settings - service should be setting to: 1")
        test.expect(dstl_read_message_service(test.dut, "1"))

        test.log.step("- reset settings to factory value by AT&F")
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))

        test.log.step("- read the actual settings")
        test.expect(dstl_read_message_service(test.dut, "0"))

        test.log.step("2. check all parameters and also with invalid values")
        test.log.step("- check EXEC command")
        test.expect(test.dut.at1.send_and_verify("AT+CSMS", ".*CMS ERROR:.*"))

        test.log.step("- check test command invalid value")
        test.expect(dstl_set_message_service(test.dut, "?1", "CMS ERROR:"))

        test.log.step("- check read command invalid value")
        test.expect(test.dut.at1.send_and_verify("AT+CSMS?ABC", ".*CMS ERROR:.*"))

        test.log.step("- try to set not supported value for service parameter: -1, 2, 3, 255")
        test.expect(dstl_set_message_service(test.dut, "-1", "CMS ERROR:"))
        test.expect(dstl_set_message_service(test.dut, "2", "CMS ERROR:"))
        test.expect(dstl_set_message_service(test.dut, "3", "CMS ERROR:"))
        test.expect(dstl_set_message_service(test.dut, "255", "CMS ERROR:"))

        test.log.step("- try to set empty write command")
        test.expect(dstl_set_message_service(test.dut, "", "CMS ERROR:"))

        test.log.step("- try to set service parameter value not as a number")
        test.expect(dstl_set_message_service(test.dut, "ABC", "CMS ERROR:"))

        test.log.step("- try to set write command with more than 1 parameter")
        test.expect(dstl_set_message_service(test.dut, "1,1", "CMS ERROR:"))

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

if "__main__" == __name__:
    unicorn.main()
