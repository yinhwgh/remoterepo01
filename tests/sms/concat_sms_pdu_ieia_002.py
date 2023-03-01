#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0105232.002, TC0105233.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0105232.002 concatSmsPduIeia8bit / TC0105233.002 concatSmsPduIeia16bit

    Purpose of this TC is to check saving, reading and sending concatenated messages in PDU mode.
    Sequence number of concatenated SMS , maximum number of all segments ,
    Information Element Identifier octet and Reference number to identify all segments must be checked in this TC.

    Precondition: One module logged on to the network. Provider supports concatenated short messages.

    1. Set PDU mode (at+cmgf=0).
    2. Save two concatenated messages with IEIa 8-bit in PDU (at+cmgw).
        for 8bit:
            at+cmgw=23
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003050201 + 62B219
            at+cmgw=23
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003050202 + 68351B
        for 16bit:
            at+cmgw=25
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70C + 060804000A0201 + 31D98C06
            at+cmgw=25
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70C + 060804000A0202 + 35DB0D07
    3. Read saved messages (at+cmgr, at+cmgl).
    4. Set text mode (at+cmgf=1)
    5. Read saved messages (at+cmgr, at+cmgl, at^scmr, at^scml).
    6. Send saved messages (at+cmss).
    7. Set PDU mode (at+cmgf=0) and Send three concatenated messages with IEIa 8-bit in PDU (at+cmgs).
         for 8bit:
            at+cmgs=23
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090301 + C2E231
            at+cmgs=23
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090302 + C86533
            at+cmgs=23
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090303 + CEE834
        for 16bit:
            at+cmgs=24
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0301 + 61F118
            at+cmgs=24
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0302 + E4B219
            at+cmgs=24
            [SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0303 + 67741A
    8. Set Pdu mode (at+cmgf=0) and read received messages (at+cmgr, at+cmgl).
    9. Set text mode (at+cmgf=1) and read received messages (at+cmgr, at+cmgl, at^scmr, at^scml).
    """

    sms_timeout = 360
    list_dict_saved_messages_8bit = [{"command": "CMGW", "concat": "0000A70A", "udh_part": "050003050201",
                                      "content": "62B219", "length": "3", "text": "123",
                                      "seq": "1", "max": "2", "ieia": "8", "ref": "5"},
                                     {"command": "CMGW", "concat": "0000A70A", "udh_part": "050003050202",
                                      "content": "68351B", "length": "3", "text": "456",
                                      "seq": "2", "max": "2", "ieia": "8", "ref": "5"}]
    list_dict_sent_messages_8bit = [{"command": "CMGS", "concat": "0000A70A", "udh_part": "050003090301",
                                     "content": "C2E231", "length": "3", "text": "abc",
                                     "seq": "1", "max": "3", "ieia": "8", "ref": "9"},
                                    {"command": "CMGS", "concat": "0000A70A", "udh_part": "050003090302",
                                     "content": "C86533", "length": "3", "text": "def",
                                     "seq": "2", "max": "3", "ieia": "8", "ref": "9"},
                                    {"command": "CMGS", "concat": "0000A70A", "udh_part": "050003090303",
                                     "content": "CEE834", "length": "3", "text": "ghi",
                                     "seq": "3", "max": "3", "ieia": "8", "ref": "9"}]
    list_dict_saved_messages_16bit = [{"command": "CMGW", "concat": "0000A70C", "udh_part": "060804000A0201",
                                       "content": "31D98C06", "length": "4", "text": "1234",
                                       "seq": "1", "max": "2", "ieia": "16", "ref": "10"},
                                      {"command": "CMGW", "concat": "0000A70C", "udh_part": "060804000A0202",
                                       "content": "35DB0D07", "length": "4", "text": "5678",
                                       "seq": "2", "max": "2", "ieia": "16", "ref": "10"}]
    list_dict_sent_messages_16bit = [{"command": "CMGS", "concat": "0000A70B", "udh_part": "060804002D0301",
                                      "content": "61F118", "length": "3", "text": "abc",
                                      "seq": "1", "max": "3", "ieia": "16", "ref": "45"},
                                     {"command": "CMGS", "concat": "0000A70B", "udh_part": "060804002D0302",
                                      "content": "E4B219", "length": "3", "text": "def",
                                      "seq": "2", "max": "3", "ieia": "16", "ref": "45"},
                                     {"command": "CMGS", "concat": "0000A70B", "udh_part": "060804002D0303",
                                      "content": "67741A", "length": "3", "text": "ghi",
                                      "seq": "3", "max": "3", "ieia": "16", "ref": "45"}]
    list_index_cmgw = []
    list_index_cmti = []

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        if test.sms_coding == "8bit":
            test.list_dict_saved_messages = test.list_dict_saved_messages_8bit
            test.list_dict_sent_messages = test.list_dict_sent_messages_8bit
            test.tc_name = "TC0105232.002 concatSmsPduIeia8bit"
            test.step_2_details = "at+cmgw=23[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003050201 + 62B219[\n]" \
                                  "at+cmgw=23[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003050202 + 68351B"
            test.step_7_details = "at+cmgs=23[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090301 + C2E231[\n]" \
                                  "at+cmgs=23[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090302 + C86533[\n]" \
                                  "at+cmgs=23[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70A + 050003090303 + CEE834"
        else:
            test.list_dict_saved_messages = test.list_dict_saved_messages_16bit
            test.list_dict_sent_messages = test.list_dict_sent_messages_16bit
            test.tc_name = "TC0105233.002 concatSmsPduIeia16bit"
            test.step_2_details = "at+cmgw=25[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70C + 060804000A0201 + 31D98C06[\n]" \
                                  "at+cmgw=25[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70C + 060804000A0202 + 35DB0D07"
            test.step_7_details = "at+cmgs=24[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0301 + 61F118[\n]" \
                                  "at+cmgs=24[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0302 + E4B219[\n]" \
                                  "at+cmgs=24[\n]" \
                                  "[SCA_PDU] + 5100 + [PDU_int_number] + 0000A70B + 060804002D0303 + 67741A"
        test.list_dict_all_delivered = test.list_dict_saved_messages + test.list_dict_sent_messages

    def run(test):
        test.log.h2("Starting TP: {}".format(test.tc_name))
        test.log.step("Step 1. Set PDU mode (at+cmgf=0).")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))

        test.log.step("Step 2. Save two concatenated messages with IEIa {} in PDU (at+cmgw).[\n]{}"
                      .format(test.sms_coding, test.step_2_details))
        test.save_or_send_sms_pdu(test.list_dict_saved_messages)

        test.log.step("Step 3. Read saved messages (at+cmgr, at+cmgl).")
        test.read_messages(test.list_index_cmgw, test.list_dict_saved_messages, "AT+CMGR", "PDU")
        test.list_messages(test.list_dict_saved_messages, "AT+CMGL=4", "PDU")

        test.log.step("Step 4. Set text mode (at+cmgf=1)")
        test.expect(dstl_select_sms_message_format(test.dut))

        test.log.step("Step 5. Read saved messages (at+cmgr, at+cmgl, at^scmr, at^scml).")
        test.read_messages(test.list_index_cmgw, test.list_dict_saved_messages, "AT+CMGR", "Text")
        test.list_messages(test.list_dict_saved_messages, "AT+CMGL=\"ALL\"", "Text")
        test.read_messages(test.list_index_cmgw, test.list_dict_saved_messages, "AT^SCMR", "Text")
        test.list_messages(test.list_dict_saved_messages, "AT^SCML=\"ALL\"", "Text")

        test.log.step("Step 6. Send saved messages (at+cmss).")
        test.send_sms_from_memory(test.list_index_cmgw)

        test.log.step("Step 7. Set PDU mode (at+cmgf=0) and "
                      "Send three concatenated messages with IEIa {} in PDU (at+cmgs).[\n]{}"
                      .format(test.sms_coding, test.step_7_details))
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.save_or_send_sms_pdu(test.list_dict_sent_messages)

        test.log.step("Step 8. Set Pdu mode (at+cmgf=0) and read received messages (at+cmgr, at+cmgl)")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.read_messages(test.list_index_cmti, test.list_dict_all_delivered, "AT+CMGR", "PDU")
        test.list_messages(test.list_dict_all_delivered, "AT+CMGL=4", "PDU")

        test.log.step("Step 9. Set text mode (at+cmgf=1) and read received messages "
                      "(at+cmgr, at+cmgl, at^scmr, at^scml).")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.read_messages(test.list_index_cmti, test.list_dict_all_delivered, "AT+CMGR", "Text")
        test.list_messages(test.list_dict_all_delivered, "AT+CMGL=\"ALL\"", "Text")
        test.read_messages(test.list_index_cmti, test.list_dict_all_delivered, "AT^SCMR", "Text")
        test.list_messages(test.list_dict_all_delivered, "AT^SCML=\"ALL\"", "Text")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def get_sms_index(test, regex, expected):
        response_content = test.expect(re.search(regex, test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for {} is: {}".format(expected, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(expected))

    def save_or_send_sms_pdu(test, list_dict):
        list_index = []
        for item in list_dict:
            sms_pdu = "{0}5100{1}{2}{3}{4}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, item["concat"],
                                                   item["udh_part"], item["content"])
            test.log.info("SMS PDU: {}".format(sms_pdu))
            test.dut.at1.send_and_verify("AT+{}={}".format(item["command"], test.pdu_length(sms_pdu)), expect=">")
            test.expect(test.dut.at1.send_and_verify(sms_pdu, end="\u001A", expect=".*{}:.*OK.*"
                                                     .format(item["command"]), timeout=test.sms_timeout))
            if "CMGW" in item["command"]:
                list_index = test.list_index_cmgw.append(test.get_sms_index(r".*CMGW:\s*(\d{1,3})", "CMGW"))
            else:
                test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
                list_index = test.list_index_cmti.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))

    def list_messages(test, message_list, command, sms_format):
        test.expect(test.dut.at1.send_and_verify("{}".format(command), ".*OK.*"))
        for item in message_list:
            if message_list == test.list_dict_saved_messages:
                msg_index = test.list_index_cmgw[message_list.index(item)]
            else:
                msg_index = test.list_index_cmti[message_list.index(item)]
            if sms_format == "Text":
                if message_list == test.list_dict_saved_messages:
                    status = "STO UNSENT"
                    scts = ""
                else:
                    status = "REC READ"
                    scts = "\".*\""
                if "CMGL" in command:
                    regex_text = ".*{0}: {1},\"{2}\",\"\{3}\",,{4},145,{5}\s*[\n\r]{6}.*".format(
                        command[3:7], msg_index, status, test.dut.sim.int_voice_nr, scts, item["length"], item["text"])
                else:
                    regex_text = ".*{0}: {1},\"{2}\",\"\{3}\",,{4},145,{5},{6},{7},{8},{9}\s*[\n\r]{10}.*".format(
                        command[3:7], msg_index, status, test.dut.sim.int_voice_nr, scts, item["length"],
                        item["seq"], item["max"], item["ieia"], item["ref"], item["text"])
                test.log.info("Expected REGEX: {}".format(regex_text))
                test.expect(re.search(regex_text, test.dut.at1.last_response))
            else:
                if message_list == test.list_dict_saved_messages:
                    status = "2"
                    sms_pdu = "{0}5100{1}{2}{3}{4}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, item["concat"],
                                                          item["udh_part"], item["content"])
                    length = test.pdu_length(sms_pdu)
                else:
                    status = "1"
                    sms_pdu = "{0}.*{1}.*{2}{3}".format(test.dut.sim.sca_pdu[:4], test.dut.sim.pdu,
                                                        item["udh_part"], item["content"])
                    length = "\\d{1,2}"
                regex_pdu = r".*{0}: {1},{2},,{3}\s*[\n\r].*{4}.*\s*[\n\r].*".format(command[3:7], msg_index, status,
                                                                                     length, sms_pdu)
                test.log.info("Expected REGEX: {}".format(regex_pdu))
                test.expect(re.search(regex_pdu, test.dut.at1.last_response))

    def read_messages(test, index_list, message_list, command, sms_format):
        for msg_index in index_list:
            test.expect(test.dut.at1.send_and_verify("{}={}".format(command, msg_index), ".*OK.*"))
            item = message_list[index_list.index(msg_index)]
            if sms_format == "Text":
                if message_list == test.list_dict_saved_messages:
                    status = "STO UNSENT"
                else:
                    status = "REC READ"
                if "CMGR" in command:
                    regex = ".*{0}: \"{1}\",\"\{2}\",.*,{3}\s*[\n\r]{4}.*".format(
                        command[3:7], status, test.dut.sim.int_voice_nr, item["length"], item["text"])
                else:
                    regex = ".*{0}: \"{1}\",\"\{2}\",.*,{3},{4},{5},{6},{7}\s*[\n\r]{8}.*".format(
                        command[3:7], status, test.dut.sim.int_voice_nr, item["length"],
                        item["seq"], item["max"], item["ieia"], item["ref"], item["text"])
                test.log.info("Expected REGEX: {}".format(regex))
                test.expect(re.search(regex, test.dut.at1.last_response))
            else:
                if message_list == test.list_dict_saved_messages:
                    status = "2"
                    sms_pdu = "{0}5100{1}{2}{3}{4}".format(test.dut.sim.sca_pdu, test.dut.sim.pdu, item["concat"],
                                                          item["udh_part"], item["content"])
                    regex_pdu = r".*{0}: {1},,{2}\s*[\n\r]{3}\s*[\n\r].*".format(command[3:7], status,
                                                                                 test.pdu_length(sms_pdu), sms_pdu)
                else:
                    status = "0"
                    sms_pdu = re.search(".*[\n\r].*[\n\r]\s*(.*)\s*[\n\r].*", test.dut.at1.last_response).group(1)
                    regex_pdu = r".*{0}: {1},,{2}\s*[\n\r].*{3}.*\s*[\n\r].*".format(command[3:7], status,
                                                                                     test.pdu_length(sms_pdu), sms_pdu)
                test.log.info("Expected REGEX: {}".format(regex_pdu))
                test.expect(re.search(regex_pdu, test.dut.at1.last_response))

    def pdu_length(test, pdu):
        return (len(pdu) - ((int(pdu[1]) + 1) * 2)) // 2

    def send_sms_from_memory(test, index_list):
        for item in index_list:
            test.expect(dstl_send_sms_message_from_memory(test.dut, item))
            test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
            test.list_index_cmti.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))


if "__main__" == __name__:
    unicorn.main()