#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0094453.002

import re
import random
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0094453.002    	ConcatStatusReport

    Intention of this TC is to check whether module is able to store and send concatenated SMS
    with status report request.

    Precondition: DUT and RMT logged on to the network, text mode on (at+cmgf=1).

    1. Set the status report request (at+csmp=49)
    2. Set the presentation of incoming URCs for status reports (at+csms=1, and e.g. at+cnmi=2,1,0,1 or 2,1)
    3. Create the concatenated message with more than 160 characters (in total in at least with two segments)
       and store it in the DUT memory (at^scmw=...).
    4. Send the message (segments) to RMT (at+cmss)
    5. Wait for the status report on DUT.
       CDS message should be confirm by CNMA
       In case of status from the memory read it with at+cmgr.
    6. Direct send the message (segments) to the RMT (at^scms=...)
    7. Wait for the status report on DUT
       CDS message should be confirm by CNMA

    Please note that max length of the particular segment for 7bit coded messages is
    153 characters in case of 8 bit reference number and 152 in case of 16 bit reference number <ieia>.
    """

    TIMEOUT = 60
    SMS_TIMEOUT = 360
    LIST_INDEX_CMTI = []
    LIST_MSG_CONTENT = []
    LIST_MSG_CONTENT_SCMS = []
    LIST_INDEX_SCMS = [1, 2]

    def setup(test):
        test.preparation(test.dut)
        test.preparation(test.r1)

    def run(test):
        test.log.h2("Starting TP C0094453.002 ConcatStatusReport")
        test.log.step("Step 1. Set the status report request (at+csmp=49)")
        test.set_sms_text_mode_parameters(test.dut, "49,167,0,0")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*CSMP: 49,167,0,0.*OK.*"))

        test.log.step("Step 2.Set the presentation of incoming URCs for status reports "
                      "(at+csms=1, and e.g. at+cnmi=2,1,0,1 or 2,1)")
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1,0,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", ".*CNMI: 2,1,0,1,.*OK.*"))

        test.log.step("Step 3. Create the concatenated message with more than 160 characters "
                      "(in total in at least with two segments) and store it in the DUT memory (at^scmw=...).")
        test.list_index_scmw = test.save_concat_message()
        test.log.info("===== Check the number of messages in the DUT module memory =====")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 2)

        test.log.step("Step 4. Send the message (segments) to RMT (at+cmss) and "
                      "Step 5. Wait for the status report on DUT. CDS message should be confirm by CNMA. "
                      "In case of status from the memory read it with at+cmgr.")
        test.send_messages(test.list_index_scmw, "CMSS")
        test.check_delivered_messages(test.LIST_INDEX_CMTI, "CMSS")
        test.LIST_INDEX_CMTI.clear()

        test.log.step("Step 6. Direct send the message (segments) to the RMT (at^scms=...) and "
                      "Step 7. Wait for the status report on DUT. CDS message should be confirm by CNMA.")
        test.send_messages(test.LIST_INDEX_SCMS, "SCMS")
        test.check_delivered_messages(test.LIST_INDEX_CMTI, "SCMS")

    def cleanup(test):
        test.restore_values_and_delete_msg(test.dut)
        test.restore_values_and_delete_msg(test.r1)

    def preparation(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(module.at1.send_and_verify("AT+CSCS=\"GSM\"", "OK"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.set_sms_text_mode_parameters(module, "17,167,0,0")
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

    def restore_values_and_delete_msg(test, module):
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(dstl_delete_all_sms_messages(module))

    def set_sms_text_mode_parameters(test, module, parameters):
        test.expect(module.at1.send_and_verify("AT+CSMP={}".format(parameters), ".*OK.*"))

    def prepare_long_message(test):
        text_content = ""
        for i in range(0, 100):
            text_content = text_content + str(random.randint(0, 9))
        return text_content

    def save_concat_message(test):
        list_command_index = []
        for segment in range(1, 3):
            test.log.info("*** write SMS {}/2 ***".format(segment))
            test.expect(test.dut.at1.send_and_verify("AT^SCMW=\"{}\",,\"STO UNSENT\",{},2,8,1"
                                                     .format(test.r1.sim.int_voice_nr, segment), expect=">"))
            text_msg_content = test.prepare_long_message()
            test.expect(test.dut.at1.send_and_verify("{}".format(text_msg_content),
                        end="\u001A", expect=".*OK.*", timeout=test.TIMEOUT))
            test.LIST_MSG_CONTENT.append(text_msg_content)
            list_command_index.append(test.get_sms_index(test.dut, r".*SCMW:\s*(\d{1,3})", "SCMW"))
        return list_command_index

    def send_messages(test, list_index, command):
        if list_index:
            for item in list_index:
                if list_index == test.list_index_scmw:
                    test.expect(dstl_send_sms_message_from_memory(test.dut, item))
                else:
                    test.log.info("*** send SMS {}/2 ***".format(item))
                    test.expect(test.dut.at1.send_and_verify("AT^SCMS=\"{}\",,{},2,8,2".format(test.r1.sim.int_voice_nr,
                                                                                               item), expect=">"))
                    text_msg_content_scms = test.prepare_long_message()
                    test.expect(test.dut.at1.send_and_verify("{}".format(text_msg_content_scms),
                                                             end="\u001A", expect=".*OK.*", timeout=test.TIMEOUT))
                    test.LIST_MSG_CONTENT_SCMS.append(text_msg_content_scms)
                msg_mr = test.get_sms_index(test.dut, r".*{}:\s*(\d{{1,3}})".format(command), command)
                test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.SMS_TIMEOUT))
                test.LIST_INDEX_CMTI.append(test.get_sms_index(test.r1, r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
                test.expect(test.r1.at1.send_and_verify("AT+CPMS?", "OK"))
                test.log.info("===== Wait for the status report on DUT =====")
                test.log.info("===== Expected Message Reference Number (msg_mr): {} =====".format(msg_mr))
                test.expect(dstl_check_urc(test.dut, ".*CDS:\s*\d,{},.*".format(msg_mr), timeout=test.SMS_TIMEOUT))
                test.log.info("===== CDS message should be confirm by CNMA =====")
                test.expect(test.dut.at1.send_and_verify("AT+CNMA", "OK"))
                test.log.info("===== In case of status from the memory read it with at+cmgr. =====")
                test.log.info("===== STATUS REPORTS are NOT saved in memory SR - steps omitted =====")
        test.log.error("Message NOT in memory - index list is empty")

    def check_delivered_messages(test, list_index, command):
        test.log.info("===== Read the delivered messages on the RMT module =====")
        if list_index:
            for item in list_index:
                test.expect(dstl_read_sms_message(test.r1, item))
                if "CMSS" in command:
                    text = test.LIST_MSG_CONTENT[list_index.index(item)]
                else:
                    text = test.LIST_MSG_CONTENT_SCMS[list_index.index(item)]
                test.log.info("Expected REGEX: .*CMGR:.*,100\s*[\n\r]{}.*".format(text))
                test.expect(re.search(r".*CMGR:.*,100\s*[\n\r]{}.*".format(text), test.r1.at1.last_response))
            test.log.info("===== Check the number of messages in the RMT module memory =====")
            if "CMSS" in command:
                exp_msg_nr = 2
            else:
                exp_msg_nr = 4
            test.log.info("===== Expected number of messages in memory (exp_msg_nr): {} =====".format(exp_msg_nr))
            test.expect(dstl_get_sms_count_from_memory(test.r1)[0] == exp_msg_nr)
        test.log.error("Message NOT in memory - index list is empty")

    def get_sms_index(test, module, regex, command):
        response_content = test.expect(re.search(regex, module.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("Index for the {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of: {}".format(command))


if "__main__" == __name__:
    unicorn.main()