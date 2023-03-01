#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0104087.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.network_registration_status import dstl_set_network_registration_urc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0104087.001   ListDifferentClassSms

    Test the function of AT^SMGL with different classes of SMS

    1. Enter PIN and register to the network for both modules.
    2. On DUT set at+cnmi=2,0 (to store all class SMS in memory)
    3. On DUT set text mode: at+cmgf=1 and at+csdh=1
    4. From Remote to DUT send SMS with all classes: None class0,class1,class2,class3,None:
    Due to IPIS276554 and IPIS200155 for Verizon network will be set and send Compressed SMSes
    5. List received SMS with at^smgl command at least 2 times
    """

    def setup(test):
        for device in [test.dut, test.r1]:
            dstl_detect(device)
            dstl_get_bootloader(device)
            dstl_get_imei(device)
            test.clean_sms_on_preferred_memory(device, ["SM", "ME"])
            test.expect(dstl_select_sms_message_format(device))
            test.expect(device.at1.send_and_verify("AT+CSMP=17,167,0,0", r".*OK*"))
            test.expect(device.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
            test.expect(dstl_set_network_registration_urc(device))

    def run(test):
        test.log.step("1. Enter PIN and register to the network for both modules.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2. On DUT set at+cnmi=2,0 (to store all class SMS in memory)")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,0", ".*OK.*"))

        test.log.step("3. On DUT set text mode: at+cmgf=1 and at+csdh=1")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))

        test.log.step("4. From Remote to DUT send SMS with all classes: None class0,class1,class2,class3,None:\n"
                      "Due to IPIS276554 and IPIS200155 for Verizon network will be set and send Compressed SMSes")

        dcs_list = ["0", "16", "17", "19", "18"]
        sms_text = ["None Class", "Class 0", "Class 1", "Class 3", "Class 2"]

        for value in range(len(sms_text)):
            test.log.info("Set an send SMS {}".format(sms_text[value]))
            test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(dcs_list[value]), r".*OK*"))
            test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, "SMS {}".format(sms_text[value]),
                                              "Text"))
        test.log.info("Wait 5 minutes for all SMS to be delivered")
        test.sleep(300)

        test.log.step("5. List received SMS with at^smgl command at least 2 times")
        test.list_received_sms_x_times(5, sms_text[:4])
        test.log.info("=== Check if the correct number of messages is saved in memory ===")
        test.log.info("=== For ME memory expected 4 messages ===")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 4)
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.list_received_sms_x_times(5, sms_text[-1:])
        test.log.info("=== Check if the correct number of messages is saved in memory ===")
        test.log.info("=== For SM memory expected 1 message ===")
        test.expect(dstl_get_sms_count_from_memory(test.dut)[0] == 1)

    def cleanup(test):
        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,0", r".*OK*"))
        test.clean_sms_on_preferred_memory(test.dut, ["SM", "ME"])
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def clean_sms_on_preferred_memory(test, device, memory):
        for mem in memory:
            test.expect(dstl_set_preferred_sms_memory(device, mem))
            test.expect(dstl_delete_all_sms_messages(device))

    def list_received_sms_x_times(test, counter, sms_list):
        for index in range(counter):
            test.expect(test.dut.at1.send_and_verify("AT^SMGL=\"ALL\"", "OK"))
            for sms_class in sms_list:
                regex = ".*\"REC UNREAD\",\".*{}\".*\nSMS {}.*".format(test.r1.sim.nat_voice_nr[-9:], sms_class)
                test.log.info("Expected REGEX: {}".format(regex))
                test.expect(re.search(regex, test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
