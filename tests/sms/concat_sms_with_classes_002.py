#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095108.002

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
    TC0095108.002    	ConcatSmsWithClasses

    Check if concatenated short messages with different classes are write, send and receive correctly.

    Precondition: One module logged on to the network. Provider supports concatenated short messages.

    1. Set text mode AT+CMGF=1
    2. Set AT+CNMI=2,1,0,0
    3. Set AT+CSMP=17,167,0,0 (Class None)
    4. Write concatenated message to memory (at least 3 segments) with own number
    (example: at^scmw="+48123456789",,"STO UNSENT",1,3,8,123)
    5. Read saved message and check if content is the same
    (at^scml command)
    6. Send message from memory and check content of received message
    (example: at+cmss=X where X are indexes of message parts in memory)
    7. Send the same message directly, without saving to memory to own number
    (example: at^scms="+48123456789",,1,3,8,124)
    8. Read messages (only for CMTI) and check if content is the same (for CMTI and CMT)
    (at^scml command)
    9. Delete all messages
    (example: at+cmgd=1,4)
    10. Repeat steps 3 to 9 with SMS class 0, 1, 2 and 3
    """

    timeout = 60
    sms_timeout_long = 360
    sms_class = {"0": "Class None", "240": "Class 0", "241": "Class 1", "242": "Class 2", "243": "Class 3"}
    list_dict_saved_messages = [{"command": "SCMW", "ref": "123", "segment": "1"},
                                     {"command": "SCMW", "ref": "123", "segment": "2"},
                                     {"command": "SCMW", "ref": "123", "segment": "3"}]
    list_dict_delivered_messages = [{"command": "SCMS", "ref": "124", "segment": "1"},
                                         {"command": "SCMS", "ref": "124", "segment": "2"},
                                         {"command": "SCMS", "ref": "124", "segment": "3"},
                                         {"command": "SCMW", "ref": "123", "segment": "1"},
                                         {"command": "SCMW", "ref": "123", "segment": "2"},
                                         {"command": "SCMW", "ref": "123", "segment": "3"}]
    list_index_cmti = []

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_register_to_network(test.dut)
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        test.log.step("Step 1. Set text mode AT+CMGF=1")
        test.expect(dstl_select_sms_message_format(test.dut))

        test.log.step("Step 2. Set AT+CNMI=2,1,0,0")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", ".*CNMI: 2,1,0,0,.*OK.*"))

        for item in test.sms_class:
            test.log.info("===== Test for SMS: {} =====".format(test.sms_class[item]))
            test.log.step("Step 3. Set AT+CSMP=17,167,0,{} ({})".format(item, test.sms_class[item]))
            test.set_sms_class_via_csmp(item)

            test.log.step("Step 4. Write concatenated message to memory (at least 3 segments) with own number"
                          "(example: at^scmw=\"+48123456789\",,\"STO UNSENT\",1,3,8,123)")
            test.list_index_scmw = test.save_concat_message(test.sms_class[item])

            test.log.step("Step 5. Read saved message and check if content is the same (at^scml command)")
            test.list_saved_messages_via_scml(test.list_index_scmw, test.sms_class[item])

            test.log.step("Step 6. Send the same message directly, without saving to memory to own number"
                          "(example: at^scms=\"+48123456789\",,1,3,8,124)")
            test.send_concat_message_directly(test.sms_class[item], item)

            if item == "240":
                test.log.info("===== For Class 0: verification of CMT messages will be directly after sending message "
                              "- steps 7 and 8 will be realized together =====")
                test.log.step("Step 7. Send message from memory and check content of received message"
                              "(example: at+cmss=X where X are indexes of message parts in memory)")
                test.log.step("Step 8. Read messages (only for CMTI) and check if content is the same "
                              "(for CMTI and CMT) (at^scml command)")
                test.send_message_from_memory(test.list_index_scmw, item)

            else:
                test.log.step("Step 7. Send message from memory and check content of received message"
                              "(example: at+cmss=X where X are indexes of message parts in memory)")
                test.send_message_from_memory(test.list_index_scmw, item)

                test.log.step("Step 8. Read messages (only for CMTI) and check if content is the same (for CMTI and CMT)"
                              "(at^scml command)")
                if item == "242":
                    test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
                test.list_delivered_messages_via_scml(test.list_index_cmti, test.sms_class[item])

            test.log.step("Step 9. Delete all messages (example: at+cmgd=1,4)")
            if item == "242":
                test.expect(dstl_delete_all_sms_messages(test.dut))
                test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
            test.expect(dstl_delete_all_sms_messages(test.dut))
            test.list_index_cmti.clear()

            if test.sms_class[item] != "Class 3":
                test.log.step("Step 10. Repeat steps 3 to 9 with SMS class 0, 1, 2 and 3")

    def cleanup(test):
        test.set_sms_class_via_csmp("0")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def set_sms_class_via_csmp(test, sms_class):
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(sms_class), ".*OK.*"))

    def list_saved_messages_via_scml(test, index_list, sms_class):
        test.expect(test.dut.at1.send_and_verify("AT^SCML=\"ALL\"", ".*OK.*"))
        for item in index_list:
            test.log.info("Expected phrase: .*SCML: {0},\"STO UNSENT\",\"\{1}\",,,145,\d{{1,3}},{4},3,8,{3}\s*[\n\r]"
                          "{2} {5} segment {4}.*".format(item, test.dut.sim.int_voice_nr,
                          test.list_dict_saved_messages[index_list.index(item)]["command"],
                          test.list_dict_saved_messages[index_list.index(item)]["ref"],
                          test.list_dict_saved_messages[index_list.index(item)]["segment"], sms_class))
            test.expect(re.search(".*SCML: {0},\"STO UNSENT\",\"\{1}\",,,145,\d{{1,3}},{4},3,8,{3}\s*[\n\r]"
                          "{2} {5} segment {4}.*".format(item, test.dut.sim.int_voice_nr,
                          test.list_dict_saved_messages[index_list.index(item)]["command"],
                          test.list_dict_saved_messages[index_list.index(item)]["ref"],
                          test.list_dict_saved_messages[index_list.index(item)]["segment"], sms_class),
                          test.dut.at1.last_response))

    def list_delivered_messages_via_scml(test, index_list, sms_class):
        test.expect(test.dut.at1.send_and_verify("AT^SCML=\"ALL\"", ".*OK.*"))
        for item in index_list:
            test.log.info("Expected phrase: .*SCML: {0},\"REC UNREAD\",\"\{1}\",,\".*\",145,\d{{1,3}},{4},3,8,{3}\s*[\n\r]"
                          "{2} {5} segment {4}.*".format(item, test.dut.sim.int_voice_nr,
                          test.list_dict_delivered_messages[index_list.index(item)]["command"],
                          test.list_dict_delivered_messages[index_list.index(item)]["ref"],
                          test.list_dict_delivered_messages[index_list.index(item)]["segment"], sms_class))
            test.expect(re.search(".*SCML: {0},\"REC UNREAD\",\"\{1}\",,\".*\",145,\d{{1,3}},{4},3,8,{3}\s*[\n\r]"
                                  "{2} {5} segment {4}.*".format(item, test.dut.sim.int_voice_nr,
                                  test.list_dict_delivered_messages[index_list.index(item)]["command"],
                                  test.list_dict_delivered_messages[index_list.index(item)]["ref"],
                                  test.list_dict_delivered_messages[index_list.index(item)]["segment"], sms_class),
                                  test.dut.at1.last_response))

    def save_concat_message(test, sms_class):
        list_command_index = []
        for segment in range(1, 4):
            test.log.info("*** write SMS {}/3 ***".format(segment))
            test.expect(test.dut.at1.send_and_verify("AT^SCMW=\"{}\",,\"STO UNSENT\",{},3,8,123"
                        .format(test.dut.sim.int_voice_nr, segment), expect=">"))
            test.expect(test.dut.at1.send_and_verify("SCMW {} segment {}".format(sms_class, segment),
                        end="\u001A", expect=".*OK.*", timeout=test.timeout))
            list_command_index.append(test.get_sms_index(r".*SCMW:\s*(\d{1,3})", "SCMW"))
        return list_command_index

    def send_concat_message_directly(test, sms_class, dcs):
        for segment in range(1, 4):
            test.log.info("*** send SMS {}/3 ***".format(segment))
            test.expect(test.dut.at1.send_and_verify("AT^SCMS=\"{}\",,{},3,8,124"
                        .format(test.dut.sim.int_voice_nr, segment), expect=">"))
            test.expect(test.dut.at1.send_and_verify("SCMS {} segment {}".format(sms_class, segment),
                        end="\u001A", expect=".*OK.*", timeout=test.timeout))
            if dcs == "240":
                test.expect(dstl_check_urc(test.dut, ".*CMT:.*SCMS Class 0 segment {}"
                                           .format(segment), timeout=test.sms_timeout_long))
            else:
                test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout_long))
                test.list_index_cmti.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
        return test.list_index_cmti

    def send_message_from_memory(test, list_command_index, dcs):
        for item in list_command_index:
            if dcs == "240":
                test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                if list_command_index.index(item) == 0:
                    test.expect(dstl_check_urc(test.dut, ".*CMT:.*SCMW Class 0 segment 1", timeout=test.sms_timeout_long))
                elif list_command_index.index(item) == 1:
                    test.expect(dstl_check_urc(test.dut, ".*CMT:.*SCMW Class 0 segment 2", timeout=test.sms_timeout_long))
                elif list_command_index.index(item) == 2:
                    test.expect(dstl_check_urc(test.dut, ".*CMT:.*SCMW Class 0 segment 3", timeout=test.sms_timeout_long))
            else:
                test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout_long))
                test.list_index_cmti.append(test.get_sms_index(r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
        return test.list_index_cmti

    def get_sms_index(test, regex, command):
        response_content = test.expect(re.search(regex, test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of CMTI")


if "__main__" == __name__:
    unicorn.main()