#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0010759.001

import unicorn
from core.basetest import BaseTest
import re
import time
from dstl.identification import get_imei
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.sms import auxiliary_sms_functions, sms_configurations, sms_functions, delete_sms, select_sms_format
from dstl.serial_interface import config_baudrate
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.read_sms_message import dstl_read_sms_message


class Test(BaseTest):
    """
    The module shall be able to transfer data at the maximum baud rate through the DCE-DTE interfaces for at least 30 minutes.

    1. Set the max baudrate.
    2. Fill the whole SMS memory.
    3. Read SMS book for 30 minutes.
    4. Return to 115200 baudrate.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        test.dut.dstl_select_sms_message_format(sms_format='Text')
        test.dut.dstl_delete_all_sms_messages()

    def run(test):
        test.log.step("1. Set the max baudrate.")
        max_baudrate = test.dut.dstl_get_supported_max_baudrate()
        test.expect(test.dut.dstl_set_baudrate(max_baudrate, test.dut.at1))

        test.log.step("2. Fill the whole SMS memory.")
        memory_index = 1
        test.expect(test.dut.dstl_set_preferred_sms_memory("ME", memory_index=memory_index))
        memory_capacity = int(test.dut.dstl_get_sms_memory_capacity(memory_index))
        for message_index in range(memory_capacity):
            test.expect(test.dut.dstl_write_sms_to_memory(sms_text="Test SMS"))

        test.log.step("3. Read SMS book for 30 minutes.")
        read_sms_book(test, memory_capacity)

    def cleanup(test):
        test.log.step("4. Return to 115200 baudrate.")
        test.expect(test.dut.dstl_set_baudrate("115200", test.dut.at1))
        test.dut.dstl_delete_all_sms_messages()


def read_sms_book(test, memory_capacity):
    loop_end_time = time.time() + 60 * 30
    while time.time() < loop_end_time:
        for sms_position in range(memory_capacity):
            test.expect(test.dut.dstl_read_sms_message(sms_position))


if "__main__" == __name__:
    unicorn.main()
