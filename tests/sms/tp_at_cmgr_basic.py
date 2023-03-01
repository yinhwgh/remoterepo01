# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0091826.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.auxiliary_sms_functions import dstl_calculate_pdu_length
from dstl.sms.configure_sms_text_mode_parameters import dstl_set_sms_text_mode_parameters, \
    dstl_show_sms_text_mode_parameters, dstl_hide_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message, dstl_check_support_of_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    This procedure provides the possibility of basic tests for the test and write command of +CMGR.

    1) Tests without PIN authentication:
    1.1) Check CMGR Test command (AT+CMGR=?).
    1.2) Check CMGR Write command (AT+CMGR=1).
    2) Authenticated with PIN tests on an empty SMS memory:
    2.1) Check CMGR Test command (AT+CMGR=?).
    2.2) Check CMGR Write command on an empty index (e.g. AT+CMGR=1).
    3) Tests with filled SMS memory:
    3.1) Fill memory with messages with every <stat> value (REC UNREAD, REC READ, STO UNSENT, STO
    SENT).
    3.2) Set AT+CSDH=1 to present detailed header information.
    3.3) Read message with status UNSENT in Text mode (AT+CMGR=<index of unsent SMS>).
    3.4) Read message with status SENT in Text mode (AT+CMGR=<index of a sent SMS>).
    3.5) Read message with status UNREAD in Text mode (AT+CMGR=<index of unread SMS>).
    3.6) Read messages with status READ in Text mode - 2 messages: previously read and saved with
    read status
    (AT+CMGR=<index of read SMS>).
    3.7) Read message with status UNSENT in PDU mode (AT+CMGR=<index of unsent SMS>).
    3.8) Read message with status SENT in PDU mode (AT+CMGR=<index of a sent SMS>).
    3.9) Read message with status UNREAD in PDU mode (AT+CMGR=<index of unread SMS>).
    3.10) Read messages with status READ in PDU mode - 2 messages: previously read and saved with
     read status
    (AT+CMGR=<index of read SMS>).
    3.11) Repeat steps 3.3 - 3.10 with CSDH=0
    4.) Invalid parameters test:
    4.1) Check CMGR Write command with: negative 0 (AT+CMGR=-0).
    4.2) Check CMGR Write command with negative integer (AT+CMGR=-1).
    4.3) Check CMGR Write command with number beyond capacity (AT+CMGR=<storage capacity +1>).
    4.4) Check CMGR Write command with string (AT+CMGR="One").
    4.5) Check CMGR Write command with empty parameter (AT+CMGR=)
    4.6) Check CMGR Read command (AT+CMGR?).
    4.7) Check CMGR Exec command (AT+CMGR).
    """

    status = ["STO UNSENT", "STO SENT", "REC UNREAD", "REC UNREAD", "REC UNREAD", "REC UNREAD",
              "REC READ"]
    scts = '"94/05/06,22:10:00+08"'
    int_voice_nr = '+48500100200'
    sca_int = "+48601000310"
    pdu_messages = {
        "STO UNSENT": '07918406010013F011000B918405100002F00000A70F53EA1354754E8B4E2A885E9ED301',
        "STO SENT": '07918406010013F011000B918405100002F00000A70D53EA13342D3AA9207A794E07',
        "REC UNREAD":
            '07918406010013F0180B918405100002F00000495060220100800FD2E21054754A8B4122885E9ED301',
        "REC READ": '07918406010013F0180B918405100002F00000495060220100800DD2E210242D0689207A794E07'
    }
    indexes_list=[]

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.step("1) Tests without PIN authentication:")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))

        test.log.step("1.1) Check CMGR Test command (AT+CMGR=?).")
        test.expect(dstl_check_support_of_read_sms_message(
            test.dut, True, ".*CMS ERROR: SIM PIN required.*"))

        test.log.step("1.2) Check CMGR Write command (AT+CMGR=1).")
        test.expect(not dstl_read_sms_message(test.dut, 1))
        test.expect(re.search(r".*CMS ERROR: SIM PIN required.*", test.dut.at1.last_response))

        test.log.step("2) Authenticated with PIN tests on an empty SMS memory:")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", "all"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step("2.1) Check CMGR Test command (AT+CMGR=?).")
        test.expect(dstl_check_support_of_read_sms_message(test.dut, True))
        test.expect(not re.search(".*CMGR:.*", test.dut.at1.last_response))

        test.log.step("2.2) Check CMGR Write command on an empty index (e.g. AT+CMGR=1).")
        test.expect(not dstl_read_sms_message(test.dut, 1))
        test.expect(re.search(r".*OK.*", test.dut.at1.last_response))
        test.expect(not re.search(".*CMGR:.*", test.dut.at1.last_response))

        test.log.step("3) Tests with filled SMS memory:")
        test.log.step("3.1) Fill memory with messages with every <stat> value (REC UNREAD, REC"
                      " READ, STO UNSENT, STO SENT).")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))

        for current_status in test.status:
            test.indexes_list.append(int(dstl_write_sms_to_memory(test.dut, "{} test".format(
                current_status),phone_num=test.int_voice_nr,stat=current_status,
                                                                  return_index=True)[0]))
            if current_status == "STO SENT":
                test.expect(dstl_set_sms_text_mode_parameters(test.dut, "24", test.scts))
        test.expect(len(test.indexes_list) == len(test.status), critical=True)

        test.log.step("3.2) Set AT+CSDH=1 to present detailed header information.")
        test.expect(dstl_show_sms_text_mode_parameters(test.dut))

        test.execute_steps_3_3_to_3_10(csdh_value=1)

        test.log.step("3.11) Repeat steps 3.3 - 3.10 with CSDH=0")
        test.expect(dstl_hide_sms_text_mode_parameters(test.dut))
        test.execute_steps_3_3_to_3_10(csdh_value=0, skip_sms_index=2)

        test.log.step("4.) Invalid parameters test:")
        test.log.step("4.1) Check CMGR Write command with: negative 0 (AT+CMGR=-0).")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=-0", ".*CMS ERROR.*"))

        test.log.step("4.2) Check CMGR Write command with negative integer (AT+CMGR=-1).")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=-1", ".*CMS ERROR.*"))

        test.log.step("4.3) Check CMGR Write command with number beyond capacity (AT+CMGR=<storage "
                      "capacity +1>).")
        storage_capacity = dstl_get_sms_memory_capacity(test.dut, 1)
        test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(storage_capacity),
                                                 ".*CMS ERROR: invalid memory index.*"))
        test.log.info("Additional <index> greater than 32767 will be check - according to ATC "
                      "expected: CMS ERROR: invalid parameter")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=32768",
                                                 ".*CMS ERROR: invalid parameter.*"))

        test.log.step("4.4) Check CMGR Write command with string (AT+CMGR=\"One\").")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=\"One\"", ".*CMS ERROR.*"))

        test.log.step("4.5) Check CMGR Write command with empty parameter (AT+CMGR=)")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR=", ".*CMS ERROR.*"))

        test.log.step("4.6) Check CMGR Read command (AT+CMGR?).")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR?", ".*CMS ERROR.*"))

        test.log.step("4.7) Check CMGR Exec command (AT+CMGR).")
        test.expect(test.dut.at1.send_and_verify("AT+CMGR", ".*CMS ERROR.*"))

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_sms_center_address(test.dut))
        test.expect(dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0"))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))

    def execute_steps_3_3_to_3_10(test, csdh_value, skip_sms_index=0):
        test.log.step("3.3) Read message with status UNSENT in Text mode (AT+CMGR=<index of "
                      "unsent SMS>).")
        test.expect(dstl_select_sms_message_format(test.dut))
        dstl_read_sms_message(test.dut, test.indexes_list[0])
        test.expect(re.search(test.prepare_cmgr_text_regex(
            "STO UNSENT", 15, csdh_value,"STO UNSENT test"), test.dut.at1.last_response))

        test.log.step("3.4) Read message with status SENT in Text mode (AT+CMGR=<index of a sent "
                      "SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[1])
        test.expect(re.search(test.prepare_cmgr_text_regex(
            "STO SENT", 13, csdh_value, "STO SENT test"), test.dut.at1.last_response))

        test.log.step("3.5) Read message with status UNREAD in Text mode (AT+CMGR=<index of "
                      "unread SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[2] + skip_sms_index)
        test.expect(re.search(test.prepare_cmgr_text_regex(
            "REC UNREAD", 15, csdh_value,"REC UNREAD test"),test.dut.at1.last_response))

        test.log.step("3.6) Read messages with status READ in Text mode - 2 messages: previously "
                      "read and saved with read status (AT+CMGR=<index of read SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[2] + skip_sms_index)
        test.expect(re.search(test.prepare_cmgr_text_regex(
            "REC READ", 15, csdh_value,"REC UNREAD test"),test.dut.at1.last_response))
        dstl_read_sms_message(test.dut, test.indexes_list[6])
        test.expect(re.search(test.prepare_cmgr_text_regex(
            "REC READ", 13, csdh_value,"REC READ test"),test.dut.at1.last_response))

        test.log.step("3.7) Read message with status UNSENT in PDU mode (AT+CMGR=<index of "
                      "unsent SMS>).")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        dstl_read_sms_message(test.dut, test.indexes_list[0])
        test.expect(re.search(test.prepare_cmgr_pdu_regex(
            test.status[0],test.pdu_messages[test.status[0]]),test.dut.at1.last_response))

        test.log.step("3.8) Read message with status SENT in PDU mode (AT+CMGR=<index of a sent "
                      "SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[1])
        test.expect(re.search(test.prepare_cmgr_pdu_regex(
            test.status[1],test.pdu_messages[test.status[1]]),test.dut.at1.last_response))

        test.log.step("3.9) Read message with status UNREAD in PDU mode (AT+CMGR=<index of unread "
                      "SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[3] + skip_sms_index)
        test.expect(re.search(test.prepare_cmgr_pdu_regex(
            test.status[3 + skip_sms_index], test.pdu_messages[test.status[3]]),
            test.dut.at1.last_response))

        test.log.step("3.10) Read messages with status READ in PDU mode - 2 messages: previously "
                      "read and saved with read status (AT+CMGR=<index of read SMS>).")
        dstl_read_sms_message(test.dut, test.indexes_list[6])
        test.expect(re.search(test.prepare_cmgr_pdu_regex(
            test.status[6], test.pdu_messages[test.status[6]]), test.dut.at1.last_response))
        dstl_read_sms_message(test.dut, test.indexes_list[3] + skip_sms_index)
        test.expect(re.search(test.prepare_cmgr_pdu_regex(
            test.status[6], test.pdu_messages[test.status[3 + skip_sms_index]]),
            test.dut.at1.last_response))

    def prepare_cmgr_text_regex(test, status, length, csdh, text):
        scts_regex = "94\/05\/06,22:10:00\+08"
        if status == "STO UNSENT" or status == "STO SENT":
            if csdh == 1:
                return r"\+CMGR: \"{}\",\"\{}\",,145,17,0,0,167,\"\{}\",145," \
                       r"{}[\n\r]+{}[\n\r]" \
                       r"+.*OK".format(status, test.int_voice_nr, test.sca_int, length, text)
            elif csdh == 0:
                return r"\+CMGR: \"{}\",\"\{}\",[\n\r]+{}[\n\r]+.*OK".format(
                    status, test.int_voice_nr, text)
        elif status == "REC UNREAD" or status == "REC READ":
            if csdh == 1:
                return r"\+CMGR: \"{}\",\"\{}\",,\"{}\",145,24,0,0,\"\{}\",145," \
                       r"{}[\n\r]+{}[\n\r]+.*OK".format(status, test.int_voice_nr, scts_regex,
                                                        test.sca_int, length, text)
            elif csdh == 0:
                return r"\+CMGR: \"{}\",\"\{}\",,\"{}\"[\n\r]+{}[\n\r]+OK".format(
                    status, test.int_voice_nr, scts_regex, text)

    def prepare_cmgr_pdu_regex(test, sms_status, sms_message):
        if sms_status == "STO UNSENT":
            status_num = 2
        elif sms_status == "STO SENT":
            status_num = 3
        elif sms_status == "REC UNREAD":
            status_num = 0
        elif sms_status == "REC READ":
            status_num = 1
        regex = r".*\+CMGR: {},,{}[\n\r]+.*{}[\n\r]+OK.*".format(
            status_num, dstl_calculate_pdu_length(sms_message), sms_message)
        return regex


if "__main__" == __name__:
    unicorn.main()
