#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0011198.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0011198.001    SmsMEWriteDeletePDU

    To test write maximum number of SMSs to ME storage in PDU mode.

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
        pdu_payload = '07918406600006F011000B918421436587F90000FF0CD4F29C0E9A36A72028B10A'
        while iteration < 21:
            test.log.info('Iteration: {}'.format(iteration))
            test.log.step("1. Write SMS to ME SMS storage location until storage is full")
            test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
            index = start_index
            while index < capacity:
                test.log.info('Writing message no. {}'.format(index))
                test.expect(test.dut.at1.send_and_verify("AT+CMGW=25", '>'))
                test.expect(test.dut.at1.send_and_verify('{}\x1A'.format(pdu_payload), '.*OK.*'))
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
