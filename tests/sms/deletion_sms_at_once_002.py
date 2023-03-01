#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0074270.002
#SRV03-5035

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    """ TC0074270.002    DeletionSMSatOnce
    At the beginning SMS storage is filled with different kind of SMS, then storage is cleaned with at+cmgd=,
    where are parameters described in 3gpp standard no. 27.005.
    Scenario should be checked for memory: SM and ME

    For following values of behaviours as below (according to 3gpp) are expected:
    
    0 (or omitted) Delete the message specified in (not tested in this TC)
    1 Delete all read messages from preferred message storage,
    leaving unread messages and stored mobile originated messages (whether sent or not) untouched
    2 Delete all read messages from preferred message storage and sent mobile originated messages,
    leaving unread messages and unsent mobile originated messages untouched
    3 Delete all read messages from preferred message storage, sent and unsent mobile originated messages,
    leaving unread messages untouched
    4 Delete all messages from preferred message storage including unread messages.
    """

    mode_0 = 0
    mode_1 = 1
    timeout = 60
    scts = "94/05/06,22:10:00+08"
    int_voice_nr = '+485001002002'
    memories = ["SM", "ME"]

    def setup(test):
        test.log.h2('Starting TP for TC0074270.002 - DeletionSMSatOnce')
        test.prepare_module()

    def run(test):
        test.log.info('For following values of behaviours as below (according to 3gpp) are expected:')
        test.log.step('Step 0 (or omitted) Delete the message specified in (not tested in this TC)')

        for mem in test.memories:
            test.log.info("===== Test second parameter of at+cmgd command for memory {} =====".format(mem))
            test.log.info("Delete SMS from memory {}".format(mem))
            test.expect(dstl_set_preferred_sms_memory(test.dut, mem))
            test.expect(dstl_delete_all_sms_messages(test.dut))

            test.log.step('Step 1 Delete all read messages from preferred message storage, leaving unread messages '
                          'and stored mobile originated messages (whether sent or not) untouched')
            test.log.info("***** Write to memory messages with ALL statuses *****")
            test.write_sms_with_status("REC UNREAD", "REC UNREAD test")
            test.write_sms_with_status("REC READ", "REC READ test")
            test.write_sms_with_status("STO UNSENT", "STO UNSENT test")
            test.write_sms_with_status("STO SENT", "STO SENT test")
            test.verify_messages_in_memory(5, 4, ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"], [])
            test.delete_messages_with_deflag(1)
            test.verify_messages_in_memory(1, 3, ["REC UNREAD", "STO UNSENT", "STO SENT"], ["REC READ"])

            test.log.step('Step 2 Delete all read messages from preferred message storage and sent mobile originated '
                          'messages, leaving unread messages and unsent mobile originated messages untouched')
            test.log.info("***** Write to memory messages with status REC READ *****")
            test.write_sms_with_status("REC READ", "REC READ test")
            test.verify_messages_in_memory(5, 4, ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"], [])
            test.delete_messages_with_deflag(2)
            test.verify_messages_in_memory(2, 2, ["REC UNREAD", "STO UNSENT"], ["REC READ", "STO SENT"])

            test.log.step('Step 3 Delete all read messages from preferred message storage, sent and unsent mobile '
                          'originated messages, leaving unread messages untouched')
            test.log.info("***** Write to memory messages with statuses REC READ and STO SENT *****")
            test.write_sms_with_status("REC READ", "REC READ test")
            test.write_sms_with_status("STO SENT", "STO SENT test")
            test.verify_messages_in_memory(5, 4, ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"], [])
            test.delete_messages_with_deflag(3)
            test.verify_messages_in_memory(3, 1, ["REC UNREAD"], ["REC READ", "STO UNSENT", "STO SENT"])

            test.log.step('Step 4 Delete all messages from preferred message storage including unread messages')
            test.log.info("***** Write to memory messages with statuses REC READ, STO UNSENT and STO SENT *****")
            test.write_sms_with_status("REC READ", "REC READ test")
            test.write_sms_with_status("STO UNSENT", "STO UNSENT test")
            test.write_sms_with_status("STO SENT", "STO SENT test")
            test.verify_messages_in_memory(5, 4, ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"], [])
            test.delete_messages_with_deflag(4)
            test.verify_messages_in_memory(4, 0, [], ["REC UNREAD", "REC READ", "STO UNSENT", "STO SENT"])

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')

    def prepare_module(test):
        test.log.info("===== Preparing DUT for test =====")
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))

    def write_sms_with_status(test, status, msg_text):
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
        if status == "REC UNREAD" or status == "REC READ":
            test.log.info("restore default setting of csmp")
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))

    def verify_messages_in_memory(test, deflag, sms_number, status_search_list, status_not_search_list):
        test.log.info("*** Check if the correct number of messages is saved in memory ***")
        test.log.info("*** Expected {} messages ***".format(str(sms_number)))
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == sms_number)
        test.log.info("*** Check messages in storage via SMGL command ***")
        test.expect(test.dut.at1.send_and_verify("AT^SMGL=\"ALL\"", ".*OK.*"))
        if deflag == 1:
            test.log.info("*** Check if only READ messages have been deleted from memory ***")
        elif deflag == 2:
            test.log.info("*** Check if READ and SENT messages have been deleted from memory ***")
        elif deflag == 3:
            test.log.info("*** Check if READ, SENT and UNSENT messages have been deleted from memory ***")
        elif deflag == 4:
            test.log.info("*** Check if ALL messages have been deleted from memory ***")
        else:
            test.log.info("*** Check if ALL messages are saved in memory ***")
        if status_search_list:
            for status_search in status_search_list:
                test.log.info("Expected REGEX: {}".format(status_search))
                test.expect(re.search(".*\"{}\".*".format(status_search), test.dut.at1.last_response))
        if status_not_search_list:
            for status_not_search in status_not_search_list:
                test.log.info("Expected REGEX: {}".format(status_not_search))
                test.expect(not re.search(".*\"{}\".*".format(status_not_search), test.dut.at1.last_response))

    def delete_messages_with_deflag(test, deflag):
        test.log.info("*** Delete message with deflag: {} ***".format(deflag))
        test.expect(test.dut.at1.send_and_verify("AT+CMGD=1,{}".format(deflag), ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()

