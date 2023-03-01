# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0091831.001

import re
import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_sms import dstl_scfg_set_sms_auto_acknl
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_disable_sms_class_0_display, dstl_show_sms_text_mode_parameters, \
    dstl_set_sms_text_mode_parameters, dstl_confirm_acknowledgement_new_sms_deliver, \
    dstl_check_supported_settings_of_acknowledgement_new_sms_deliver
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """ TC0091831.001 AtCnmaBasic
    This procedure provides the possibility of basic tests for the test and write command of +CNMA.

    Step 1: Check command without and with PIN
    Step 2: Check all parameters and also with invalid values
    Step 3: Check functionality by creating, sending and receiving SMS in PDU and text mode and send
     a corresponding acknowledge or send no or a wrong acknowledge.
    """

    SMS_TIMEOUT = 360
    SMS_TIMEOUT_NO_URC = 60
    CMS_ERROR_SIM_PIN = r"\+CMS ERROR: SIM PIN required"
    CMS_ERROR = r"\+CMS ERROR:.*"
    OK = r".*OK.*"
    CMS_ERROR_CNMA = r".*CMS ERROR: no \+CNMA acknowledgement expected.*"

    def setup(test):
        test.prepare_module_to_test(test.dut, '===== Preparing DUT for test =====')
        test.prepare_module_to_test(test.r1, '===== Preparing REMOTE for test =====')
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.h2("Starting TP for TC0091831.001 AtCnmaBasic")
        test.log.step("Step 1. Check command without and with PIN")
        test.log.info('===== Scenario without PIN authentication =====')
        test.expect(dstl_check_supported_settings_of_acknowledgement_new_sms_deliver(test.dut,
                                                                            test.CMS_ERROR_SIM_PIN))
        test.check_cnma_command(parameter="", exp_resp=test.CMS_ERROR_SIM_PIN)
        test.check_cnma_command(parameter="1", exp_resp=test.CMS_ERROR_SIM_PIN)

        test.log.info('===== Scenario with PIN authentication =====')
        test.expect(dstl_enter_pin(test.dut), critical=True)
        test.sleep(10)  # waiting for module to get ready
        test.log.info("===== NOTE: according to ATC: \n Execute and write command shall only be "
                      "used when AT+CSMS parameter <service> equals 1 (= phase 2+) =====")
        test.expect(dstl_set_message_service(test.dut, service="1", exp_resp=test.OK))
        test.expect(dstl_set_error_message_format(test.dut))
        test.expect(dstl_check_supported_settings_of_acknowledgement_new_sms_deliver(test.dut))
        test.check_cnma_command(parameter="", exp_resp=test.CMS_ERROR_CNMA)
        test.check_cnma_command(parameter="1", exp_resp=test.CMS_ERROR_CNMA)

        test.log.step("2. Check all parameters and also with invalid values")
        invalid_parameters = ["1000", "3", "-1", "-0", "ABC", "1,37537", "1,0"]
        ###used send_and_verify(), as it checks the correct syntax of the command
        test.expect(test.dut.at1.send_and_verify('AT+CNMA?', test.CMS_ERROR))
        for param in invalid_parameters:
            test.check_cnma_command(parameter=param, exp_resp=test.CMS_ERROR)

        test.log.step('3. Check functionality by creating, sending and receiving SMS in PDU and '
                      'text mode and send a corresponding acknowledge or send no or a wrong '
                      'acknowledge')
        test.prepare_module_to_functional_test(test.dut, '===== Preparing DUT for functional test '
                                                         'in step 3 =====')
        test.prepare_module_to_functional_test(test.r1, '===== Preparing Remote for functional '
                                                        'test in step 3 =====')

        test.log.info('===== Start the proper functional test in step 3 =====')
        test.log.info('===== Check CNMA command in Text Mode =====')
        test.expect(dstl_select_sms_message_format(test.dut))
        test.log.info("===== Check CNMA command in Text Mode - SMS Class 3 - CMT URC =====")
        test.check_cnma_functionality_test("Text Mode", "243", "Test SMS class 3 Text Mode", "CMT")
        test.log.info("===== Check CNMA command in Text Mode - SMS Class None - CMTI URC =====")
        test.check_cnma_functionality_test("Text Mode", "0", "Test SMS class None Text Mode",
                                           "CMTI")

        test.log.info('===== Check CNMA command in PDU Mode =====')
        test.expect(dstl_select_sms_message_format(test.dut, sms_format="PDU"))
        test.log.info("===== Check CNMA command in PDU Mode - Exec command - SMS Class 3 - CMT "
                      "URC =====")
        test.check_cnma_functionality_test("PDU Exec", "243", "Test SMS PDU Mode", "CMT")
        test.log.info("===== Check CNMA command in PDU Mode - Write command (CNMA=2 and CNMA=1) "
                      "- SMS Class 3 - CMT URC =====")
        test.check_cnma_functionality_test("PDU Write CNMA=2 and CNMA=1", "243", "Test SMS PDU Mode"
                                           , "CMT")
        test.log.info("===== Check CNMA command in PDU Mode - Write command (CNMA=0) - SMS Class 3 "
                      "- CMT URC =====")
        test.check_cnma_functionality_test("PDU Write CNMA=0", "243", "Test SMS PDU Mode", "CMT")
        test.log.info("===== Check CNMA command in PDU Mode - Write command - SMS Class None - "
                      "CMTI URC =====")
        test.check_cnma_functionality_test("PDU", "0", "Test SMS PDU Mode", "CMTI")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_reset_settings_to_factory_default_values(test.r1))
        test.expect(dstl_store_user_defined_profile(test.r1))

    def prepare_module_to_test(test, device, text):
        test.log.info(text)
        dstl_detect(device)
        dstl_get_imei(device)
        dstl_get_bootloader(device)
        dstl_set_scfg_urc_dst_ifc(device)

    def prepare_module_to_functional_test(test, device, text):
        test.log.info(text)
        test.expect(dstl_register_to_network(device), critical=True)
        test.expect(dstl_set_error_message_format(test.dut))
        test.expect(dstl_select_sms_message_format(device))
        test.expect(dstl_set_preferred_sms_memory(device, 'ME'))
        test.expect(dstl_delete_all_sms_messages(device))
        test.expect(dstl_set_character_set(device, "GSM"))
        test.expect(dstl_set_sms_center_address(device, device.sim.sca_int))
        test.expect(dstl_set_message_service(device, service="1", exp_resp=test.OK))
        test.expect(dstl_configure_sms_event_reporting(device, mode="2", mt="3"))
        test.expect(dstl_scfg_set_sms_auto_acknl(device, "0", test.OK))
        test.expect(dstl_disable_sms_class_0_display(device))
        test.expect(dstl_show_sms_text_mode_parameters(device))

    def check_cnma_command(test, parameter="", exp_resp=".*OK.*"):
        test.expect(dstl_confirm_acknowledgement_new_sms_deliver(test.dut, num_for_pdu=parameter,
                                                                 expected_response=exp_resp,
                                                                 force_execution=True, timeout=1))

    def set_csmp_settings(test, device, dcs, text):
        test.log.info(text)
        test.expect(dstl_set_sms_text_mode_parameters(device, fo="17", vp_or_scts="167", pid="0",
                                                      dcs=dcs, exp_resp=test.OK))

    def check_cnma_functionality_test(test, mode, dcs, text, urc):
        if mode == "Text Mode":
            text_urc = text
        else:
            text_urc = "D4F29C0E9A36A72028B10A6ABEC965"
        test.set_csmp_settings(test.r1, dcs, text)
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, text, 'Text',
                                          set_sms_format=False, set_sca=False))
        if urc == "CMT":
            exp_urc = test.expect(dstl_check_urc(test.dut, '.*{}:.*{}.*'.format(urc, text_urc),
                                                 timeout=test.SMS_TIMEOUT))
        else:
            exp_urc = test.expect(dstl_check_urc(test.dut, '.*{}:.*'.format(urc),
                                                 timeout=test.SMS_TIMEOUT))
        if exp_urc:
            if urc == "CMTI":
                test.check_cnma_command(parameter="", exp_resp=test.CMS_ERROR_CNMA)
            else:
                if mode == "PDU Exec":
                    test.check_cnma_command(parameter="", exp_resp=test.OK)
                    test.expect(test.check_no_urc(".*CMT:.*", test.SMS_TIMEOUT_NO_URC))
                elif mode == "PDU Write CNMA=2 and CNMA=1":
                    test.check_cnma_command(parameter="2", exp_resp=test.OK)
                    test.expect(dstl_check_urc(test.dut, '.*{}:.*{}.*'.format(urc, text_urc),
                                               timeout=test.SMS_TIMEOUT))
                    test.check_cnma_command(parameter="1", exp_resp=test.OK)
                    test.expect(test.check_no_urc(".*CMT:.*", test.SMS_TIMEOUT_NO_URC))
                elif mode == "PDU Write CNMA=0":
                    test.check_cnma_command(parameter="0", exp_resp=test.OK)
                    test.expect(test.check_no_urc(".*CMT:.*", test.SMS_TIMEOUT_NO_URC))
                else:
                    test.check_cnma_command(parameter="2", exp_resp=test.CMS_ERROR)
                    test.check_cnma_command(parameter="1", exp_resp=test.CMS_ERROR)
                    test.check_cnma_command(parameter="", exp_resp=test.OK)
                    test.expect(test.check_no_urc(".*CMT:.*", test.SMS_TIMEOUT_NO_URC))
        else:
            test.expect(False, msg="Checking CNMA command after {} for {} impossible - message NOT "
                                   "delivered.".format(urc, text))

    def check_no_urc(test, urc, timeout):
        elapsed_seconds = 0
        start_time = time.time()
        result = True
        while elapsed_seconds < timeout:
            if re.search(urc, test.dut.at1.last_response):
                result = False
                break
            elapsed_seconds = time.time() - start_time
        return result


if "__main__" == __name__:
    unicorn.main()
