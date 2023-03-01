# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0091828.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, \
    dstl_set_full_functionality_mode
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters, \
    dstl_show_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_list_occupied_sms_indexes
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory_without_number, \
    dstl_write_sms_to_memory
from dstl.usim.get_imsi import dstl_get_imsi


class Test(BaseTest):
    """
    TC0091828.001 - TpAtCmgwBasic

    This procedure provides the possibility of basic tests for the test and write command of +CMGW.

    1. Test command without pin authentication and in airplane mode
        1.1 Check command without PIN,
        1.2 Check command in Airplane Mode,
    2. Test with pin,
        2.1 Check all command forms in PDU mode,
        2.2 Check all command forms in Text mode,
    3. Check with invalid values,
        3.1 Check PDU mode with invalid values,
            3.1.1 Test wring message with mismatched status and content type in PDU mode,
            3.1.2 Test wring message with incorrect length,
        3.2 Check Text mode with invalid values,

    AT command should be implemented and work as expected and described in documentation
    """

    OK_RESPONSE = r'.*OK.*'
    CMS_ERROR = r'.*CMS ERROR.*'
    PROMPT_OR_ERROR = r'>.*|.*CMS ERROR'
    CMS_ERROR_PIN = r'.*CMS ERROR: SIM PIN required.*'

    def setup(test):
        test.phone_number = test.dut.sim.int_voice_nr
        test.text = "text mode sms"
        test.pdu = f'{test.dut.sim.sca_pdu}1100{test.dut.sim.pdu}0000FF04F4F29C0E'
        test.length = dstl_calculate_pdu_length(test.pdu)
        test.valid_pdu = f'.*{test.dut.sim.pdu}.*FF04F4F29C0E.*'
        test.scts = '"94/05/06,22:10:00+08"'

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_imsi(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        dstl_set_error_message_format(test.dut)

    def run(test):
        test.log.info("Starting TC0091828.001 - TpAtCmgwBasic")

        test.log.step("Step 1  Test command without pin authentication and in airplane mode.")
        test.log.step("Step 1.1  Check command without PIN.")

        test.log.info("=== Check test command without PIN. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.CMS_ERROR_PIN))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command without PIN. ===")
        test.expect(dstl_write_sms_to_memory_without_number(test.dut,
                                                            exp_resp=test.CMS_ERROR_PIN,
                                                            exp_resp_sms_mode=test.CMS_ERROR_PIN))

        test.log.info("=== Check write command without PIN. ===")
        test.expect(dstl_write_sms_to_memory(test.dut, exp_resp=test.CMS_ERROR_PIN))

        test.log.step("Step 1.2  Check command in Airplane Mode.")
        test.log.info("=== Check Airplane Mode without PIN. ===")
        test.expect(dstl_set_airplane_mode(test.dut))

        test.log.info("=== Check test command without PIN in Airplane Mode. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.CMS_ERROR_PIN))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command without PIN in Airplane Mode. ===")
        test.expect(dstl_write_sms_to_memory_without_number(test.dut,
                                                            exp_resp=test.CMS_ERROR_PIN,
                                                            exp_resp_sms_mode=test.CMS_ERROR_PIN))

        test.log.info("=== Check write command without PIN in Airplane Mode. ===")
        test.expect(dstl_write_sms_to_memory(test.dut, exp_resp=test.CMS_ERROR_PIN))

        test.log.info("=== Check Airplane Mode with PIN. ===")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.info("=== Check CMGW command in PDU mode in Airplane Mode. ===")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))

        test.log.info("=== Check test command in Airplane Mode. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.OK_RESPONSE))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command in Airplane Mode. ===")
        test.expect(dstl_write_sms_to_memory_without_number(test.dut,
                                                            exp_resp=test.CMS_ERROR,
                                                            exp_resp_sms_mode=test.CMS_ERROR_PIN))

        test.log.info("=== Check write command in Airplane Mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length,
                                                     pdu=test.pdu, return_index=True))
        test.verify_stored_msg(test.valid_pdu, index[0])

        test.log.info("=== Check CMGW command in TEXT mode in Airplane Mode. ===")
        test.expect(dstl_select_sms_message_format(test.dut))

        test.log.info("=== Check test command in Airplane Mode. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.OK_RESPONSE))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command in Airplane Mode. ===")
        index = test.expect(dstl_write_sms_to_memory_without_number(test.dut, test.text,
                                                                    return_index=True))
        test.verify_stored_msg(test.text, index[1])

        test.log.info("=== Check write command in Airplane Mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number)

        test.log.step("Step 2  Test with pin.")
        test.expect(dstl_set_full_functionality_mode(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("Step 2.1 Check all command forms in PDU mode.")
        test.expect(dstl_select_sms_message_format(test.dut, 'pdu'))
        test.log.info(
            "See IPIS100311896 - lack description for ERROR response in AT Command set for PDU "
            "mode, error description based on description for Text mode.")

        test.log.info("=== Check test command in PDU mode. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.OK_RESPONSE))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command in PDU mode. ===")
        test.expect(dstl_write_sms_to_memory_without_number(test.dut,
                                                            exp_resp=test.CMS_ERROR,
                                                            exp_resp_sms_mode=test.CMS_ERROR_PIN))

        test.log.info("=== Check write command in PDU mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length,
                                                     pdu=test.pdu, return_index=True))
        test.verify_stored_msg(test.valid_pdu, index[0])

        test.log.info("=== Check write command in PDU mode with message status. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length,
                                                     pdu=test.pdu, stat="3", return_index=True))
        test.verify_stored_msg(test.valid_pdu, index[0], stat="3")

        test.log.info("=== Check write command special case - write PDU without SCA ===")
        pdu_special = f'001100{test.dut.sim.pdu}0000FF04F4F29C0E'
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU',
                                                     length=dstl_calculate_pdu_length(pdu_special),
                                                     pdu=pdu_special, return_index=True))
        test.verify_stored_msg(test.valid_pdu, index[0])

        test.log.info("=== Check prompt abort - PDU ===")
        test.check_prompt_abort(test.length, test.pdu)

        test.log.step("Step 2.2 Check all command forms in TEXT mode.")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))
        test.expect(dstl_show_sms_text_mode_parameters(test.dut))

        test.log.info("=== Check test command in TEXT mode. ===")
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=?", test.OK_RESPONSE))
        test.expect(".*CMGW.*" not in test.dut.at1.last_response)

        test.log.info("=== Check exec command in TEXT mode. ===")
        index = test.expect(dstl_write_sms_to_memory_without_number(test.dut, test.text,
                                                                    return_index=True))
        test.verify_stored_msg(test.text, index[1])

        test.log.info("=== Check write command without <toda> in TEXT mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number)

        test.log.info("=== Check write command with <toda> in TEXT mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number, toda="145",
                                                     return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, toda="145")

        test.log.info("=== Check write command with <toda> and with <stat> in TEXT mode. ===")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number, toda="145",
                                                     stat='STO SENT', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, toda="145",
                               stat="STO SENT")
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number, toda="145",
                                                     stat='STO UNSENT', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, toda="145",
                               stat="STO UNSENT")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "24", test.scts))
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number, toda="145",
                                                     stat='REC READ', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, toda="145",
                               stat="REC READ", scts=test.scts)
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number, toda="145",
                                                     stat='REC UNREAD', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, toda="145",
                               stat="REC UNREAD", scts=test.scts)

        test.log.info("=== Check write command without <toda> and with <stat> in TEXT mode. ===")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     stat='STO SENT', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, stat='STO SENT')

        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     stat='STO UNSENT', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number,
                               stat='STO UNSENT')

        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "24", test.scts))
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     stat='REC READ', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number, stat='REC READ',
                               scts=test.scts)
        index = test.expect(dstl_write_sms_to_memory(test.dut, sms_text=test.text,
                                                     phone_num=test.phone_number,
                                                     stat='REC UNREAD', return_index=True))
        test.verify_stored_msg(test.text, index[0], phone_number=test.phone_number,
                               stat='REC UNREAD', scts=test.scts)

        test.log.info("=== Check prompt abort - TEXT ===")
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))
        test.check_prompt_abort(test.phone_number, 'test abort')

        test.log.step("Step 3 Check with invalid values")
        test.log.step("Step 3.1 Check PDU mode with invalid values")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length + 5,
                                             stat="4", exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length="0",
                                             exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length="A",
                                             exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=123456789,
                                             exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=",3",
                                             exp_resp=test.CMS_ERROR))

        test.log.step(
            "Step 3.1.1 Test writing message with mismatched status and content type in PDU mode")
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length,
                                             pdu=test.pdu, stat="0", exp_resp=test.PROMPT_OR_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length,
                                             pdu=test.pdu, stat="1", exp_resp=test.PROMPT_OR_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length - 5,
                                             pdu=test.pdu, stat="0", exp_resp=test.PROMPT_OR_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length - 5,
                                             pdu=test.pdu, stat="1", exp_resp=test.PROMPT_OR_ERROR))

        test.log.step("Step 3.1.2 Test writing message with incorrect length,")
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length * 2,
                                             pdu=test.pdu, exp_resp=test.PROMPT_OR_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length * 3,
                                             pdu=test.pdu, exp_resp=test.PROMPT_OR_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, sms_format='PDU', length=test.length - 10,
                                             pdu=test.pdu, exp_resp=test.PROMPT_OR_ERROR))

        test.log.step("Step 3.2 Check Text mode with invalid values")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_write_sms_to_memory(test.dut, phone_num=test.phone_number, toda="256",
                                             exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, phone_num=test.phone_number, stat="ALL",
                                             exp_resp=test.CMS_ERROR))
        test.expect(dstl_write_sms_to_memory(test.dut, phone_num=test.phone_number, stat=3,
                                             exp_resp=test.CMS_ERROR))
        test.expect(test.dut.at1.send_and_verify('AT+CMGW=,,"STO SENT"', test.CMS_ERROR))

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)
        dstl_reset_settings_to_factory_default_values(test.dut)
        dstl_store_user_defined_profile(test.dut)

    def check_prompt_abort(test, number, content):
        sms_index = max(dstl_list_occupied_sms_indexes(test.dut))
        test.expect(test.dut.at1.send_and_verify(f'AT+CMGW={number}', '.*>.*', wait_for=".*>.*"))
        test.expect(
            test.dut.at1.send_and_verify(f'{content}', end="\u001B", expect=r".*OK.*", timeout=30))
        test.expect(sms_index == max(dstl_list_occupied_sms_indexes(test.dut)))

    def verify_stored_msg(test, content, index, **kwargs):
        test.log.info(f'Expected msg content: {content}')
        test.expect(re.search(f'.*{content}.*', dstl_read_sms_message(test.dut, index)))

        for key, value in kwargs.items():
            if "+" in value:
                value = str(value).replace("+", "\\+")
            test.log.info(f'Expected {key}: {value}')
            test.expect(re.search(f'.*"?{value}"?.*', test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
