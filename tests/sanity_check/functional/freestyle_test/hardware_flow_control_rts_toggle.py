#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0094217.001
#TC0103494.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.serial_interface.config_baudrate import dstl_get_supported_max_baudrate, dstl_set_baudrate, dstl_get_supported_baudrate_list
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.serial_interface.serial_interface_flow_control import dstl_check_flow_control_number_after_set
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.read_sms_message import dstl_read_sms_message


class Test(BaseTest):
    """
    To check if the RTS/CTS hardware flow control works properly on a module serial interface.

    1. Preparation:
    1.1 Enable RTS/CTS control flow on module.
    1.2 Set highest available baudrate.
    1.3 Write SMS to the module memory. Fill the whole memory.
    2. RTS/CTS flow control enabled on the terminal application:
    2.1 On terminal application: open port with enabled RTS/CTS flow control.
    2.2 Send command to List SMS messages from ME memory, multiple times, as fast as possible.
    3. RTS/CTS flow control inactive on terminal application (RTS line controlled manually):
    3.1 For this part of the test the power saving should be disabled forcing module to await commands constantly.
    3.2 Set RTS line inactive.
    3.3 Send command to List SMS messages from ME memory, multiple times.
    3.4 Set RTS line active.
    4.1 Set lowest available baudrate.
    4.2 Repeat part 2 on lowest available baudrate.
    4.3 Repeat part 3 on lowest available baudrate.
    """

    def setup(test):
        test.ITERATIONS = 10
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        test.dut.dstl_select_sms_message_format(sms_format='Text')
        test.dut.dstl_delete_all_sms_messages()
        test.dut.at1.connection.setDTR(True)
        test.dut.at1.connection.setRTS()

        test.log.step("1. Preparation:")
        test.log.step("1.1 Enable RTS/CTS control flow on module.")
        test.expect(test.dut.dstl_check_flow_control_number_after_set(3))

        test.log.step("1.2 Set highest available baudrate.")
        test.expect(test.dut.dstl_set_baudrate(test.dut.dstl_get_supported_max_baudrate(), test.dut.at1))

        test.log.step("1.3 Write SMS to the module memory. Fill the whole memory.")
        fill_sms_memory(test)

    def run(test):
        execute_step_2(test)
        execute_step_3(test)

        test.log.step("4.1 Set lowest available baudrate.")
        test.expect(test.dut.dstl_set_baudrate(get_lowest_baudrate(test), test.dut.at1))

        test.log.step("4.2 Repeat part 2 on lowest available baudrate.")
        execute_step_2(test)

        test.log.step("4.3 Repeat part 3 on lowest available baudrate.")
        execute_step_3(test)

    def cleanup(test):
        test.dut.at1.connection.setRTS()
        test.expect(test.dut.dstl_set_baudrate("115200", test.dut.at1))
        test.dut.at1.reconfigure({"rtscts": False})
        test.dut.dstl_delete_all_sms_messages()


def execute_step_2(test):
    test.log.step("2. RTS/CTS flow control enabled on the terminal application:")
    test.log.step("2.1 On terminal application: open port with enabled RTS/CTS flow control.")
    test.dut.at1.reconfigure({"rtscts": True})

    test.log.step("2.2 Send command to List SMS messages from ME memory, multiple times, as fast as possible.")
    for sms_position in range(test.ITERATIONS):
        test.expect(test.dut.dstl_read_sms_message(sms_position))


def execute_step_3(test):
    test.log.step("3. RTS/CTS flow control inactive on terminal application (RTS line controlled manually):")
    test.dut.at1.reconfigure({"rtscts": False})

    test.log.step("3.1 For this part of the test the power saving should be disabled forcing module to await commands constantly.")
    test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/PwrSave\",\"disabled\"",'O'))

    test.log.step("3.2 Set RTS line inactive.")
    test.dut.at1.connection.setRTS(value=0)

    test.log.step("3.3 Send command to List SMS messages from ME memory, multiple times.")
    for sms_position in range(test.ITERATIONS):
        test.dut.at1.send("AT+CMGR={}".format(sms_position), wait_after_send=5)
        test.expect("OK" not in test.dut.at1.read() and "CMGL" not in test.dut.at1.read())

    test.log.step("3.4 Set RTS line active.")
    test.dut.at1.connection.setRTS()
    test.sleep(30)
    result = re.findall("(\\+CMGR:)", test.dut.at1.read())
    test.expect(len(result) == test.ITERATIONS)


def fill_sms_memory(test):
    memory_index = 1
    test.expect(test.dut.dstl_set_preferred_sms_memory("ME", memory_index=memory_index))
    memory_capacity = int(test.dut.dstl_get_sms_memory_capacity(memory_index))
    for message_index in range(memory_capacity):
        test.expect(test.dut.dstl_write_sms_to_memory(sms_text="Test SMS"))


def get_lowest_baudrate(test):
    ipr_list = test.dut.dstl_get_supported_baudrate_list()
    int_ipr_list = list(map(int, ipr_list))
    return str(min(int_ipr_list))


if "__main__" == __name__:
    unicorn.main()
