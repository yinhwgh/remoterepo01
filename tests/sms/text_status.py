#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0011146.001

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
    TC0011146.001    TextStatus

    Test if SMS with different statuses can be written, read and sent in Text mode.

    Test the following scenarios:
    1) write SMSes with different statuses
    2) send written messages to second module
    3) read messages without changing statuses (at^smgl, at^smgr)
    4) test invalid statuses entered via at^smgl, at^smgr
    5) read them with changing statuses (at+cmgl, at+cmgr)
    6) test invalid statuses entered via at+cmgl, at+cmgr
    """

    def setup(test):
        test.prepare_module(test.dut, "PREPARING DUT")
        test.prepare_module(test.r1, "PREPARING REMOTE")
        test.sms_timeout = 120
        test.rmt_int_number = test.r1.sim.int_voice_nr
        test.tosca_int = 145
        test.sms_status_rec_unread = "SMS Status 0 - REC UNREAD"
        test.sms_status_rec_read = "SMS Status 1 - REC READ"
        test.sms_status_sto_unsent = "SMS Status 2 - STO UNSENT"
        test.sms_status_sto_sent = "SMS Status 3 - STO SENT"
        test.sms_status_rec_unread_2 = "SMS Status 0 - REC UNREAD second"
        test.sms_status_sto_unsent_2 = "SMS Status 2 - STO UNSENT second"
        test.rmt_status_unchanged_list = ["REC UNREAD", "REC UNREAD"]
        test.rmt_content_list = [test.sms_status_sto_unsent, test.sms_status_sto_sent]
        test.dut_status_unchanged_list = ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"]
        test.dut_content_list = [test.sms_status_rec_unread, test.sms_status_rec_read,
                                 test.sms_status_sto_unsent, test.sms_status_sto_sent]
        test.dut_all_status_changed_list = ["REC READ", "REC READ", "STO UNSENT", "STO SENT"]
        test.dut_status_changed_list = ["REC READ", "REC READ"]
        test.dut_content_status_changed_list = [test.sms_status_rec_unread, test.sms_status_rec_read]
        test.dut_content_status_changed_list_2 = [test.sms_status_rec_unread_2, test.sms_status_rec_read]

    def run(test):
        test.log.step("Test the following scenarios: ")
        test.log.step("Step 1) write SMSes with different statuses")
        index_status_rec_unread = test.write_sms_status(test.sms_status_rec_unread, "REC UNREAD")
        index_status_rec_read = test.write_sms_status(test.sms_status_rec_read, "REC READ")
        index_status_sto_unsent = test.write_sms_status(test.sms_status_sto_unsent, "STO UNSENT")
        index_status_sto_sent = test.write_sms_status(test.sms_status_sto_sent, "STO SENT")
        test.write_sms_status("ALL", "ALL")
        test.dut_index_list = [index_status_rec_unread, index_status_rec_read,
                               index_status_sto_unsent, index_status_sto_sent]
        test.dut_index_status_changed_list = [index_status_rec_unread, index_status_rec_read]

        test.log.step("Step 2) send written messages to second module")
        test.log.info("***** Try to SEND all SMS "
                      "(only messages with status: STO SENT and STO UNSENT should be sent) *****")
        test.log.info("Send SMS with Status UR - REC UNREAD")
        test.send_sms_from_memory(index_status_rec_unread, ".*CMS ERROR.*")
        test.log.info("Send SMS with Status R - REC READ")
        test.send_sms_from_memory(index_status_rec_read, ".*CMS ERROR.*")
        test.log.info("Send SMS with Status US - STO UNSENT")
        rmt_sms_index_1 = test.send_sms_from_memory(index_status_sto_unsent, ".*OK.*")
        test.expect(test.r1.at1.send_and_verify("AT+CPMS?", ".*CPMS: \"ME\",1,.*OK.*"))
        test.log.info("Send SMS with Status S - STO SENT")
        rmt_sms_index_2 = test.send_sms_from_memory(index_status_sto_sent, ".*OK.*")
        test.expect(test.r1.at1.send_and_verify("AT+CPMS?", ".*CPMS: \"ME\",2,.*OK.*"))
        test.rmt_index_list = [rmt_sms_index_1, rmt_sms_index_2]

        test.log.step("Step 3) read messages without changing statuses (at^smgl, at^smgr)")
        test.log.info("***** LIST MESSAGES ON RMT MODULE WITHOUT STATUS CHANGE *****")
        test.log.info("List messages with status ALL")
        test.check_list_sms_command(test.r1, "AT^SMGL=\"ALL\"",
                                    test.rmt_index_list, test.rmt_status_unchanged_list, test.rmt_content_list)
        test.log.info("List messages with status REC UNREAD")
        test.check_list_sms_command(test.r1, "AT^SMGL=\"REC UNREAD\"",
                                    test.rmt_index_list, test.rmt_status_unchanged_list, test.rmt_content_list)
        test.log.info("List default <stat> - execute EXEC command SMGL - expected messages with status REC UNREAD")
        test.check_list_sms_command(test.r1, "AT^SMGL",
                                    test.rmt_index_list, test.rmt_status_unchanged_list, test.rmt_content_list)
        test.log.info("***** READ MESSAGES ON RMT MODULE WITHOUT STATUS CHANGE *****")
        test.read_message_on_dut(test.r1, "AT^SMGR", rmt_sms_index_1, "SMGR: \"REC UNREAD\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_sto_unsent))
        test.read_message_on_dut(test.r1, "AT^SMGR", rmt_sms_index_2, "SMGR: \"REC UNREAD\",.*[\n\r]{}.*OK.*"
                                 .format( test.sms_status_sto_sent))
        test.log.info("***** Check, if Status REC UNREAD still exist via SMGL=\"REC UNREAD\" command *****")
        test.check_list_sms_command(test.r1, "AT^SMGL=\"REC UNREAD\"",
                                    test.rmt_index_list, test.rmt_status_unchanged_list, test.rmt_content_list)
        test.log.info("***** LIST MESSAGES ON DUT MODULE WITHOUT STATUS CHANGE *****")
        test.log.info("***** Write STO UNSENT message one more time *****")
        test.expect(test.dut.at1.send_and_verify("AT+CMGD={}".format(index_status_sto_unsent), ".*OK.*"))
        index_status_sto_unsent_2 = test.write_sms_status(test.sms_status_sto_unsent_2, "STO UNSENT")
        test.log.info("List messages with status REC UNREAD")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"REC UNREAD\"",
                                    [index_status_rec_unread], ["REC UNREAD"], [test.sms_status_rec_unread])
        test.log.info("List messages with status REC READ")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"REC READ\"",
                                    [index_status_rec_read], ["REC READ"], [test.sms_status_rec_read])
        test.log.info("List messages with status STO UNSENT")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"STO UNSENT\"",
                                    [index_status_sto_unsent_2], ["STO UNSENT"], [test.sms_status_sto_unsent_2])
        test.log.info("List messages with status STO SENT")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"STO SENT\"",
                                    [index_status_sto_sent], ["STO SENT"], [test.sms_status_sto_sent])
        test.log.info("List messages with status ALL")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"ALL\"",
                                    test.dut_index_list, test.dut_status_unchanged_list, test.dut_content_list)
        test.log.info("List default <stat> - execute EXEC command SMGL - expected messages with status REC UNREAD")
        test.check_list_sms_command(test.dut, "AT^SMGL",
                                    [index_status_rec_unread], ["REC UNREAD"], [test.sms_status_rec_unread])
        test.log.info("***** READ MESSAGES ON DUT MODULE WITHOUT STATUS CHANGE *****")
        test.log.info("Read messages with status REC UNREAD")
        test.read_message_on_dut(test.dut, "AT^SMGR", index_status_rec_unread, "SMGR: \"REC UNREAD\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_rec_unread))
        test.log.info("Read messages with status REC READ")
        test.read_message_on_dut(test.dut, "AT^SMGR", index_status_rec_read, "SMGR: \"REC READ\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_rec_read))
        test.log.info("Read messages with status STO UNSENT")
        test.read_message_on_dut(test.dut, "AT^SMGR", index_status_sto_unsent_2, "SMGR: \"STO UNSENT\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_sto_unsent_2))
        test.log.info("Read messages with status STO SENT")
        test.read_message_on_dut(test.dut, "AT^SMGR", index_status_sto_sent, "SMGR: \"STO SENT\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_sto_sent))
        test.log.info("***** Check, if Status REC UNREAD still exist via SMGL=\"ALL\" command *****")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"ALL\"",
                                    test.dut_index_list, test.dut_status_unchanged_list, test.dut_content_list)

        test.log.step("Step 4) test invalid statuses entered via at^smgl, at^smgr")
        test.test_invalid_statuses_on_dut("AT^SMGL", "\"\"")
        test.test_invalid_statuses_on_dut("AT^SMGL", "\"REC\"")
        test.test_invalid_statuses_on_dut("AT^SMGL", "4")
        test.test_invalid_statuses_on_dut("AT^SMGR", "A")
        test.test_invalid_statuses_on_dut("AT^SMGR", "-1")
        test.test_invalid_statuses_on_dut("AT^SMGR", "\"\"")

        test.log.step("Step 5) read them with changing statuses (at+cmgl, at+cmgr)")
        test.log.info("***** READ WRITTEN SMSes ON DUT MODULE WITH CHANGING STATUS *****")
        test.log.info("Read messages with status REC UNREAD")
        test.read_message_on_dut(test.dut, "AT+CMGR", index_status_rec_unread, "CMGR: \"REC UNREAD\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_rec_unread))
        test.log.info("Read messages with status REC READ")
        test.read_message_on_dut(test.dut, "AT+CMGR", index_status_rec_read, "CMGR: \"REC READ\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_rec_read))
        test.log.info("Read messages with status STO UNSENT")
        test.read_message_on_dut(test.dut, "AT+CMGR", index_status_sto_unsent_2, "CMGR: \"STO UNSENT\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_sto_unsent_2))
        test.log.info("Read messages with status STO SENT")
        test.read_message_on_dut(test.dut, "AT+CMGR", index_status_sto_sent, "CMGR: \"STO SENT\",.*[\n\r]{}.*OK.*"
                                 .format(test.sms_status_sto_sent))
        test.log.info("***** Check, if Status REC UNREAD has changed to REC READ via SMGL=\"REC READ\" command *****")
        test.check_list_sms_command(test.dut, "AT^SMGL=\"REC READ\"", test.dut_index_status_changed_list,
                                    test.dut_status_changed_list,  test.dut_content_status_changed_list)
        test.log.info("***** LIST MESSAGES ON DUT MODULE WITH STATUS CHANGE *****")
        test.log.info("***** Write REC UNREAD message one more time *****")
        test.expect(test.dut.at1.send_and_verify("AT+CMGD={}".format(index_status_rec_unread), ".*OK.*"))
        index_status_rec_unread_2 = test.write_sms_status(test.sms_status_rec_unread_2, "REC UNREAD")
        test.dut_index_status_changed_list_2 = [index_status_rec_unread_2, index_status_rec_read]
        test.log.info("List messages with status REC UNREAD")
        test.check_list_sms_command(test.dut, "AT+CMGL=\"REC UNREAD\"",
                                    [index_status_rec_unread_2], ["REC UNREAD"], [test.sms_status_rec_unread_2])
        test.log.info("List messages with status REC READ")
        test.check_list_sms_command(test.dut, "AT+CMGL=\"REC READ\"", test.dut_index_status_changed_list_2,
                                    test.dut_status_changed_list, test.dut_content_status_changed_list_2)
        test.log.info("List messages with status STO UNSENT")
        test.check_list_sms_command(test.dut, "AT+CMGL=\"STO UNSENT\"",
                                    [index_status_sto_unsent_2], ["STO UNSENT"], [test.sms_status_sto_unsent_2])
        test.log.info("List messages with status STO SENT")
        test.check_list_sms_command(test.dut, "AT+CMGL=\"STO SENT\"",
                                    [index_status_sto_sent], ["STO SENT"], [test.sms_status_sto_sent])
        test.log.info("List messages with status ALL")
        test.dut_index_list_2 = [index_status_rec_unread_2, index_status_rec_read,
                                 index_status_sto_unsent_2, index_status_sto_sent]
        test.dut_content_list_2 = [test.sms_status_rec_unread_2, test.sms_status_rec_read,
                                   test.sms_status_sto_unsent_2, test.sms_status_sto_sent]
        test.check_list_sms_command(test.dut, "AT+CMGL=\"ALL\"",
                                    test.dut_index_list_2, test.dut_all_status_changed_list, test.dut_content_list_2)

        test.log.step("Step 6) test invalid statuses entered via at+cmgl, at+cmgr")
        test.test_invalid_statuses_on_dut("AT+CMGL", "\"\"")
        test.test_invalid_statuses_on_dut("AT+CMGL", "\"REC\"")
        test.test_invalid_statuses_on_dut("AT+CMGL", "4")
        test.test_invalid_statuses_on_dut("AT+CMGR", "A")
        test.test_invalid_statuses_on_dut("AT+CMGR", "-1")
        test.test_invalid_statuses_on_dut("AT+CMGR", "\"\"")

    def cleanup(test):
        test.delete_sms_from_memory(test.dut)
        test.restore_values(test.dut)
        test.delete_sms_from_memory(test.r1)
        test.restore_values(test.r1)

    def prepare_module(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        test.expect(dstl_get_imei(module))
        test.expect(dstl_get_bootloader(module))
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.delete_sms_from_memory(module)

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def restore_values(test, module):
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def write_sms_status(test, msg_text, status):
        test.log.info("Write SMS with Status: {}".format(status))
        if status == "ALL":
            test.expect(test.dut.at1.send_and_verify("AT+CMGW=\"{}\",{},\"{}\"".
                                                     format(test.rmt_int_number, test.tosca_int, status), ".*ERROR.*"))
        else:
            if status == "REC UNREAD" or status == "REC READ":
                test.log.info("message status REC UNREAD and REC READ require timestamp value, \n"
                              "which is taken from at+csmp <vp> parameter \n"
                              "current value must be stored in absolute format: \n"
                              "<fo> - 24d > xxx11x00b > VPF - (11) absolute format, MTI - (00)SMS DELIVER \n")
                test.expect(test.dut.at1.send_and_verify("AT+CSMP=24,\"18/01/01,08:10:00+02\",0,0", ".*"))
                if test.dut.platform.upper() is 'QCT' and test.dut.at1.last_response("ERROR"):
                    test.log.info("ERROR due to IPIS100232580 (BOBCAT), continue with workaround")
                    test.expect(test.dut.at1.send_and_verify("AT+CSMP=24,", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CMGW=\"{}\",{},\"{}\"".
                                                     format(test.rmt_int_number, test.tosca_int, status), expect=">"))
            test.expect(test.dut.at1.send_and_verify(msg_text, end="\u001A", expect=".*OK.*", timeout=test.sms_timeout))
            index = test.get_sms_index(test.dut, ".*CMGW: (.*)", "CMGW")
            if status == "REC UNREAD" or status == "REC READ":
                test.log.info("restore default setting of csmp")
                test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
            return index

    def get_sms_index(test, module, regex, message):
        response_content = test.expect(re.search(regex, module.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for {} is: {}".format(message, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(message))

    def send_sms_from_memory(test, index, expected_resp):
        if expected_resp == ".*OK.*":
            test.expect(dstl_send_sms_message_from_memory(test.dut, index))
            test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.sms_timeout))
            return test.get_sms_index(test.r1, r".*CMTI.*,\s*(\d{1,3})", "CMTI")
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CMSS={}".format(index), expected_resp))

    def check_list_sms_command(test, module, command, index_list, status, content):
        test.expect(module.at1.send_and_verify("{}".format(command), ".*OK.*"))
        for item in index_list:
            test.log.info("Expected REGEX: .*{}: {},\"{}\",.*[\n\r]{}.*".format(command[3:7], item,
                                                status[index_list.index(item)], content[index_list.index(item)]))
            test.expect(re.search(".*{}: {},\"{}\",.*[\n\r]{}.*".format(command[3:7], item, status[index_list.index(item)],
                                                        content[index_list.index(item)]), module.at1.last_response))

    def read_message_on_dut(test, module, command, index, response):
        test.expect(module.at1.send_and_verify("{}={}".format(command, index), response))

    def test_invalid_statuses_on_dut(test, command, invalid_status):
        test.expect(test.dut.at1.send_and_verify("{}={}".format(command, invalid_status), ".*ERROR.*"))


if "__main__" == __name__:
    unicorn.main()