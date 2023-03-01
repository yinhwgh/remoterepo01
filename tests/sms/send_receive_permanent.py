# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0010473.001, TC0010473.002

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
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity


class Test(BaseTest):
    """
    TC0010473.001, TC0010473.002   SendReceivePermanent

    Test scenario will be realized as follows:
    send 1000 sms one by one and check if all sms were delivered correctly,
    when the memory is full, read the messages and then delete them.

    1. Send 1000 sms from remote to dut
    2. Send 1000 sms from dut to remote
    """

    SMS_TIMEOUT = 360
    LIST_INDEX_CMTI = []
    LIST_OF_SENT_MESSAGES = []
    LIST_OF_RECEIVED_MESSAGES = []

    def setup(test):
        test.prepare_mode(test.dut, "===== Preparation of DUT module =====")
        test.prepare_mode(test.r1, "===== Preparation of REMOTE module =====")

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0010473.002 SendReceivePermanent")
        else:
            test.log.h2("Starting TP TC0010473.001 SendReceivePermanent")
        test.log.step("Step 1. Send 1000 sms from remote to dut")
        test.execute_test_step(test.r1, test.dut)

        test.log.step("Step 2. Send 1000 sms from dut to remote")
        test.execute_test_step(test.dut, test.r1)

    def cleanup(test):
        test.restore_values(test.dut)
        test.restore_values(test.r1)

    def prepare_mode(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_register_to_network(module), critical=True)
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))

    def restore_values(test, module):
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def get_max_value_of_sms_storage(test, receiver):
        if receiver == test.dut:
            receiver_name = "DUT"
        else:
            receiver_name = "REMOTE"
        test.log.info("Get MAX value of SMS Storage")
        test.MAX_VALUE_OF_SMS_STORAGE = dstl_get_sms_memory_capacity(receiver, 1)
        test.log.info("MAX value of SMS Storage for module {} is: {}".format(receiver_name,
                                                                             test.MAX_VALUE_OF_SMS_STORAGE))
        return test.MAX_VALUE_OF_SMS_STORAGE

    def get_sms_index(test, module, regex, command):
        response_content = test.expect(re.search(regex, module.at1.last_response))
        if response_content:
            msg_index = response_content[1]
            test.log.info("SMS index for {} is: {}".format(command, msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of {}".format(command))

    def execute_test_step(test, sender, receiver):
        test.log.info("===== send 1000 sms one by one and check if all sms were delivered correctly =====")
        test.get_max_value_of_sms_storage(receiver)
        for i in range(1, 1001):
            test.log.info("===== SMS nr: {} =====".format(i))
            test.send_sms(sender, receiver)
            current_value_fo_sms_storage = dstl_get_sms_count_from_memory(receiver)[1]
            test.log.info("CURRENT value of SMS Storage is: {}".format(current_value_fo_sms_storage))
            if int(current_value_fo_sms_storage) == int(test.MAX_VALUE_OF_SMS_STORAGE) or i == 1000:
                if i == 1000:
                    comment = "===== SMS nr 1000 sent, read the messages and then delete them ====="
                else:
                    comment = "===== when the memory is full, read the messages and then delete them ====="
                test.log.info(comment)
                test.read_delivered_messages_via_cmgr(test.LIST_INDEX_CMTI, sender, receiver)
                test.expect(dstl_delete_all_sms_messages(receiver))
                test.LIST_INDEX_CMTI.clear()
        test.compare_number_of_correctly_sent_and_read_messages(sender)

    def send_sms(test, sender, receiver):
        test.expect(sender.at1.send_and_verify('AT+CMGS="{}"'.format(receiver.sim.int_voice_nr), expect=">"))
        test.expect(sender.at1.send_and_verify("Test", end="\u001A", expect=".*OK.*|.*ERROR.*",
                                               timeout=test.SMS_TIMEOUT))
        if dstl_check_urc(sender, ".*CMGS.*"):
            test.LIST_OF_SENT_MESSAGES.append(test.get_sms_index(sender, r".*CMGS:\s*(\d{1,3})", "CMGS"))
            if dstl_check_urc(receiver, ".*CMTI.*", timeout=test.SMS_TIMEOUT):
                test.LIST_INDEX_CMTI.append(test.get_sms_index(receiver, r".*CMTI.*,\s*(\d{1,3})", "CMTI"))
                return test.LIST_INDEX_CMTI
            else:
                return test.log.info("Message was not received")
        else:
            return test.log.info("Message has NOT been sent")

    def read_delivered_messages_via_cmgr(test, index_list, sender, receiver):
        if index_list:
            for item in index_list:
                test.expect(receiver.at1.send_and_verify("AT+CMGR={}".format(item), ".*OK.*"))
                test.log.info("Expected phrase: .*\{}.*(\n|\r){}.*".format(sender.sim.int_voice_nr, "Test"))
                if re.search(".*\{}.*(\n|\r){}.*".format(sender.sim.int_voice_nr, "Test"), receiver.at1.last_response):
                    test.expect(True, msg="Correct message content")
                    test.LIST_OF_RECEIVED_MESSAGES.append(item)
                else:
                    test.log.info("Incorrect message content")
        else:
            test.log.info("Message NOT in memory - index list is empty")

    def compare_number_of_correctly_sent_and_read_messages(test, sender):
        if sender == test.dut:
            sender_name = "DUT"
            receiver_name = "REMOTE"
        else:
            sender_name = "REMOTE"
            receiver_name = "DUT"
        test.log.info("===== COMPARE number of correctly sent and read messages from {} to {} =====".format(
            sender_name, receiver_name))
        number_of_correctly_read_messages = len(test.LIST_OF_RECEIVED_MESSAGES)
        number_of_correctly_send_messages = len(test.LIST_OF_SENT_MESSAGES)
        number_of_not_read_messages = 1000 - len(test.LIST_OF_RECEIVED_MESSAGES)
        number_of_not_send_messages = 1000 - len(test.LIST_OF_SENT_MESSAGES)
        test.log.info("Number of correctly received messages: {}".format(number_of_correctly_read_messages))
        test.log.info("Number of NOT received messages: {}".format(number_of_not_read_messages))
        test.log.info("Number of correctly sent messages: {}".format(number_of_correctly_send_messages))
        test.log.info("Number of NOT sent messages: {}".format(number_of_not_send_messages))
        percent_of_correctly_read_messages = number_of_correctly_read_messages/10
        percent_of_correctly_send_messages = number_of_correctly_send_messages/10
        if test.expect(percent_of_correctly_read_messages > 90 and percent_of_correctly_send_messages > 90):
            test.log.info("Percent of successfully sent messages from {} to {} is greater than 90% - Success".format(
                sender_name, receiver_name))
        else:
            test.log.error("Percent of successfully sent messages from {} to {} is lower than 90% - FAIL".format(
                sender_name, receiver_name))
        test.LIST_OF_RECEIVED_MESSAGES.clear()
        test.LIST_OF_SENT_MESSAGES.clear()


if "__main__" == __name__:
    unicorn.main()
