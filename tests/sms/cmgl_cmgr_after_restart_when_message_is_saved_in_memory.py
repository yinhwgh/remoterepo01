#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0103914.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory, dstl_get_current_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """TC0103914.001    CmglCmgrAfterRestartWhenMessageIsSavedInMemory

    The goal of the TC is to check if it is possible read and list SMS after restart module when message is saved
     in memory

    This scenario cover the issue IPIS100268926 and its next FUPs:

    1. Enable phase 2+ for SMS: AT+CSMS=1
    2. Set Text mode: AT+CMGF=1
    3. Set ME on all memories: AT+CPMS="ME","ME","ME"
    4. Write short message to the memory: AT+CMGW
    5. Check SMS message storage (number of stored messages): AT+CPMS?
    6. Restart module
    7. Register module to the network
    8. Check SMS message storage (number of stored messages): AT+CPMS? (If power-up values in at+cpms different
       than memory used before restart set proper SMS memories once again - "ME" for 1st TC loop, "SM" for 2nd TC loop )
    9. Set PDU mode: AT+CMGF=0
    10. List SMS messages from storage: AT+CMGL=4
    11. Read saved message: AT+CMGR=<index>
    12. Set text mode: AT+CMGF=1
    13. List SMS messages from storage: AT+CMGL="all"
    14. Read saved message: AT+CMGR=<index>
    15. Delete message from memory
    16. Set SM on all memories: AT+CPMS="SM","SM","SM"
    17. Repeat steps 4-14
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_get_imei(test.dut))
        test.expect(dstl_get_bootloader(test.dut))
        for memory in ["ME", "SM"]:
            test.expect(dstl_set_preferred_sms_memory(test.dut, memory))
            test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
        test.log.step("1. Enable phase 2+ for SMS: AT+CSMS=1")
        test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))

        test.log.step("2. Set Text mode: AT+CMGF=1")
        test.expect(dstl_select_sms_message_format(test.dut))

        test.log.step("3. Set ME on all memories: AT+CPMS=\"ME\",\"ME\",\"ME\"")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))

        for memory in ["ME", "SM"]:
            test.log.step("4. Write short message to the memory: AT+CMGW")
            test.expect(dstl_write_sms_to_memory(test.dut, "SMS in {} memory".format(memory), "TEXT"))
            sms_index = re.search(r".*CMGW: (\d{1,3})", test.dut.at1.last_response)

            test.log.step("5. Check SMS message storage (number of stored messages): AT+CPMS?")
            test.expect(dstl_get_current_sms_memory(test.dut))
            test.expect(re.search(r".*\"{}\",1.*".format(memory), test.dut.at1.last_response))

            test.log.step("6. Restart module")
            test.expect(dstl_restart(test.dut))

            test.log.step("7. Register module to the network")
            test.expect(dstl_register_to_network(test.dut))

            test.log.step("8. Check SMS message storage (number of stored messages): AT+CPMS? (If power-up values in "
                          "at+cpms different than memory used before restart set proper SMS memories once again - "
                          "\"ME\" for 1st TC loop, \"SM\" for 2nd TC loop )")
            if dstl_get_current_sms_memory(test.dut) == (memory, memory, memory):
                test.expect(True)
                test.expect(re.search(r".*\"{}\",1.*".format(memory), test.dut.at1.last_response))
            else:
                test.expect(dstl_set_preferred_sms_memory(test.dut, "{}".format(memory)))
                test.expect(re.search(r".*CPMS: 1.*", test.dut.at1.last_response))

            test.log.step("9. Set PDU mode: AT+CMGF=0")
            test.expect(dstl_select_sms_message_format(test.dut, "PDU"))

            test.log.step("10. List SMS messages from storage: AT+CMGL=4")
            test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, 4))
            test.check_correct_sms_content("PDU", memory)

            test.log.step("11. Read saved message: AT+CMGR=<index>")
            if sms_index is not None:
                test.expect(dstl_read_sms_message(test.dut, sms_index.group(1)))
                test.check_correct_sms_content("PDU", memory)
            else:
                test.expect(False, msg="Message not in memory")

            test.log.step("12. Set text mode: AT+CMGF=1")
            test.expect(dstl_select_sms_message_format(test.dut))

            test.log.step("13. List SMS messages from storage: AT+CMGL=\"all\"")
            test.expect(dstl_list_sms_messages_from_preferred_memory(test.dut, "ALL"))
            test.check_correct_sms_content("TEXT", memory)

            test.log.step("14. Read saved message: AT+CMGR=<index>")
            if sms_index is not None:
                test.expect(dstl_read_sms_message(test.dut, sms_index.group(1)))
                test.check_correct_sms_content("TEXT", memory)
            else:
                test.expect(False, msg="Message not in memory")

            test.log.step("15. Delete message from memory")
            test.expect(dstl_delete_all_sms_messages(test.dut))

            if memory != "SM":
                test.log.step("16. Set SM on all memories: AT+CPMS=\"SM\",\"SM\",\"SM\"")
                test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))

                test.log.step("17. Repeat steps 4-14")

    def cleanup(test):
        for memory in ["SM", "ME"]:
            test.expect(dstl_set_preferred_sms_memory(test.dut, memory))
            test.expect(dstl_delete_all_sms_messages(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def check_correct_sms_content(test, sms_format, memory):
        if sms_format == "PDU":
            if memory == "ME":
                test.expect(re.search(r".*D3E6149476839A4550BBDC7ECBF3.*", test.dut.at1.last_response))
            else:
                test.expect(re.search(r".*D3E614947683A64D50BBDC7ECBF3.*", test.dut.at1.last_response))
        else:
            test.expect(re.search(r".*SMS in {} memory.*".format(memory), test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
