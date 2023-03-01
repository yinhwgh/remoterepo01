#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0011197.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory


class Test(BaseTest):
    """
    TC0011197.001    SmsMEWriteDeleteText

    To test write maximum number of SMSs to ME storage in text mode.

    1. Write SMS to ME SMS storage location until storage is full
    2. Delete SMS one by one
    3. Repeat steps 1-2 in a loop of 20 iteration.
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(15)  # waiting for module to get ready
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_set_preferred_sms_memory(test.dut, 'ME'))
        dstl_delete_all_sms_messages(test.dut)

    def run(test):
        start_index = 0
        capacity = 255
        iteration = 1
        while iteration < 21:
            test.log.info('Iteration: {}'.format(iteration))
            test.log.step("1. Write SMS to ME SMS storage location until storage is full")
            test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
            index = start_index
            while index < capacity:
                test.log.info('Writing message no. {}'.format(index))
                test.expect(dstl_write_sms_to_memory(test.dut, 'SMS message {}'.format(index)))
                index += 1
            test.expect(test.dut.at1.send_and_verify
                        ("AT+CPMS?", ".*[+]CPMS: \"ME\",{0},{0},\"ME\",{0},{0},\"ME\",{0},{0}.*".format(capacity)))

            test.log.step("2. Delete SMS one by one")
            index = start_index
            while index < capacity:
                test.expect(test.dut.at1.send_and_verify("AT+CMGD={}".format(index), ".*OK.*"))
                index += 1

            iteration += 1
            if iteration < 21:
                test.log.step("3. Repeat steps 1-2 in a loop of 20 iteration")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))


if "__main__" == __name__:
    unicorn.main()
