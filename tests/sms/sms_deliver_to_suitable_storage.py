# responsible: malgorzata.kaluza@globallogic.com, renata.bryla@globallogic.com
# location: Wroclaw
# TC0011215.001, TC0011215.003

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages, dstl_delete_sms_message_from_index
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_get_current_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """TC0011215.001 / TC0011215.003 - SmsDeliverToSuitableStorage

    Send a series of SMS to device and ensure that it is received into the correct default storage (SIM)

    The following scenarios are executed:
    0) Check available memories on DUT (for <mem1>, <mem2>, <mem3>).
    1a) ME storage is set as <mem2> (for writing & sending), SMS is written on <mem2>. Read written SMS.
    1b) SM storage is set as <mem2> (for writing & sending), SMS is written on <mem2>. Read written SMS.
    2) ME storage is set as <mem1> (for listening and deleting) and MT/ME for <mem3> (for incoming SMSes).
    CNMI=2,1 is set.
    - If module does not support MT memory, ME will be used instead.
    - Please perform sending, receiving and reading for SMS Class 0, 1, 2, 3 and none.
    3) (Only if SSMSS command is supported).
    Valid and invalid parameters of at^ssmss command are set.
    4) (Only if SSMSS command is supported).
    ME is listed, then numeration of MT/ME (depending on support for MT memory) is changed (at^ssmss=1) and storage for
    listening is changed to SM, SM is listed.
    5) Deleting of all SMSes (on SM and ME).
    6) SM storage is set as <mem1> (for listening and deleting) and SM for <mem3> (for incoming SMSes), then SM is
    listed. CNMI=2,1 is set.
    - Please perform sending, receiving and reading for SMS Class 0, 1, 2, 3 and none.
    7) Deleting of all SMSes (on SM and ME).

    On all DUTs (eg. Quinn) where functionality of at^ssmss does not exist. TC results should be checked according to
    AT-SPEC
    """
    memory1 = []
    memory2 = []
    memory3 = []
    cmgw_mem_index = 0
    timeout_value = 360

    def setup(test):
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step("0) Check available memories on DUT (for <mem1>, <mem2>, <mem3>).")
        test.save_memory_settings()

        test.log.step("1a) ME storage is set as <mem2> (for writing & sending), SMS is written on <mem2>. Read written "
                      "SMS.")
        test.set_memories_via_cpms("SM", "ME", "SM")
        test.write_sms_and_check_memory("No class", "SM_MEM1_MEM3")
        test.set_memories_via_cpms("ME", "ME", "ME")
        test.read_and_delete_sms_check_memory("ME_ALL_MEM")

        test.log.step("1b) SM storage is set as <mem2> (for writing & sending), SMS is written on <mem2>. Read written "
                      "SMS.")
        test.set_memories_via_cpms("ME", "SM", "ME")
        test.write_sms_and_check_memory("No class", "ME_MEM1_MEM3")
        test.set_memories_via_cpms("SM", "SM", "SM")
        test.read_and_delete_sms_check_memory("SM_ALL_MEM")

        test.log.step("2) ME storage is set as <mem1> (for listening and deleting) and MT/ME for <mem3> "
                      "(for incoming SMSes.). CNMI=2,1 is set.")
        test.log.info("- If module does not support MT memory, ME will be used instead.")
        test.log.info("- Please perform sending, receiving and reading for SMS Class 0, 1, 2, 3 and none.")
        test.set_appropriate_mem1_and_mem3("ME", False)
        test.send_and_receive_sms_different_class(2, "ME")

        test.log.step("3) (Only if SSMSS command is supported). Valid and invalid parameters of at^ssmss command are "
                      "set (if supported)")
        test.log.info("***   COMMAND NOT SUPPORTED   ***")

        test.log.step("4) (Only if SSMSS command is supported) ME is listed, then numeration of MT/ME "
                      "(depending on support for MT memory) is changed (at^ssmss=1) and storage for "
                      "listening is changed to SM, SM is listed.")
        test.log.info("***   COMMAND NOT SUPPORTED   ***")

        test.log.step("5) Deleting of all SMSes (on SM and ME).")
        test.delete_sms_on_sm_and_me(test.dut)

        test.log.step("6) SM storage is set as <mem1> (for listening and deleting) and SM for <mem3> "
                      "(for incoming SMSes), then SM is listed. CNMI=2,1 is set.")
        test.log.info("- Please perform sending, receiving and reading for SMS Class 0, 1, 2, 3 and none.")
        test.set_appropriate_mem1_and_mem3("SM", True)
        test.send_and_receive_sms_different_class(6, "SM")

        test.log.step("7) Deleting of all SMSes (on SM and ME).")
        test.delete_sms_on_sm_and_me(test.dut)

    def cleanup(test):
        test.restore_values(test.dut)
        test.restore_values(test.r1)

    def save_memory_settings(test):
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=?", ".*OK.*"))
        memories = test.expect(re.search(r'.*CPMS: (\(.*\)),(\(.*\)),(\(.*\)).*', test.dut.at1.last_response))
        if memories is not None:
            test.memory1.append(memories.group(1).strip())
            test.memory2.append(memories.group(2).strip())
            test.memory3.append(memories.group(3).strip())

    def set_memories_via_cpms(test, mem1, mem2, mem3):
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=\"{}\",\"{}\",\"{}\"".format(mem1, mem2, mem3), ".*OK.*"))

    def write_sms_and_check_memory(test, sms_text, set_memories):
        test.cmgw_mem_index = test.write_sms_to_memory_via_cmgw(sms_text)
        test.check_memories_content_via_cpms_read_command(0, 1, 0, set_memories)

    def write_sms_to_memory_via_cmgw(test, text):
        test.expect(dstl_write_sms_to_memory(test.dut, text))
        return test.get_sms_index("CMGW")

    def get_sms_index(test, command):
        response_content = test.expect(re.search(".*{}: (.*)".format(command), test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("SMS index for command {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get {} value".format(command))

    def check_memories_content_via_cpms_read_command(test, index1, index2, index3, set_memories):
        test.expect(dstl_get_current_sms_memory(test.dut))
        if set_memories == "SM_MEM1_MEM3":
            test.log.info("expected phrase: .*\"SM\",{},\d{{1,3}},\"ME\",{},\d{{1,3}},\"SM\",{},\d{{1,3}}.*"
                          .format(index1, index2, index3))
            test.expect(re.search(r".*\"SM\",{},\d{{1,3}},\"ME\",{},\d{{1,3}},\"SM\",{},\d{{1,3}}.*"
                                  .format(index1, index2, index3), test.dut.at1.last_response))
        elif set_memories == "ME_MEM1_MEM3":
            test.log.info("expected phrase: .*\"ME\",{},\d{{1,3}},\"SM\",{},\d{{1,3}},\"ME\",{},\d{{1,3}}.*"
                          .format(index1, index2, index3))
            test.expect(re.search(r".*\"ME\",{},\d{{1,3}},\"SM\",{},\d{{1,3}},\"ME\",{},\d{{1,3}}.*"
                                  .format(index1, index2, index3), test.dut.at1.last_response))
        elif set_memories == "ME_ALL_MEM":
            test.log.info("expected phrase: .*\"ME\",{},\d{{1,3}},\"ME\",{},\d{{1,3}},\"ME\",{},\d{{1,3}}.*"
                          .format(index1, index2, index3))
            test.expect(re.search(r".*\"ME\",{},\d{{1,3}},\"ME\",{},\d{{1,3}},\"ME\",{},\d{{1,3}}.*"
                                  .format(index1, index2, index3), test.dut.at1.last_response))
        elif set_memories == "SM_ALL_MEM":
            test.log.info("expected phrase: .*\"SM\",{},\d{{1,3}},\"SM\",{},\d{{1,3}},\"SM\",{},\d{{1,3}}.*"
                          .format(index1, index2, index3))
            test.expect(re.search(r".*\"SM\",{},\d{{1,3}},\"SM\",{},\d{{1,3}},\"SM\",{},\d{{1,3}}.*"
                                  .format(index1, index2, index3), test.dut.at1.last_response))

    def read_sms_from_index(test, sms_index):
        if sms_index or str(sms_index) == '0':
            test.expect(dstl_read_sms_message(test.dut, sms_index))
            test.expect(re.search(r".*No class.*", test.dut.at1.last_response))
        else:
            test.expect(False, msg="Message not in memory")

    def read_and_delete_sms_check_memory(test, set_memories):
        test.read_sms_from_index(test.cmgw_mem_index)
        test.expect(dstl_delete_sms_message_from_index(test.dut, test.cmgw_mem_index))
        test.check_memories_content_via_cpms_read_command(0, 0, 0, set_memories)

    def send_and_receive_sms(test, sms_text, urc_received, sub_point_b_d_e, step_number):
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, sms_text))
        if sub_point_b_d_e:
            if "MT" in test.memory3[0] and step_number == 2:
                test.expect(dstl_check_urc(test.dut, ".*\+CMTI: \"MT\".*", test.timeout_value))
            elif "ME" in test.memory3[0] and step_number == 2:
                test.expect(dstl_check_urc(test.dut, ".*\+CMTI: \"ME\".*", test.timeout_value))
            else:
                test.expect(dstl_check_urc(test.dut, ".*\+CMTI: \"SM\".*", test.timeout_value))
        else:
            test.expect(dstl_check_urc(test.dut, urc_received, test.timeout_value))
        test.set_cnmi()

    def send_and_receive_sms_different_class(test, step_number, set_memory):
        test.log.step("{}.a sending and receiving SMS_CLASS0 for at+cnmi=2,1 set on: DUT".format(str(step_number)))
        test.set_and_check_dcs_via_csmp(240)
        test.send_and_receive_sms("0 class", ".*CMT:.*", False, step_number)

        test.log.step("{}.b sending and receiving SMS_CLASS1 for at+cnmi=2,1 set on: DUT".format(str(step_number)))
        test.set_and_check_dcs_via_csmp(241)
        test.send_and_receive_sms("1 class", "", True, step_number)

        test.log.step("{}.c sending and receiving SMS_CLASS2 for at+cnmi=2,1 set on: DUT".format(str(step_number)))
        test.set_and_check_dcs_via_csmp(242)
        test.send_and_receive_sms("2 class", ".*\+CMTI: \"SM\".*", False, step_number)

        test.log.step("{}.d sending and receiving SMS_CLASS3 for at+cnmi=2,1 set on: DUT".format(str(step_number)))
        test.set_and_check_dcs_via_csmp(243)
        test.send_and_receive_sms("3 class", "", True, step_number)

        test.log.step("{}.e sending and receiving SMS_CLASS_NONE for at+cnmi=2,1 set on: DUT".format(str(step_number)))
        test.set_and_check_dcs_via_csmp(0)
        test.send_and_receive_sms("No class", "", True, step_number)

        test.log.step("{}.f verify received messages".format(str(step_number)))
        test.set_memories_via_cpms(set_memory, set_memory, set_memory)
        if step_number == 2:
            test.verify_received_messages(".*1 class.*3 class.*No class.*OK", 3)
        else:
            test.verify_received_messages(".*1 class.*2 class.*3 class.*No class.*OK", 4)

    def set_cnmi(test):
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

    def set_and_check_dcs_via_csmp(test, dcs):
        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs), ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CSMP?", ".*CSMP: 17,167,0,{}[\r\n].*OK".format(str(dcs))))

    def verify_received_messages(test, expected_response, sms_number):
        test.expect(test.dut.at1.send_and_verify("AT+CMGL=\"ALL\"", expected_response))
        if sms_number == 3:
            test.log.info("*** Check if messages class 0 and 2 are NOT in memory ***")
            test.expect(not re.search(".*0 class.*2 class.*", test.dut.at1.last_response))
        else:
            test.log.info("*** Check if message class 0 is NOT in memory ***")
            test.expect(not re.search(".*0 class.*", test.dut.at1.last_response))
        test.log.info("*** Check if the correct number of messages is saved in memory ***")
        test.log.info("*** Expected {} messages ***".format(str(sms_number)))
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == sms_number)

    def delete_sms_on_sm_and_me(test, module):
        test.set_memories_via_cpms("SM", "SM", "SM")
        test.expect(dstl_delete_all_sms_messages(module))
        test.set_memories_via_cpms("ME", "ME", "ME")
        test.expect(dstl_delete_all_sms_messages(module))

    def set_appropriate_mem1_and_mem3(test, memory, step6):
        if step6:
            test.set_memories_via_cpms(memory, "ME", "SM")
        else:
            if "MT" in test.memory3[0]:
                test.log.info("\"MT\" memory supported for mem3")
                test.set_memories_via_cpms(memory, "SM", "MT")
            else:
                test.log.info("\"MT\" memory NOT supported for mem3")
                test.set_memories_via_cpms(memory, "SM", "ME")
        test.set_cnmi()

    def restore_values(test, module):
        test.delete_sms_on_sm_and_me(module)
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        if module == test.dut:
            test.delete_sms_on_sm_and_me(test.dut)
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
