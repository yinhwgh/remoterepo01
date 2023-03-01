#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095583.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0095583.001    MessageReferenceNumberAfterModuleRestartText3GPP

    To check if TP Message Reference number (<mr>) has correct value after module restart. 3GPP standard.

    Check the following scenario:
    1. Set text mode on the module. Be sure that module operates in 3gpp standard.
    2. Send one sms directly (at+cmgs).
    3. Write to SM and ME memory one sms.
    4. Send them from memory. (at+cmss)
    5. Restart module
    6. Set again text mode on the module and send sms directly (at+cmgs).
    7. Send sms from SM and ME memory (saved before restart) (at+cmss)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_register_to_network(test.dut)
        test.delete_sms_from_selected_memory(["SM", "ME"])
        test.prepare_module("Preparing module to test")
        test.max_ref_number = dstl_get_sms_memory_capacity(test.dut, 1)
        test.log.info("Max Message Reference Number equals: {}".format(test.max_ref_number))
        test.sms_timeout = 300

    def run(test):
        test.log.step("Check the following scenario:")
        test.log.step("1. Set text mode on the module. Be sure that module operates in 3gpp standard.")
        test.expect(dstl_select_sms_message_format(test.dut))

        test.log.step("2. Send one sms directly (at+cmgs)")
        msg_ref_num_1 = test.send_sms_directly("SMS directly 1")
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))

        test.log.step("3. Write to SM and ME memory one sms.")
        test.log.info("Write SMS to memory SM")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        cmgw_sm_memory = test.write_sms_to_memory("SMS memory SM")
        test.log.info("Write SMS to memory ME")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        cmgw_me_memory = test.write_sms_to_memory("SMS memory ME")

        test.log.step("4. Send them from memory. (at+cmss)")
        test.log.info("Send SMS from memory SM")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        msg_ref_num_2 = test.send_sms_from_memory(cmgw_sm_memory)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
        test.compare_ref_numbers(msg_ref_num_2, msg_ref_num_1, test.max_ref_number)
        test.log.info("Send SMS from memory ME")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        msg_ref_num_3 = test.send_sms_from_memory(cmgw_me_memory)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
        test.compare_ref_numbers(msg_ref_num_3, msg_ref_num_2, test.max_ref_number)

        test.log.step("5. Restart module")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.prepare_module("Preparing module to test after restart")

        test.log.step("6. Set again text mode on the module and send sms directly (at+cmgs).")
        msg_ref_num_4 = test.send_sms_directly("SMS directly 2")
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
        test.compare_ref_numbers(msg_ref_num_4, msg_ref_num_3, test.max_ref_number)

        test.log.step("7. Send sms from SM and ME memory (saved before restart) (at+cmss)")
        test.log.info("Send SMS from memory SM")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        msg_ref_num_5 = test.send_sms_from_memory(cmgw_sm_memory)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
        test.compare_ref_numbers(msg_ref_num_5, msg_ref_num_4, test.max_ref_number)
        test.log.info("Send SMS from memory ME")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        msg_ref_num_6 = test.send_sms_from_memory(cmgw_me_memory)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout))
        test.compare_ref_numbers(msg_ref_num_6, msg_ref_num_5, test.max_ref_number)

    def cleanup(test):
        test.delete_sms_from_selected_memory(["SM", "ME"])
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def prepare_module(test, text):
        test.log.info(text)
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))

    def delete_sms_from_selected_memory(test, memory):
        for mem in memory:
            test.log.info("Delete SMS from memory {}".format(mem))
            dstl_set_preferred_sms_memory(test.dut, mem)
            dstl_delete_all_sms_messages(test.dut)

    def send_sms_directly(test, text):
        test.expect(dstl_send_sms_message(test.dut, test.dut.sim.int_voice_nr, text))
        return test.get_sms_index("CMGS")

    def write_sms_to_memory(test, text):
        test.expect(dstl_write_sms_to_memory(test.dut, text))
        return test.get_sms_index("CMGW")

    def send_sms_from_memory(test, index):
        test.expect(dstl_send_sms_message_from_memory(test.dut, index))
        return test.get_sms_index("CMSS")

    def get_sms_index(test, command):
        response_content = test.expect(re.search(".*{}: (.*)".format(command), test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for command {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get {} value".format(command))

    def compare_ref_numbers(test, ref_number_next, ref_number_prev, max_number):
        test.log.info("Compare Reference Number of messages - check if the counter has increased by 1")
        test.log.info("Current Message Reference Number equals: {}".format(ref_number_next))
        test.log.info("Previous Message Reference Number equals: {}".format(ref_number_prev))

        if ref_number_prev and max_number and ref_number_prev == max_number:
            test.log.info("Max counter of Message Reference Number has been reached !")
            test.log.info("Check if Next Message Reference Number is equal to 0")
            if test.expect(ref_number_next == 0):
                test.log.info("Message reference number is set to 0 !")
            else:
                test.log.info("Message reference number NOT set to 0 !")
        else:
            if test.expect(ref_number_next is not None and ref_number_prev is not None
                           and ref_number_next == ref_number_prev + 1):
                test.log.info("Message Reference Number has been successfully increased by 1")
            else:
                if ref_number_next is not None and ref_number_prev is not None:
                    test.log.info("Message Reference Number has not been increased by 1")
                else:
                    test.log.error("Message Reference Numbers were not found correctly")


if "__main__" == __name__:
    unicorn.main()