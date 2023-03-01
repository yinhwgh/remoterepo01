#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095081.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.auxiliary_sms_functions import _convert_number_to_ucs2
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """ TC0095081.002 AtSmsCrLfConcatSms

   The module should be able to send SMS with carriage return (CR) and line feed (LF) characters.

    Precondition: Module logged on to the network. SMS Service Centre address is set.

    Module saves and sends concatenated message with carriage return (CR) and line feed (LF) characters.

    1. save messages with at^scmw - create three segments - the first segment contains carriage return (CR) character,
    the second segment contains line feed (LF) character and the last segment contains both characters (CR and LF).
    2. send each message segment from memory with at+cmss,
    3. send each message directly with at^scms - also three segments, the same as in step 1.
    4. repeat saving and sending for every character set supported by at+cscs command (GSM, UCS2, etc.)

    - For GSM character set use escape character with appropriate code from GSM character table,
    - When using UCS-2 character set follow the "ETSI GSM 03.38 mapping into Unicode" rules:
       GSM     UCS-2
    LF 0x0A = 0x000A
    CR 0x0D = 0x000D
    """

    TIMEOUT_SHORT = 60
    TIMEOUT_SMS = 120
    TIMEOUT_SMS_LONG = 360
    STEPS = [{"descr": "GSM_7bit", "char_set": "GSM", "dcs": "0"},
             {"descr": "UCS2", "char_set": "UCS2", "dcs": "8"},
             {"descr": "GSM_8bit", "char_set": "GSM", "dcs": "4"}]
    SCMW_MSG_GSM = [{"seq": "1", "msg_text": "CR\u000Dend", "msg_text_read": "CR.0Dend", "ieia": "8", "ref": "250"},
                    {"seq": "2", "msg_text": "LF\u000Aend", "msg_text_read": "LF.0Aend", "ieia": "8", "ref": "250"},
                    {"seq": "3", "msg_text": "CRLF\u000D\u000Aend", "msg_text_read": "CRLF.0D.0Aend", "ieia": "8",
                     "ref": "250"}]
    SCMW_MSG_UCS2 = [{"seq": "1", "msg_text": "0031000D0031", "msg_text_read": "0031000D0031", "ieia": "8",
                      "ref": "251"},
                     {"seq": "2", "msg_text": "0031000A0031", "msg_text_read": "0031000A0031", "ieia": "8",
                      "ref": "251"},
                     {"seq": "3", "msg_text": "0031000D000A0031", "msg_text_read": "0031000D000A0031", "ieia": "8",
                      "ref": "251"}]
    SCMW_MSG_8bit = [{"seq": "1", "msg_text": "410D41", "msg_text_read": "410D41", "ieia": "8", "ref": "252"},
                     {"seq": "2", "msg_text": "410A41", "msg_text_read": "410A41", "ieia": "8", "ref": "252"},
                     {"seq": "3", "msg_text": "410D0A41", "msg_text_read": "410D0A41", "ieia": "8", "ref": "252"}]
    SCMS_MSG_GSM = [{"seq": "1", "msg_text": "CR\u000Dend", "msg_text_read": "CR.0Dend", "ieia": "16", "ref": "270"},
                    {"seq": "2", "msg_text": "LF\u000Aend", "msg_text_read": "LF.0Aend", "ieia": "16", "ref": "270"},
                    {"seq": "3", "msg_text": "CRLF\u000D\u000Aend", "msg_text_read": "CRLF.0D.0Aend", "ieia": "16",
                     "ref": "270"}]
    SCMS_MSG_UCS2 = [{"seq": "1", "msg_text": "0031000D0031", "msg_text_read": "0031000D0031", "ieia": "16",
                      "ref": "271"},
                     {"seq": "2", "msg_text": "0031000A0031", "msg_text_read": "0031000A0031", "ieia": "16",
                      "ref": "271"},
                     {"seq": "3", "msg_text": "0031000D000A0031", "msg_text_read": "0031000D000A0031", "ieia": "16",
                      "ref": "271"}]
    SCMS_MSG_8bit = [{"seq": "1", "msg_text": "410D41", "msg_text_read": "410D41", "ieia": "16", "ref": "272"},
                     {"seq": "2", "msg_text": "410A41", "msg_text_read": "410A41", "ieia": "16", "ref": "272"},
                     {"seq": "3", "msg_text": "410D0A41", "msg_text_read": "410D0A41", "ieia": "16", "ref": "272"}]
    list_index_scmw = []
    list_index_cmti_cmss = []
    list_index_cmti_scms = []

    def setup(test):
        test.prepare_module_to_test()

    def run(test):
        test.log.h2("Starting TP for TC0095081.002 AtSmsCrLfConcatSms")
        test.log.info(
            "Module saves and sends concatenated message with carriage return (CR) and line feed (LF) characters.")
        test.execute_steps_1_4(test.STEPS[0], test.SCMW_MSG_GSM, test.SCMS_MSG_GSM)
        test.execute_steps_1_4(test.STEPS[1], test.SCMW_MSG_UCS2, test.SCMS_MSG_UCS2)
        test.execute_steps_1_4(test.STEPS[2], test.SCMW_MSG_8bit, test.SCMS_MSG_8bit)

    def cleanup(test):
        test.set_dcs_via_csmp("0")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module_to_test(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_urc_dst_ifc(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=0", "OK"))
        test.DUT_NUMBER = test.dut.sim.int_voice_nr
        test.DUT_NUMBER_UCS2 = _convert_number_to_ucs2(test.dut.sim.int_voice_nr)

    def set_dcs_via_csmp(test, dcs):
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs), ".*OK.*"))

    def set_character_set(test, alphabet):
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"{}\"".format(alphabet), "OK"))

    def get_sms_index(test, regex, command):
        response_content = test.expect(re.search(regex, test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("Index for the {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of: {}".format(command))

    def write_one_concat_msg(test, content_dict, da_number):
        test.expect(test.dut.at1.send_and_verify('AT^SCMW="{}",,,{},3,{},{}'.format(
            da_number, content_dict['seq'], content_dict['ieia'], content_dict['ref']), expect='.*>.*'))
        test.expect(test.dut.at1.send_and_verify(content_dict['msg_text'], end="\u001A", expect='.*OK.*',
                                                 wait_for='.*OK.*', timeout=test.TIMEOUT_SHORT))
        test.list_index_scmw.append(test.get_sms_index(r".*SCMW:\s*(\d{1,3})", "SCMW"))
        return test.list_index_scmw

    def write_all_concat_msg(test, list_dict, da_number):
        test.log.info("===== First segment - contains carriage return (CR) character =====")
        test.write_one_concat_msg(list_dict[0], da_number)
        test.log.info("===== Second segment - contains line feed (LF) character =====")
        test.write_one_concat_msg(list_dict[1], da_number)
        test.log.info("===== Last segment - contains both characters (CR and LF) =====")
        test.write_one_concat_msg(list_dict[2], da_number)

    def send_one_concat_msg_directly(test, content_dict, da_number):
        test.expect(test.dut.at1.send_and_verify('AT^SCMS="{}",,{},3,{},{}'.format(
            da_number, content_dict['seq'], content_dict['ieia'], content_dict['ref']), expect='.*>.*'))
        test.expect(test.dut.at1.send_and_verify(content_dict['msg_text'], end="\u001A", expect='.*OK.*',
                                                 wait_for='.*OK.*', timeout=test.TIMEOUT_SMS))
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.TIMEOUT_SMS_LONG))
        test.list_index_cmti_scms.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
        return test.list_index_cmti_scms

    def send_all_concat_msg(test, list_dict, da_number):
        test.log.info("===== First segment - contains carriage return (CR) character =====")
        test.send_one_concat_msg_directly(list_dict[0], da_number)
        test.log.info("===== Second segment - contains line feed (LF) character =====")
        test.send_one_concat_msg_directly(list_dict[1], da_number)
        test.log.info("===== Last segment - contains both characters (CR and LF) =====")
        test.send_one_concat_msg_directly(list_dict[2], da_number)

    def read_one_concat_msg(test, index, status, da_number, content_dict):
        if index is not None:
            test.expect(test.dut.at1.send_and_verify('AT^SCMR={}'.format(index), ".*OK.*"))
            if da_number == test.DUT_NUMBER_UCS2:
                regex = r"\^SCMR:\s*\"{}\",\"{}\",.*,{},3,{},{}\s*[\n\r].*{}\s*".format(
                    status, da_number, content_dict["seq"], content_dict['ieia'], content_dict["ref"],
                    content_dict["msg_text_read"])
            else:
                regex = r"\^SCMR:\s*\"{}\",\"\{}\",.*,{},3,{},{}\s*[\n\r].*{}\s*".format(
                    status, da_number, content_dict["seq"], content_dict['ieia'], content_dict["ref"],
                    content_dict["msg_text_read"])
            test.log.info("Expected REGEX: {}".format(regex))
            test.expect(re.search(regex, test.dut.at1.last_response))
        else:
            test.expect(False, msg="Message not in memory")

    def read_all_concat_messages(test, index_list, da_number, content_dict):
        if index_list == test.list_index_scmw:
            status = "STO UNSENT"
        else:
            status = "REC UNREAD"
        if len(index_list) == 3:
            test.log.info("Read messages on DUT with indexes: {}".format(index_list))
            test.log.info("===== Read First segment - contains carriage return (CR) character =====")
            test.read_one_concat_msg(index_list[0], status, da_number, content_dict[0])
            test.log.info("===== Read Second segment - contains line feed (LF) character =====")
            test.read_one_concat_msg(index_list[1], status, da_number, content_dict[1])
            test.log.info("===== Read Last segment - contains both characters (CR and LF) =====")
            test.read_one_concat_msg(index_list[2], status, da_number, content_dict[2])
        else:
            test.expect(False, msg="Message not in memory index")

    def send_concat_msg_from_memory(test):
        if len(test.list_index_scmw) == 3:
            test.log.info("Send messages from DUT memory with indexes: {}".format(test.list_index_scmw))
            for item in test.list_index_scmw:
                test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.TIMEOUT_SMS_LONG))
                test.list_index_cmti_cmss.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
            return test.list_index_cmti_cmss
        else:
            test.expect(False, msg="NOT all expected messages in memory - step will be omitted")

    def execute_steps_1_4(test, steps_dict, list_dict_saved, list_dict_sent):
        test.log.info("===== Execute steps for character set: {} =====".format(steps_dict["descr"]))
        test.set_character_set(steps_dict["char_set"])
        test.set_dcs_via_csmp(steps_dict["dcs"])

        if list_dict_saved == test.SCMW_MSG_UCS2:
            da_number = test.DUT_NUMBER_UCS2
        else:
            da_number = test.DUT_NUMBER

        test.log.step("Step 1. save messages with at^scmw - create three segments \n"
                      "- the first segment contains carriage return (CR) character, \n"
                      "the second segment contains line feed (LF) character \n"
                      "and the last segment contains both characters (CR and LF).")
        test.write_all_concat_msg(list_dict_saved, da_number)
        test.log.info("===== Read saved SMS for {} =====".format(steps_dict["descr"]))
        test.read_all_concat_messages(test.list_index_scmw, da_number, list_dict_saved)

        test.log.step("Step 2. send each message segment from memory with at+cmss")
        test.send_concat_msg_from_memory()
        test.log.info("===== Read delivered messages sent from memory for {} =====".format(steps_dict["descr"]))
        test.read_all_concat_messages(test.list_index_cmti_cmss, da_number, list_dict_saved)

        test.log.step("Step 3. send each message directly with at^scms - also three segments, the same as in step 1.")
        test.send_all_concat_msg(list_dict_sent, da_number)
        test.log.info("===== Read delivered messages sent directly for {} =====".format(steps_dict["descr"]))
        test.read_all_concat_messages(test.list_index_cmti_scms, da_number, list_dict_sent)

        test.log.info("===== Delete All messages form memory =====")
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.list_index_scmw.clear()
        test.list_index_cmti_cmss.clear()
        test.list_index_cmti_scms.clear()

        if steps_dict["descr"] != "GSM_8bit":
            test.log.step("Step 4. repeat saving and sending for every character set supported by at+cscs command "
                          "(GSM, UCS2, etc.)")


if "__main__" == __name__:
    unicorn.main()