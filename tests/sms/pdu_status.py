# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0011217.001

import re
import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.character_set import dstl_set_character_set
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_show_sms_text_mode_parameters
from dstl.sms.delete_sms import dstl_delete_all_sms_messages, dstl_delete_sms_message_from_index
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_message_service import dstl_set_message_service
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0011217.001 PDUStatus

    Test if SMS with different statuses can be write, read, send in PDU mode.

    1) write SMSes with different statuses
    2) send written SMSes to second module and check status of received SMSes on REMOTE
    3) read all written SMSes without changing statuses (at^smgl, at^smgr)
    4) test invalid statuses entered via at^smgl, at^smgr
    5) read all written SMSes with changing statuses (at+cmgl, at+cmgr)
    6) test invalid statuses entered via at+cmgl, at+cmgr

    All steps (1-6) will be perform for all supported storages and coding
    """

    SMS_TIMEOUT = 120
    CODINGS = ["7bit", "8bit", "UCS2"]
    MEMORY = ["SM", "ME", "MT"]
    MESSAGES_7BIT_DUT = [{"status_text": "REC UNREAD", "status_pdu": "0", "msg_type": "04",
                          "coding": "00", "time_stamp": "99309251619580", "content_length": "0C",
                          "pdu_content": "D3E61434A587E9F5390806", "status_pdu_changed": "1"},
                         {"status_text": "REC READ", "status_pdu": "1", "msg_type": "04",
                          "coding": "00", "time_stamp": "99309251619580", "content_length": "0C",
                          "pdu_content": "D3E61434A587E9F5392806"},
                         {"status_text": "STO UNSENT", "status_pdu": "2", "msg_type": "1100",
                          "coding": "00", "time_stamp": "FF", "content_length": "0C",
                          "pdu_content": "D3E61434A587E9F5394806"},
                         {"status_text": "STO SENT", "status_pdu": "3", "msg_type": "1100",
                          "coding": "00", "time_stamp": "FF", "content_length": "0C",
                          "pdu_content": "D3E61434A587E9F5396806"},
                         {"status_text": "ALL", "status_pdu": "4", "msg_type": "", "coding": "00",
                          "time_stamp": "", "content_length": "", "pdu_content": ""}]
    MESSAGES_7BIT_RMT = [{"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_7BIT_DUT[2]["pdu_content"]},
                         {"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_7BIT_DUT[3]["pdu_content"]}]
    MESSAGES_8BIT_DUT = [{"status_text": "REC UNREAD", "status_pdu": "0", "msg_type": "04",
                          "coding": "04", "time_stamp": "99309251619580", "content_length": "0C",
                          "pdu_content": "534D53205374617475732030", "status_pdu_changed": "1"},
                         {"status_text": "REC READ", "status_pdu": "1", "msg_type": "04",
                          "coding": "04", "time_stamp": "99309251619580", "content_length": "0C",
                          "pdu_content": "534D53205374617475732031"},
                         {"status_text": "STO UNSENT", "status_pdu": "2", "msg_type": "1100",
                          "coding": "04", "time_stamp": "FF", "content_length": "0C",
                          "pdu_content": "534D53205374617475732032"},
                         {"status_text": "STO SENT", "status_pdu": "3", "msg_type": "1100",
                          "coding": "04", "time_stamp": "FF", "content_length": "0C",
                          "pdu_content": "534D53205374617475732033"},
                         {"status_text": "ALL", "status_pdu": "4", "msg_type": "", "coding": "04",
                          "time_stamp": "", "content_length": "", "pdu_content": ""}]
    MESSAGES_8BIT_RMT = [{"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_8BIT_DUT[2]["pdu_content"]},
                         {"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_8BIT_DUT[3]["pdu_content"]}]
    MESSAGES_UCS2_DUT = [{"status_text": "REC UNREAD", "status_pdu": "0", "msg_type": "04",
                          "coding": "08", "time_stamp": "99309251619580", "content_length": "18",
                          "pdu_content": "0053004D0053002000530074006100740075007300200030",
                          "status_pdu_changed": "1"},
                         {"status_text": "REC READ", "status_pdu": "1", "msg_type": "04",
                          "coding": "08", "time_stamp": "99309251619580", "content_length": "18",
                          "pdu_content": "0053004D0053002000530074006100740075007300200031"},
                         {"status_text": "STO UNSENT", "status_pdu": "2", "msg_type": "1100",
                          "coding": "08", "time_stamp": "FF", "content_length": "18",
                          "pdu_content": "0053004D0053002000530074006100740075007300200032"},
                         {"status_text": "STO SENT", "status_pdu": "3", "msg_type": "1100",
                          "coding": "08", "time_stamp": "FF", "content_length": "18",
                          "pdu_content": "0053004D0053002000530074006100740075007300200033"},
                         {"status_text": "ALL", "status_pdu": "4", "msg_type": "", "coding": "08",
                          "time_stamp": "", "content_length": "", "pdu_content": ""}]
    MESSAGES_UCS2_RMT = [{"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_UCS2_DUT[2]["pdu_content"]},
                         {"status_text": "REC UNREAD", "status_pdu": "0",
                          "pdu_content": MESSAGES_UCS2_DUT[3]["pdu_content"]}]
    list_index_cmgw = []
    list_index_cmti = []
    INVALID_STATUSES_LIST_CMD = ['""', '"REC"', 5, 50000]
    INVALID_STATUSES_READ_CMD = ['A', '-1', '\"\"']

    def setup(test):
        test.prepare_module(test.dut, "===== PREPARING DUT =====")
        test.prepare_module(test.r1, "===== PREPARING REMOTE =====")

    def run(test):
        test.log.info("All steps (1-6) will be perform for all supported storages and coding")
        for coding in test.CODINGS:
            for mem in test.MEMORY:
                test.log.info(f"=====     =====     =====     =====     =====     =====     =====")
                test.log.info(f"===== REPETITION for coding: {coding} and for memory: {mem} =====")
                test.log.info(f"=====     =====     =====     =====     =====     =====     =====")
                test.expect(dstl_set_preferred_sms_memory(test.dut, f"{mem}"))
                if coding == "7bit":
                    msg_list_dict_dut = test.MESSAGES_7BIT_DUT
                    msg_list_dict_rmt = test.MESSAGES_7BIT_RMT
                elif coding == "8bit":
                    msg_list_dict_dut = test.MESSAGES_8BIT_DUT
                    msg_list_dict_rmt = test.MESSAGES_8BIT_RMT
                else:
                    msg_list_dict_dut = test.MESSAGES_UCS2_DUT
                    msg_list_dict_rmt = test.MESSAGES_UCS2_RMT

                test.log.step("Step 1) write SMSes with different statuses")
                test.write_sms_with_status(
                    msg_list_dict_dut[0], test.prepare_pdu(msg_list_dict_dut[0]))
                test.write_sms_with_status(
                    msg_list_dict_dut[1], test.prepare_pdu(msg_list_dict_dut[1]))
                test.write_sms_with_status(
                    msg_list_dict_dut[2], test.prepare_pdu(msg_list_dict_dut[2]))
                test.write_sms_with_status(
                    msg_list_dict_dut[3], test.prepare_pdu(msg_list_dict_dut[3]))
                test.write_sms_with_status(
                    msg_list_dict_dut[4], test.prepare_pdu(msg_list_dict_dut[4]))

                test.log.step("Step 2) send written SMSes to second module "
                              "and check status of received SMSes on REMOTE")
                test.log.info("***** Try to SEND SMS with all statuses \n "
                              "SMSes only with statuses STO UNSENT and STO SENT can be sent *****")
                test.send_sms_from_memory(test.list_index_cmgw)
                test.log.info("===== LIST MESSAGES ON RMT MODULE =====")
                test.check_list_sms_command(
                    test.r1, "SMGL", 4, test.list_index_cmti, msg_list_dict_rmt)

                test.log.step("Step 3) read all written SMSes without changing statuses "
                              "(at^smgl, at^smgr)")
                test.write_sms_with_status_one_more_time(
                    test.list_index_cmgw[2], msg_list_dict_dut[2])

                test.log.info("===== LIST MESSAGES ON DUT MODULE WITHOUT STATUS CHANGE =====")
                test.log.info("***** List messages with status REC UNREAD *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 0, test.list_index_cmgw[0], msg_list_dict_dut[0])
                test.log.info("***** List messages with status REC READ *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 1, test.list_index_cmgw[1], msg_list_dict_dut[1])
                test.log.info("***** List messages with status STO UNSENT *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 2, test.list_index_cmgw[2], msg_list_dict_dut[2])
                test.log.info("***** List messages with status STO SENT *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 3, test.list_index_cmgw[3], msg_list_dict_dut[3])
                test.log.info("***** List messages with status ALL *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 4, test.list_index_cmgw[:4], msg_list_dict_dut)

                test.log.info("===== READ MESSAGES ON DUT MODULE WITHOUT STATUS CHANGE =====")
                test.read_sms_in_memory(test.dut, "SMGR", test.list_index_cmgw[:4], msg_list_dict_dut)
                test.log.info("***** Check, if Status REC UNREAD still exist in memory *****")
                test.check_list_sms_command(
                    test.dut, "SMGL", 0, test.list_index_cmgw[0], msg_list_dict_dut[0])

                test.log.step("Step 4) test invalid statuses entered via at^smgl, at^smgr")
                test.check_invalid_syntax("AT^SMGL", test.INVALID_STATUSES_LIST_CMD, ".*CMS ERROR.*")
                test.check_invalid_syntax("AT^SMGR", test.INVALID_STATUSES_READ_CMD, ".*CMS ERROR.*")
                test.check_invalid_syntax("AT+CMGR", [256], ".*CMS ERROR: invalid memory index.*")
                test.check_invalid_syntax("AT^SMGR", [50000], ".*CMS ERROR: invalid parameter.*")

                test.log.step("Step 5) read all written SMSes with changing statuses "
                              "(at+cmgl, at+cmgr)")

                test.log.info("===== LIST MESSAGES ON DUT MODULE WITH STATUS CHANGE =====")
                test.log.info("***** List messages with status REC UNREAD *****")
                test.check_list_sms_command(
                    test.dut, "CMGL", 0, test.list_index_cmgw[0], msg_list_dict_dut[0])
                test.log.info("***** List messages with status REC READ *****")
                test.check_list_sms_command(
                    test.dut, "CMGL", 1, test.list_index_cmgw[1], msg_list_dict_dut[1])
                test.log.info("***** List messages with status STO UNSENT *****")
                test.check_list_sms_command(
                    test.dut, "CMGL", 2, test.list_index_cmgw[2], msg_list_dict_dut[2])
                test.log.info("***** List messages with status STO SENT *****")
                test.check_list_sms_command(
                    test.dut, "CMGL", 3, test.list_index_cmgw[3], msg_list_dict_dut[3])
                test.write_sms_with_status_one_more_time(
                    test.list_index_cmgw[0], msg_list_dict_dut[0])
                test.log.info("***** List messages with status ALL *****")
                test.check_list_sms_command(
                    test.dut, "CMGL", 4, test.list_index_cmgw[:4], msg_list_dict_dut)
                test.log.info("***** Check, if Status REC UNREAD has changed to REC READ *****")
                test.read_message_with_changed_status(msg_list_dict_dut[0])

                test.write_sms_with_status_one_more_time(test.list_index_cmgw[0], msg_list_dict_dut[0])
                test.log.info("===== READ WRITTEN SMSes ON DUT MODULE WITH CHANGING STATUS =====")
                test.read_sms_in_memory(
                    test.dut, "CMGR", test.list_index_cmgw[:4], msg_list_dict_dut)
                test.log.info("***** Check, if Status REC UNREAD has changed to REC READ *****")
                test.read_message_with_changed_status(msg_list_dict_dut[0])

                test.log.step("Step 6) test invalid statuses entered via at+cmgl, at+cmgr")
                test.check_invalid_syntax("AT+CMGL", test.INVALID_STATUSES_LIST_CMD, ".*CMS ERROR.*")
                test.check_invalid_syntax("AT+CMGR", test.INVALID_STATUSES_READ_CMD, ".*CMS ERROR.*")
                test.check_invalid_syntax("AT+CMGR", [256], ".*CMS ERROR: invalid memory index.*")
                test.check_invalid_syntax("AT+CMGR", [50000], ".*CMS ERROR: invalid parameter.*")

                test.log.info("===== Delete all messages on both module =====")
                test.delete_sms_from_memory(test.dut, ["SM", "ME"])
                test.delete_sms_from_memory(test.r1, ["SM", "ME"])
                test.list_index_cmgw.clear()
                test.list_index_cmti.clear()

    def cleanup(test):
        pass

    def prepare_module(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_set_error_message_format(module))
        test.expect(dstl_set_character_set(module, 'GSM'))
        test.expect(dstl_set_message_service(module))
        test.expect(dstl_configure_sms_event_reporting(module, mode="2", mt="1"))
        test.expect(dstl_show_sms_text_mode_parameters(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.delete_sms_from_memory(module, ["SM", "ME"])
        test.expect(dstl_select_sms_message_format(module, 'PDU'))

    def delete_sms_from_memory(test, module, memory):
        for mem in memory:
            test.log.info(f"Delete SMS from memory: {mem}")
            test.expect(dstl_set_preferred_sms_memory(module, mem))
            test.expect(dstl_delete_all_sms_messages(module))

    def prepare_pdu(test, messages_list_dict):
        pdu_message = f'{test.dut.sim.sca_pdu}{messages_list_dict["msg_type"]}{test.r1.sim.pdu}' \
                      f'00{messages_list_dict["coding"]}{messages_list_dict["time_stamp"]}' \
                      f'{messages_list_dict["content_length"]}{messages_list_dict["pdu_content"]}'
        return pdu_message

    def write_sms_with_status(test, list_dict, pdu_msg):
        test.log.info(f'===== Write SMS with Status: {list_dict["status_text"]} =====')
        if list_dict["status_text"] == "ALL":
            test.expect(dstl_write_sms_to_memory(test.dut, stat=list_dict["status_pdu"],
                                                 sms_format="PDU", exp_resp=".*CMS ERROR:.*"))
        else:
            index = test.expect(dstl_write_sms_to_memory(test.dut, return_index=True,
                                stat=list_dict["status_pdu"], sms_format="PDU", pdu=pdu_msg))
            return test.list_index_cmgw.append(index[0])

    def write_sms_with_status_one_more_time(test, index, list_dict):
        test.log.info(f'***** Write {list_dict["status_text"]} message one more time *****')
        test.expect(dstl_delete_sms_message_from_index(test.dut, index))
        test.write_sms_with_status(list_dict, test.prepare_pdu(list_dict))

    def send_sms_from_memory(test, index_list):
        test.log.info(f"===== Send messages from memory with indexes: {index_list} =====")
        for item in index_list:
            if item == index_list[0] or item == index_list[1]:
                expected_resp = ".*CMS ERROR.*"
            else:
                expected_resp = ".*OK.*"
            if "ERROR" in expected_resp:
                test.expect(
                    dstl_send_sms_message_from_memory(test.dut, item, exp_resp=expected_resp))
            else:
                test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                if test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.SMS_TIMEOUT)):
                    cmti = test.expect(re.search(r".*CMTI.*,\s*(\d{1,3})", test.r1.at1.last_response))
                    if cmti:
                        test.log.info(f"SMS index for CMTI is: {cmti[1]}")
                        if item == index_list[2]:
                            idx = 1
                        else:
                            idx = 2
                        test.expect(dstl_get_sms_count_from_memory(test.r1)[0] == idx)
                        test.list_index_cmti.append(cmti[1])
                    else:
                        return test.log.error("Fail to get value of CMTI")
                else:
                    test.log.info("Message NOT delivered")
        return test.list_index_cmti

    def check_list_sms_command(test, module, command, status, index_list, content_list):
        if command == "SMGL":
            test.expect(dstl_list_sms_messages_from_preferred_memory(module, status,
                                                                     change_status=False))
        else:
            test.expect(dstl_list_sms_messages_from_preferred_memory(module, status))
        if status == 4:
            for item in index_list:
                regex = fr'.*{command}: {item},' \
                        fr'{content_list[index_list.index(item)]["status_pdu"]},,{"[0-9]+"}\s*' \
                        fr'.*{content_list[index_list.index(item)]["pdu_content"]}\s*.*'
                test.log.info(f"Expected REGEX: {regex}")
                test.expect(re.search(regex, module.at1.last_response))
        else:
            regex = fr'.*{command}: {index_list},{content_list["status_pdu"]},,{"[0-9]+"}\s*' \
                    fr'.*{content_list["pdu_content"]}\s*.*'
            test.log.info(f"Expected REGEX: {regex}")
            test.expect(re.search(regex, module.at1.last_response))

    def read_sms_in_memory(test, module, command, index_list, content_list):
        for item in index_list:
            test.log.info(f'***** Read messages with status: '
                          f'{content_list[index_list.index(item)]["status_text"]} *****')
            if command == "SMGR":
                test.expect(dstl_read_sms_message(module, item, change_status=False))
            else:
                test.expect(dstl_read_sms_message(module, item))

            regex = fr'.*{command}: {content_list[index_list.index(item)]["status_pdu"]},,' \
                    fr'{"[0-9]+"}\s*.*{content_list[index_list.index(item)]["pdu_content"]}\s*.*'
            test.log.info(f"Expected REGEX: {regex}")
            test.expect(re.search(regex, module.at1.last_response))

    def read_message_with_changed_status(test, content_list):
        test.expect(dstl_read_sms_message(test.dut, test.list_index_cmgw[0]))
        regex = fr'.*{"CMGR"}: {content_list["status_pdu_changed"]},,{"[0-9]+"}\s*' \
                fr'.*{content_list["pdu_content"]}\s*.*'
        test.log.info(f"Expected REGEX: {regex}")
        test.expect(re.search(regex, test.dut.at1.last_response))

    def check_invalid_syntax(test, command, invalid_values_list, exp_resp):
        for invalid_status in invalid_values_list:
            test.expect(test.dut.at1.send_and_verify(f"{command}={invalid_status}", exp_resp))


if "__main__" == __name__:
    unicorn.main()