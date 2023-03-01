# responsible: aleksander.denis@globallogic.com
# location: Wroclaw
# TC0091835.001

import unicorn

import re

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
from dstl.sms.configure_sms_text_mode_parameters import dstl_read_sms_text_mode_parameters, \
    dstl_set_sms_text_mode_parameters


class Test(BaseTest):
    """
    TC0091835.001 - AtCsmpBasic    #test procedure version: 0.8

    INTENTION
    This procedure provides the possibility of basic tests for the test and write command of +CSMP.
    Functional tests are not done here.

    PRECONDITION
    none.

    1) Verification of the PIN requirement:
    1.1) Test call without PIN.
    1.2) Read call without PIN.
    1.3) Argumentless call without PIN.
    1.4) Correct write call without PIN.
    2) Unmodyfying, positive tests with PIN:
    2.1) Test call with PIN.
    2.2) Read call with PIN.
    3) Invalid (values out of bounds, characters, too many parameters) parameters handling while
    PINned.
    4) Positive* (one negative on part of the platforms) write tests while pinned:
    4.1) Write full value and verify if it was store.
    4.2) Short write call with verification.?
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)

    def run(test):
        test.log.h2("Executing script for test case TC0091835.001 - AtCsmpBasic")
        test.log.step("Step 1  Verification of the PIN requirement:")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))
        test.expect(dstl_set_error_message_format(test.dut))
        test.log.step("Step 1.1  Test call without PIN.")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut,fo="?",
                                                      exp_resp=".*CMS ERROR: SIM PIN required.*"))

        test.log.step("Step 1.2  Read call without PIN.")
        test.expect(not dstl_read_sms_text_mode_parameters(test.dut))
        test.expect(re.search(r".*\+CMS ERROR: SIM PIN required.*", test.dut.at1.last_response))

        test.log.step("Step 1.3  Argumentless call without PIN.")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut,fo="",
                                                      exp_resp=".*CMS ERROR: SIM PIN required.*"))

        test.log.step("Step 1.4 Correct write call without PIN.")
        test.expect(
            dstl_set_sms_text_mode_parameters(test.dut, exp_resp=".*CMS ERROR: SIM PIN required.*"))

        test.log.step("Step 2  Unmodyfying, positive tests with PIN:")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("Step 2.1 Test call with PIN.")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=?", ".*OK.*"))
        test.expect(".*CSMP:.*" not in test.dut.at1.last_response)

        test.log.step("Step 2.2 Read call with PIN.")
        test.log.info(
            "Verify CSMP? PowerUp values - should be: <fo>=17, <vp>=167, <pid> in range (0-255), "
            "<dcs> in range (0-247)")
        csmp_settings = dstl_read_sms_text_mode_parameters(test.dut)
        test.expect(csmp_settings[0] == '17')
        test.expect(csmp_settings[1] == '167')
        test.expect(int(csmp_settings[2]) in range(0,255))
        test.expect(int(csmp_settings[3]) in range(0,247))

        test.log.step(
            "Step 3 Invalid (values out of bounds, characters, too many parameters) parameters "
            "handling while PINned.")
        test.log.info(
            "According to IPIS100201608 it is possible to set VP parameter up to 2000000000")
        invalid_values = ["0,2000000000", "256,2", "1,,247", "-1", ",,-3", ",,0,0", "0,3,aa",
                          ",,,,,,,4"]
        for invalid in invalid_values:
            test.expect(dstl_set_sms_text_mode_parameters(test.dut, invalid,
                                                          exp_resp=".*CMS ERROR:.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP", ".*CMS ERROR:.*"))

        test.log.step(
            "Step 4 Positive* (one negative on part of the platforms) write tests while pinned:")
        test.log.step("Step 4.1  Write full value and verify if it was store.")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, '17', '166', '1', '1'))
        test.expect(dstl_read_sms_text_mode_parameters(test.dut) == ['17', '166', '1', '1\r'])

        test.log.step("Step 4.2  Short write call with verification.")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, '2'))
        test.expect(dstl_read_sms_text_mode_parameters(test.dut)[0] == '2')

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))


if "__main__" == __name__:
    unicorn.main()
