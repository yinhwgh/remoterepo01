# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0103913.001, TC0103913.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_sms import dstl_scfg_set_sms_auto_acknl
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_enable_sms_class_0_display, \
    dstl_configure_sms_event_reporting, dstl_read_sms_event_reporting_configuration, \
    dstl_set_sms_text_mode_parameters, dstl_read_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_parameters import ListSmsAcknl


class Test(BaseTest):
    """TC0103913.001 / TC0103913.002   SmsClass0WithDifferentDsInCnmiSettings
    The goal of the TC is to check if URC +CMT is displayed for SMS class 0 regardless of the URC +CNMI settings.
    Description:
    This scenario cover the issue IPIS100269019 and its next FUPs:
    1. Enable phase 2+ for SMS: AT+CSMS=1
    2. Set Text mode: AT+CMGF=1
    3. Set and check <ds>=1 via CNMI: AT+CNMI=2,1,0,1,1
    4. Set and check SMS class 0 configuration: e.g. AT+CSMP=17,167,0,16 or 17,167,0,240
    5. Send message to own number: AT+CMGS="OwnNumber"
    6. Wait for URC +CMT
    7. Set and check <ds>=0 via CNMI: AT+CNMI=2,1,0,0,1
    8. Repeat steps 4-6
    """

    def setup(test):
        test.log.h2("START of script for test case TC0103913.001/002 "
                    "SmsClass0WithDifferentDsInCnmiSettings")
        test.prepare_module_to_test()

    def run(test):
        test.log.info("This scenario cover the issue IPIS100269019 and its next FUPs:")
        test.log.step("Step 1. Enable phase 2+ for SMS: AT+CSMS=1")
        test.expect(dstl_set_message_service(test.dut, service='1'))

        test.log.step("Step 2. Set Text mode: AT+CMGF=1")
        test.expect(dstl_select_sms_message_format(test.dut, sms_format='Text'))

        test.log.step("Step 3. Set and check <ds>=1 via CNMI: AT+CNMI=2,1,0,1,1")
        test.set_and_check_cnmi_settings("1")

        test.execute_steps_4_6("16", "TEST MSG - CNMI ds=1 CSMP dcs=16")

        test.log.step("Step 7. Set and check <ds>=0 via CNMI: AT+CNMI=2,1,0,0,1")
        test.set_and_check_cnmi_settings("0")

        test.log.step("Step 8. Repeat steps 4-6")

        test.execute_steps_4_6("240", "TEST MSG - CNMI ds=0 CSMP dcs=240")

    def cleanup(test):
        test.log.info('===== Delete SMS from memory and restore values =====')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

    def prepare_module_to_test(test):
        test.log.info("Preparing DUT for test")
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_character_set(test.dut, character_set="GSM"))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_error_message_format(test.dut, err_mode='2'))
        test.expect(dstl_set_preferred_sms_memory(test.dut, preferred_storage="ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_enable_sms_class_0_display(test.dut, expected_response=".*OK.*"))
        test.expect(dstl_scfg_set_sms_auto_acknl(test.dut,
                                                 mode=ListSmsAcknl.NO_AUTOMATIC_ACKNOWLEDGEMENT))
        test.expect(dstl_set_sms_center_address(test.dut, center_addr=test.dut.sim.sca_int))

    def set_and_check_cnmi_settings(test, ds):
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="2", mt="1", bm="0", ds=ds,
                                                       bfr="1", exp_resp=".*OK.*"))
        test.expect(dstl_read_sms_event_reporting_configuration(test.dut)
                    == {"mode": "2", "mt": "1", "bm": "0", "ds": ds, "bfr": "1"})

    def execute_steps_4_6(test, dcs, text):
        test.log.step("Step 4. Set and check SMS class 0 configuration: e.g. AT+CSMP=17,167,0,16 "
                      "or 17,167,0,240")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, fo="17", vp_or_scts="167", pid="0",
                                                      dcs=dcs, exp_resp=".*OK.*"))
        test.expect(dstl_read_sms_text_mode_parameters(test.dut) == ['17', '167', '0', f'{dcs}\r'])

        test.log.step('Step 5. Send message to own number: AT+CMGS="OwnNumber"')
        test.expect(dstl_send_sms_message(test.dut, test.dut.sim.int_voice_nr, text,
                                          set_sms_format=False, set_sca=False))

        test.log.step("Step 6. Wait for URC +CMT")
        test.expect(dstl_check_urc(test.dut, r".*CMT:.*\"\{}\".*\s*[\n\r]{}.*".
                                   format(test.dut.sim.int_voice_nr, text), timeout=360))


if "__main__" == __name__:
    unicorn.main()