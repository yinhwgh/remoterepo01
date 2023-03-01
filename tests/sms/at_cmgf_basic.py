# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0091824.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.select_sms_format import dstl_select_sms_message_format, dstl_check_sms_mode,\
    dstl_check_supported_sms_formats


class Test(BaseTest):
    """
    This procedure provides the possibility of basic tests for the test, read and write command
    of +CMGF.

    Step 1: check command without and with PIN
    Step 2: check all parameters and also with invalid values

    A functional check is not done here - functionality is check in functional test eg.
    PDUMode, TextMode
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))

    def run(test):
        test.log.step("1. Check command without and with PIN")
        test.log.info("=== Check command without PIN ===")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))
        test.expect(dstl_set_error_message_format(test.dut, "2"))
        test.sleep(10)
        test.expect(not dstl_check_supported_sms_formats(test.dut))
        test.expect(re.search(r".*ERROR: SIM PIN required.*", test.dut.at1.last_response))
        test.expect(not dstl_check_sms_mode(test.dut))
        test.expect(re.search(r".*ERROR: SIM PIN required.*", test.dut.at1.last_response))
        test.expect(not dstl_select_sms_message_format(test.dut))
        test.expect(re.search(r".*ERROR: SIM PIN required.*", test.dut.at1.last_response))

        test.log.info("=== Check command with PIN ===")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_check_supported_sms_formats(test.dut))
        test.expect(dstl_check_sms_mode(test.dut) == "PDU")
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))

        test.log.step("2. Check all parameters and also with invalid values")
        test.log.info("=== Check command valid values ===")
        test.expect(dstl_check_sms_mode(test.dut) == "PDU")
        test.expect(dstl_select_sms_message_format(test.dut, "Text"))
        test.expect(dstl_check_sms_mode(test.dut) == "Text")
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))
        test.expect(dstl_check_sms_mode(test.dut) == "PDU")

        test.log.info("=== Check command invalid values ===")
        for parameter_value in ["2", "-1", "114", "a", "", '""', "1,2"]:
            test.expect(test.dut.at1.send_and_verify(f"AT+CMGF={parameter_value}", ".*ERROR.*"))

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))


if "__main__" == __name__:
    unicorn.main()
