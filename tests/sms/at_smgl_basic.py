# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0091898.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0091898.001     AtSmglBasic
    This procedure provides the possibility of basic tests for the test, exec and write command of AT^SMGL.
    1. Check command without and with PIN
        - scenario without PIN authentication: test, exec and write commands should be PIN protected

    2. Check write command with valid and invalid parameters in PDU and Text mode

        - verify input and output syntax also with detailed header (at+csdh=1)
    A functional check is not done here:
    - functionality test is done in PDUStatus and TextStatus
    """

    def setup(test):
        test.mode_0 = 0
        test.mode_1 = 1
        test.timeout = 60
        test.scts = "94/05/06,22:10:00+08"
        test.int_voice_nr = '+48500100200'
        test.pdu = '0B918405100002F0'
        test.invalid_parameters_text = (0, 1, 2, 3, 4, 255, -1, '1REC READ', '"4STO SENT"', '"COMMON"', '"A"', '""',
                                        '"ERROR"', 'ERROR', 'full', '"ALL1"', 4000)
        test.invalid_parameters_pdu = ('"REC UNREAD"', '"REC READ"', '"STO UNSENT"', '"STO SENT"', '"ALL"', 255, -1,
                                       '1REC READ', '"4STO SENT"', '"COMMON"', '"A"', '""', '"ERROR"', 'ERROR',
                                       'full', '"ALL1"', 4000)
        test.status_list_text = ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT", "ALL"]
        test.status_list_pdu = [0, 1, 2, 3, 4]
        test.content_list_text = ['REC UNREAD test', 'REC READ test', 'STO UNSENT test', 'STO SENT test']
        test.content_list_pdu = ['D2E21054754A8B4122885E9ED301', 'D2E210242D0689207A794E07',
                                 '53EA1354754E8B4E2A885E9ED301', '53EA13342D3AA9207A794E07']
        test.prepare_module()


    def run(test):
        test.log.step("1. Check command without and with PIN - scenario without PIN authentication: test, exec and "
                      "write commands should be PIN protected")
        test.log.step("===== Check command without PIN =====")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
        if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
            test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
        else:
            test.log.info("SIM PIN entered - restart is needed")
            test.expect(dstl_restart(test.dut))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
            if re.search(r".*SIM PIN.*", test.dut.at1.last_response):
                test.expect(True, msg="SIM PIN code locked - checking if command is PIN protected could be realized")
            else:
                test.expect(True, msg="SIM PIN code unlocked - must be locked for checking if command is PIN protected")
                test.expect(dstl_lock_sim(test.dut))
                test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=?", r".*\+CMS ERROR: SIM PIN required.*", timeout=test.timeout))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL", r".*\+CMS ERROR: SIM PIN required.*", timeout=test.timeout))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=1", r".*\+CMS ERROR: SIM PIN required.*", timeout=test.timeout))

        test.log.step("===== Check command with PIN authentication =====")
        test.expect(dstl_enter_pin(test.dut))
        test.log.info("Wait according to info from ATC: [\n]"
                      "Users should be aware that error will occur when using this AT command quickly [\n]"
                      "after SIM PIN authentication due to the fact the SIM data may not yet be accessible")
        test.sleep(timeout=test.timeout) 
        test.log.info("***** Tests on an empty memory in PDU mode *****")
        test.expect(dstl_select_sms_message_format(test.dut, sms_format="PDU"))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=?", r".*\^SMGL: \(0(-|,1,2,3,)4\).*OK.*"))
        test.check_exec_command_with_empty_memory()
        test.list_sms_command_with_empty_memory(test.mode_0, test.status_list_pdu)

        test.log.info("***** Tests on an empty memory in Text mode *****")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=?",
                    r'.*\^SMGL: \("REC UNREAD","REC READ","STO UNSENT","STO SENT","ALL"\).*OK.*'))
        test.check_exec_command_with_empty_memory()
        test.list_sms_command_with_empty_memory(test.mode_1, test.status_list_text)

        test.log.step("2. Check write command with valid and invalid parameters in PDU and Text mode [\n]"
                      "- verify input and output syntax also with detailed header (at+csdh=1)")
        test.log.info("***** Tests with SMS in memory - write to memory messages with all statuses *****")
        test.index_list = [test.write_sms_with_status(test.content_list_text[0], test.status_list_text[0]),
                           test.write_sms_with_status(test.content_list_text[1], test.status_list_text[1]),
                           test.write_sms_with_status(test.content_list_text[2], test.status_list_text[2]),
                           test.write_sms_with_status(test.content_list_text[3], test.status_list_text[3])]

        test.log.step("===== Check command with valid parameters =====")
        test.log.info("***** Check command in PDU mode *****")
        test.expect(dstl_select_sms_message_format(test.dut, sms_format="PDU"))
        test.log.info("===== List messages with status REC UNREAD =====")
        test.list_sms_in_pdu("AT^SMGL=0", test.status_list_pdu[:1], test.index_list[:1], test.content_list_pdu[:1])
        test.log.info("===== List messages with status REC READ =====")
        test.list_sms_in_pdu("AT^SMGL=1", test.status_list_pdu[1:2], test.index_list[1:2], test.content_list_pdu[1:2])
        test.log.info("===== List messages with status STO UNSENT =====")
        test.list_sms_in_pdu("AT^SMGL=2", test.status_list_pdu[2:3], test.index_list[2:3], test.content_list_pdu[2:3])
        test.log.info("===== List messages with status STO SENT =====")
        test.list_sms_in_pdu("AT^SMGL=3", test.status_list_pdu[3:4], test.index_list[3:], test.content_list_pdu[3:])
        test.log.info("===== List messages with status ALL =====")
        test.list_sms_in_pdu("AT^SMGL=4", test.status_list_pdu, test.index_list, test.content_list_pdu)
        test.log.info("***** List default <stat> - execute EXEC command SMGL "
                      "- expected messages with status REC UNREAD *****")
        test.list_sms_in_pdu("AT^SMGL", test.status_list_pdu[:1], test.index_list[:1], test.content_list_pdu[:1])

        test.log.info("***** Check command in Text mode with disabled the SMS detailed header (AT+CSDH=0) *****")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.set_sms_detailed_header(test.mode_0)
        test.log.info("===== List messages with status REC UNREAD =====")
        test.list_sms_in_text(test.mode_0, "AT^SMGL=\"REC UNREAD\"", test.index_list[:1],
                              test.status_list_text[:1], test.content_list_text[:1])
        test.log.info("===== List messages with status REC READ =====")
        test.list_sms_in_text(test.mode_0, "AT^SMGL=\"REC READ\"", test.index_list[1:2],
                              test.status_list_text[1:2], test.content_list_text[1:2])
        test.log.info("===== List messages with status STO UNSENT =====")
        test.list_sms_in_text(test.mode_0, "AT^SMGL=\"STO UNSENT\"", test.index_list[2:3],
                              test.status_list_text[2:3], test.content_list_text[2:3])
        test.log.info("===== List messages with status STO SENT =====")
        test.list_sms_in_text(test.mode_0, "AT^SMGL=\"STO SENT\"", test.index_list[3:],
                              test.status_list_text[3:4], test.content_list_text[3:])
        test.log.info("===== List messages with status ALL =====")
        test.list_sms_in_text(test.mode_0, "AT^SMGL=\"ALL\"", test.index_list, test.status_list_text,
                              test.content_list_text)
        test.log.info("***** List default <stat> - execute EXEC command SMGL "
                      "- expected messages with status REC UNREAD *****")
        test.list_sms_in_text(test.mode_0, "AT^SMGL", test.index_list[:1],
                              test.status_list_text[:1], test.content_list_text[:1])
        test.log.info("***** Check command in Text mode with enabled the SMS detailed header (AT+CSDH=1) *****")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.set_sms_detailed_header(test.mode_1)
        test.log.info("===== List messages with status REC UNREAD =====")
        test.list_sms_in_text(test.mode_1, "AT^SMGL=\"REC UNREAD\"", test.index_list[:1],
                              test.status_list_text[:1], test.content_list_text[:1])
        test.log.info("===== List messages with status REC READ =====")
        test.list_sms_in_text(test.mode_1, "AT^SMGL=\"REC READ\"", test.index_list[1:2],
                              test.status_list_text[1:2], test.content_list_text[1:2])
        test.log.info("===== List messages with status STO UNSENT =====")
        test.list_sms_in_text(test.mode_1, "AT^SMGL=\"STO UNSENT\"", test.index_list[2:3],
                              test.status_list_text[2:3], test.content_list_text[2:3])
        test.log.info("===== List messages with status STO SENT =====")
        test.list_sms_in_text(test.mode_1, "AT^SMGL=\"STO SENT\"", test.index_list[3:],
                              test.status_list_text[3:], test.content_list_text[3:])
        test.log.info("===== List messages with status ALL =====")
        test.list_sms_in_text(test.mode_1, "AT^SMGL=\"ALL\"", test.index_list, test.status_list_text,
                              test.content_list_text)
        test.log.info("***** List default <stat> - execute EXEC command SMGL "
                      "- expected messages with status REC UNREAD *****")
        test.list_sms_in_text(test.mode_1, "AT^SMGL", test.index_list[:1],
                              test.status_list_text[:1], test.content_list_text[:1])

        test.log.step("===== Check command with valid parameters =====")
        test.log.info("***** Check command in PDU mode *****")
        test.expect(dstl_select_sms_message_format(test.dut, sms_format="PDU"))
        for param in test.invalid_parameters_pdu:
            test.expect(test.dut.at1.send_and_verify("AT^SMGL={}".format(param), ".*CMS ERROR.*"))
        test.log.info("***** Check command with invalid parameters in Text mode *****")
        test.expect(dstl_select_sms_message_format(test.dut))
        for param in test.invalid_parameters_text:
            test.expect(test.dut.at1.send_and_verify("AT^SMGL={}".format(param), ".*CMS ERROR.*"))

    def cleanup(test):
        test.log.info('===== Delete SMS from memory and restore values =====')
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module(test):
        test.log.info("===== Preparing DUT for test =====")
        dstl_detect(test.dut)
        test.expect(dstl_get_imei(test.dut))
        test.expect(dstl_get_bootloader(test.dut))
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def set_sms_detailed_header(test, mode):
        test.expect(test.dut.at1.send_and_verify("AT+CSDH={}".format(mode), ".*OK.*"))

    def check_exec_command_with_empty_memory(test):
        test.expect(test.dut.at1.send_and_verify("AT^SMGL", ".*OK.*"))
        test.expect(not re.search(".*SMGL:.*", test.dut.at1.last_response))

    def list_sms_command_with_empty_memory(test, format_mode, status):
        if format_mode == 1:
            for i in status:
                test.expect(test.dut.at1.send_and_verify("AT^SMGL=\"{}\"".format(i), ".*OK.*"))
                test.expect(not re.search(".*SMGL:.*", test.dut.at1.last_response))
        else:
            for i in status:
                test.expect(test.dut.at1.send_and_verify("AT^SMGL={}".format(i), "^.*OK.*"))
                test.expect(not re.search(".*SMGL:.*", test.dut.at1.last_response))

    def write_sms_with_status(test, msg_text, status):
        test.log.info("===== Write SMS with Status: {} =====".format(status))
        if status == "REC UNREAD" or status == "REC READ":
            test.log.info("message status REC UNREAD and REC READ require timestamp value, \n"
                          "which is taken from at+csmp <vp> parameter \n"
                          "current value must be stored in absolute format: \n"
                          "<fo> - 24d > xxx11x00b > VPF - (11) absolute format, MTI - (00)SMS DELIVER \n")
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=24,\"{}\",0,0".format(test.scts), ".*"))
            if test.dut.platform.upper() is 'QCT' and test.dut.at1.last_response("ERROR"):
                test.log.info("ERROR due to IPIS100232580 (BOBCAT) but problem appears all over the QCT platform, "
                              "continue with workaround")
                test.expect(test.dut.at1.send_and_verify("AT+CSMP=24,", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMGW=\"{}\",145,\"{}\"".
                                                 format(test.int_voice_nr, status), expect=">"))
        test.expect(test.dut.at1.send_and_verify(msg_text, end="\u001A", expect=".*OK.*", timeout=test.timeout))
        index = test.get_sms_index(".*CMGW: (.*)", "CMGW")
        if status == "REC UNREAD" or status == "REC READ":
            test.log.info("restore default setting of csmp")
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        return index

    def get_sms_index(test, regex, message):
        response_content = test.expect(re.search(regex, test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for {} is: {}".format(message, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(message))

    def list_sms_in_text(test, mode, command, index_list, status, content):
        scts_regex = r"94\/05\/06,22:10:00\+08"
        length = 0
        test.expect(test.dut.at1.send_and_verify("{}".format(command), ".*OK.*"))
        if mode == test.mode_0:
            for item in index_list:
                regex_status_rec = r".*{}: {},\"{}\",\"\{}\",,\"{}\"\s*[\n\r]{}.*".format(command[3:7], item,
                                                                                          status[
                                                                                              index_list.index(item)],
                                                                                          test.int_voice_nr, scts_regex,
                                                                                          content[
                                                                                              index_list.index(item)])
                regex_status_sto = r".*{}: {},\"{}\",\"\{}\",,\s*[\n\r]{}.*".format(command[3:7], item,
                                                                                    status[index_list.index(item)],
                                                                                    test.int_voice_nr,
                                                                                    content[index_list.index(item)])

                if test.index_list.index(item) < 2:
                    test.log.info("Expected REGEX: {}".format(regex_status_rec))
                    test.expect(re.search(regex_status_rec, test.dut.at1.last_response))
                else:
                    test.log.info("Expected REGEX: {}".format(regex_status_sto))
                    test.expect(re.search(regex_status_sto, test.dut.at1.last_response))
        elif mode == test.mode_1:
            for item in index_list:
                if test.index_list.index(item) == 0 or test.index_list.index(item) == 2:
                    length = 15
                elif test.index_list.index(item) == 1 or test.index_list.index(item) == 3:
                    length = 13
                regex_status_rec = r".*{}: {},\"{}\",\"\{}\",,\"{}\",145,{}\s*[\n\r]{}.*".format(command[3:7], item,
                                                                                                 status[
                                                                                                     index_list.index(
                                                                                                         item)],
                                                                                                 test.int_voice_nr,
                                                                                                 scts_regex, length,
                                                                                                 content[
                                                                                                     index_list.index(
                                                                                                         item)])
                regex_status_sto = r".*{}: {},\"{}\",\"\{}\",,,145,{}\s*[\n\r]{}.*".format(command[3:7], item,
                                                                                           status[
                                                                                               index_list.index(item)],
                                                                                           test.int_voice_nr, length,
                                                                                           content[
                                                                                               index_list.index(item)])

                if test.index_list.index(item) < 2:
                    test.log.info("Expected REGEX: {}".format(regex_status_rec))
                    test.expect(re.search(regex_status_rec, test.dut.at1.last_response))
                else:
                    test.log.info("Expected REGEX: {}".format(regex_status_sto))
                    test.expect(re.search(regex_status_sto, test.dut.at1.last_response))

    def list_sms_in_pdu(test, command, status, index_list, content):
        test.dut.at1.send_and_verify("{}".format(command), ".*OK.*")
        for item in index_list:
            msg_content = re.search(r"\S+{}".format(content[index_list.index(item)]), test.dut.at1.last_response)[0]
            if msg_content:
                regex_pdu = r".*\^SMGL: {},{},,{}\s*[\n\r].*{}.*{}\s*[\n\r].*" \
                    .format(item, status[index_list.index(item)], _calculate_pdu_length(msg_content), test.pdu,
                            content[index_list.index(item)])
                test.log.info("Expected REGEX: {}".format(regex_pdu))
                test.expect(re.search(regex_pdu, test.dut.at1.last_response))
            else:
                test.expect(False, msg="Message not found")


if "__main__" == __name__:
    unicorn.main()
