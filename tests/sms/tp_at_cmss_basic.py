# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0091830.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory, \
    dstl_write_sms_to_memory_without_number


class Test(BaseTest):
    """TC0091830.001   TpAtCmssBasic

    This procedure provides the possibility of basic tests for the test and write command of +CMSS.

    1. Check command without PIN
    2. Check command with PIN
    3. Check all parameters also with invalid values

    """

    OK_RESPONSE = r'.*OK.*'
    CMS_ERROR = r'.*CMS ERROR.*'
    CMS_ERROR_PIN = r'.*CMS ERROR: SIM PIN required.*'

    def setup(test):
        test.int_phone_number = test.dut.sim.int_voice_nr
        test.text = 'text mode sms'
        test.valid_received_pdu = f'{test.dut.sim.pdu}.*65D0BC3D07'

        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_urc_dst_ifc(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        dstl_set_error_message_format(test.dut)

    def run(test):
        test.log.info("Starting TC0091830.001 TpAtCmssBasic")

        test.log.step("1. Check command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CMSS=?", test.CMS_ERROR_PIN))
        test.expect(dstl_send_sms_message_from_memory(test.dut, 0, exp_resp=test.CMS_ERROR_PIN))

        test.log.step("2. Check command with PIN")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.info("=== Check test command with PIN ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMSS=?", test.OK_RESPONSE))
        test.expect(".*CMSS.*" not in test.dut.at1.last_response)

        test.log.info("=== Check write command with empty memory ===")
        test.expect(dstl_send_sms_message_from_memory(test.dut, 0, exp_resp=test.CMS_ERROR))

        test.log.step("3. Check all parameters also with invalid values")
        test.log.info("=== Prepare module for sending sms ===")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_character_set(test.dut, "GSM"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_set_message_service(test.dut))
        test.expect(dstl_configure_sms_event_reporting(test.dut, "2", "1"))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))

        test.log.info("=== Prepare messages in storage ===")
        test.expect(dstl_select_sms_message_format(test.dut, "TEXT"))
        msg_index_no_da = \
            test.expect(dstl_write_sms_to_memory_without_number(test.dut, sms_text=test.text,
                                                                return_index=True))
        msg_index_with_da = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                                 phone_num=test.int_phone_number,
                                                                 return_index=True))

        test.log.info("=== Check write command in TEXT mode ===")
        test.log.info("=== Check write command with no da specified ===")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      exp_resp=test.CMS_ERROR))

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      destination_addr=test.int_phone_number))
        test.verify_delivered_msg(test.text)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      destination_addr=test.int_phone_number,
                                                      toda="145"))
        test.verify_delivered_msg(test.text)

        test.log.info("=== Check write command with da ===")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0]))
        test.verify_delivered_msg(test.text)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0],
                                                      destination_addr=test.int_phone_number))
        test.verify_delivered_msg(test.text)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0],
                                                      destination_addr=test.int_phone_number,
                                                      toda="145"))
        test.verify_delivered_msg(test.text)

        test.log.info("=== Check write command in PDU mode ===")
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))

        test.log.info("=== Check write command with no da specified ===")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      exp_resp=test.CMS_ERROR))

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      destination_addr=test.int_phone_number))
        test.verify_delivered_msg(test.valid_received_pdu)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_no_da[1],
                                                      destination_addr=test.int_phone_number,
                                                      toda="145"))
        test.verify_delivered_msg(test.valid_received_pdu)

        test.log.info("=== Check write command with da ===")
        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0]))
        test.verify_delivered_msg(test.valid_received_pdu)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0],
                                                      destination_addr=test.int_phone_number))
        test.verify_delivered_msg(test.valid_received_pdu)

        test.expect(dstl_send_sms_message_from_memory(test.dut, msg_index_with_da[0],
                                                      destination_addr=test.int_phone_number,
                                                      toda="145"))
        test.verify_delivered_msg(test.valid_received_pdu)

        test.log.info("=== Starting test for invalid values ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMSS", test.CMS_ERROR))
        test.expect(test.dut.at1.send_and_verify("AT+CMSS?", test.CMS_ERROR))
        invalid_values = ["", "-1", "-1,abc", "-1,abc,abc", "abc", "abc,abc", "abc,abc,abc", "256",
                          "256,256", "256,256,256", "10", "0,,145", "0,,129",
                          f'1,"{test.int_phone_number}","a"']
        for invalid in invalid_values:
            test.expect(
                dstl_send_sms_message_from_memory(test.dut, invalid, exp_resp=test.CMS_ERROR))

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

    def verify_delivered_msg(test, content):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=360))
        sms_received = re.search(r"CMTI:.*\",\s*(\d{1,3})", test.dut.at1.last_response)
        if sms_received:
            test.log.info(f"Expected msg content: {content}")
            test.expect(
                re.search(f".*{content}.*", dstl_read_sms_message(test.dut, sms_received[1])))
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()
