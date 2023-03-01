# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0091827.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.configure_sms_pdu_parameters import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_enable_sms_urc


class Test(BaseTest):
    """TC0091827.001    AtCmgsBasic

    This procedure provides the possibility of basic tests for the test and write command of +CMGS.

    1. Check command without and with PIN
    2. Check all parameters and also with invalid values
    """

    TIMEOUT_SMS = 120
    TIMEOUT_SMS_LONG = 360
    CMS_PIN_ERROR = r".*\+CMS ERROR: SIM PIN required.*"
    CMS_ERROR = r".*\+CMS ERROR.*"
    OK = ".*OK.*"

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.step("1. Check command without and with PIN")
        test.log.info("===== Check CMGS command without PIN =====")
        test.log.info("===== Check CMGS Test command (AT+CMGS=?) =====")
        test.check_test_command_cmgs(test.CMS_PIN_ERROR)
        test.log.info("===== Check CMGS Write command =====")
        pdu_content = '{}1100{}0000FF04F4F29C0E'.format(test.dut.sim.sca_pdu, test.dut.sim.pdu)
        pdu_length = dstl_calculate_pdu_length(pdu_content)
        test.expect(test.dut.at1.send_and_verify('AT+CMGS={}'.format(pdu_length),
                                                 test.CMS_PIN_ERROR))
        test.execute_part_if_unexpected_prompt(pdu_content)
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.int_voice_nr),
                                                 test.CMS_PIN_ERROR))
        test.execute_part_if_unexpected_prompt('Cmgs Error')

        test.log.info("===== Check CMGS command with PIN =====")
        test.log.info("===== Prepare module to test with PIN authentication =====")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(10)  # waiting for module to get ready
        test.expect(dstl_set_character_set(test.dut, 'GSM'))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, 'ME'))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_message_service(test.dut, service="0"))
        test.expect(dstl_enable_sms_urc(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))

        test.log.info('===== Start the proper test with PIN authentication in TEXT mode =====')
        test.check_test_command_cmgs(test.OK)
        test.send_and_read_sms_in_text_mode("SMS test 1 without toda", test.dut.sim.int_voice_nr)
        test.send_and_read_sms_in_text_mode("SMS test 2 without toda", test.dut.sim.nat_voice_nr)
        test.send_and_read_sms_in_text_mode("SMS test 3 with toda", test.dut.sim.int_voice_nr, "145")
        test.send_and_read_sms_in_text_mode("SMS test 4 with toda", test.dut.sim.nat_voice_nr, "129")

        test.log.info("===== Start the proper test with PIN authentication in PDU mode =====")
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))
        test.check_test_command_cmgs(test.OK)
        test.expect(test.dut.at1.send_and_verify("AT+CMGS={}".format(pdu_length), ".*>.*"))
        test.expect(test.dut.at1.send_and_verify(pdu_content, end="\u001A",
                                                 expect=r"\+CMGS: \d{{1,3}}{}".
                                                 format(test.OK), timeout=test.TIMEOUT_SMS))
        test.reading_incoming_sms(".*{}.*{}.*".format(test.dut.sim.pdu, "04F4F29C0E"))

        test.log.step("2. Check all parameters and also with invalid values")
        invalid_values = ["", "XYZ", "-255", "XYZ,145", "-255,145", "+4810000000,-1",
                          "+4810000000,256", "\"XYZ\"", "\"-255\"", "\"XYZ\",145", "\"-255\",145",
                          "\"+4810000000\",-1", "\"+4810000000\",256", "14,-1", "14,256",
                          "\"14\",-1", "\"14\",256"]
        test.log.info("===== Test all parameters with invalid values in PDU Mode =====")
        test.expect(dstl_select_sms_message_format(test.dut, "PDU"))
        for value in invalid_values:
            test.expect(
                dstl_send_sms_message(test.dut, value, "0011000000FF0CD3E614442FCFE92028B10A",
                                      sms_format="PDU", set_sms_format=False, set_sca=False,
                                      first_expect=".*CMS ERROR.*", exp_resp=".*CMS ERROR.*"))
        test.expect(
            dstl_send_sms_message(test.dut, "14,1", "0011000000FF0CD3E614442FCFE92028B10A",
                                  sms_format="PDU", set_sms_format=False, set_sca=False,
                                  first_expect=".*CMS ERROR.*", exp_resp=".*CMS ERROR.*"))
        test.log.info("===== Test all parameters with invalid values in Text Mode =====")
        test.expect(dstl_select_sms_message_format(test.dut))
        for value in invalid_values:
            test.expect(test.dut.at1.send_and_verify("AT+CMGS={}".format(value), test.CMS_ERROR))
            test.execute_part_if_unexpected_prompt('Cmgs Error')

    def cleanup(test):
        dstl_delete_all_sms_messages(test.dut)

    def execute_part_if_unexpected_prompt(test, msg):
        if ">" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify(msg, end="\u001A", expect=".*OK|ERROR.*", timeout=60)

    def check_test_command_cmgs(test, exp_resp):
        test.expect(test.dut.at1.send_and_verify('AT+CMGS=?', exp_resp))
        if exp_resp == test.OK:
            test.expect(not re.search(r".*CMGS:.*", test.dut.at1.last_response))

    def send_and_read_sms_in_text_mode(test, msg, da, toda=None):
        if toda:
            test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\",{}".format(da, toda),
                                                     expect=".*>.*", wait_for=".*>.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(da), expect=">",
                                                     wait_for=".*>.*"))
        test.expect(test.dut.at1.send_and_verify(msg, end="\u001A", expect=r"\+CMGS: \d{{1,3}}{}".
                                                 format(test.OK), wait_for=test.OK,
                                                 timeout=test.TIMEOUT_SMS))
        test.reading_incoming_sms(r'.*"\{}".*\s*{}.*'.format(test.dut.sim.int_voice_nr, msg))

    def reading_incoming_sms(test, exp_resp):
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.TIMEOUT_SMS_LONG))
        sms_index = re.search(r".*\",(\d{1,3})", test.dut.at1.last_response)
        if sms_index is not None:
            test.expect(dstl_read_sms_message(test.dut, sms_index.group(1)))
            test.log.info("Expected REGEX: {}".format(exp_resp))
            test.expect(re.search(exp_resp, test.dut.at1.last_response))
        else:
            test.expect(False, msg="Module does not received SMS in required timeout")


if "__main__" == __name__:
    unicorn.main()
