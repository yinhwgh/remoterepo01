#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0087771.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.list_sms_message import dstl_list_sms_messages_from_preferred_memory


class Test(BaseTest):
    """
    This TC should check if the Linux MUX driver works properly under Ubuntu x64 operating system.

    Simultaneously on different channels using multiple driver instances:
    1. Send and receive some AT commands (AT, AT^SCFG=?, etc).
    2. Establish a voice and data call with in parallel SMS.
    """

    def setup(test):
        test.expect("x86_64" in test.os.execute('lscpu'), critical=True)
        prepare_module(test, test.dut)
        prepare_module(test, test.r1)

    def run(test):
        test.dut.at1.close()
        test.sleep(10)
        open_mux_channels(test)

        test.log.step("Simultaneously on different channels using multiple driver instances:")
        test.log.step("1. Send and receive some AT commands (AT, AT^SCFG=?, etc).")
        send_commands_simultaneously(test)

        test.log.step("2. Establish a voice and data call with in parallel SMS.")
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Product {} doesn't support voice and data call".format(test.dut.project))
            send_sms_simultaneously(test)
        else:
            test.log.error("Step not implemented for product {}".format(test.dut.project))

        if test.dut.project.upper() == "SERVAL":
            test.log.info("MUX3 channel on product {} is dedicated for GNS engine. Checking GNS engine on MUX3".format(test.dut.project))
            check_gns_engine_simultaneously(test)
        else:
            test.log.error("Step not implemented for product {}".format(test.dut.project))

    def cleanup(test):
        close_mux_channels(test)
        test.dut.at1.open()
        test.sleep(10)
        test.dut.dstl_delete_all_sms_messages()
        test.r1.dstl_delete_all_sms_messages()
        test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","off"', ".*OK.*")
        test.dut.at1.send_and_verify("AT^SGPSC=\"engine\",0", ".*OK.*")
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.r1.at1.send_and_verify("AT&F", ".*OK.*")


def close_mux_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.dut.mux_3.close()
    test.sleep(10)


def open_mux_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.dut.mux_3.open()
    test.sleep(10)


def prepare_module(test, module):
    module.dstl_detect()
    module.dstl_get_imei()
    test.expect(module.dstl_register_to_network())
    module.dstl_select_sms_message_format(sms_format='Text')
    module.dstl_delete_all_sms_messages()
    test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))


def send_commands_simultaneously(test):
    thread_mux_1 = test.thread(send_commands_for_thread, test, test.dut.mux_1, 5)
    thread_mux_2 = test.thread(send_commands_for_thread, test, test.dut.mux_2, 5)
    thread_mux_1.join()
    thread_mux_2.join()


def send_commands_for_thread(test, device, iterations):
    for loop in range(iterations):
        send_commands(test, device)


def send_commands(test, device):
    test.expect(device.send_and_verify("AT", ".*OK.*"))
    test.expect(device.send_and_verify("ATI", ".*OK.*"))
    test.expect(device.send_and_verify("AT^SCFG=?", ".*OK.*"))


def send_sms_simultaneously(test):
    thread_mux_1 = test.thread(send_commands_for_thread, test, test.dut.mux_1, 5)
    thread_mux_2 = test.thread(send_sms_for_thread, test, 5)
    thread_mux_1.join()
    thread_mux_2.join()


def send_sms_for_thread(test, iterations):
    for loop in range(iterations):
        send_sms(test, "Test sms {}.".format(loop))


def send_sms(test, text):
    test.expect(test.dut.mux_2.send_and_verify("AT+CMGF=1", ".*OK.*"))
    test.expect(test.dut.mux_2.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr), ".*>.*", wait_for=".*>.*"))
    test.expect(test.dut.mux_2.send_and_verify(text, end="\u001A", expect=".*OK.*", timeout=30))
    test.expect(test.r1.at1.wait_for(".*CMTI.*", timeout=120))


def check_gns_engine_simultaneously(test):
    thread_mux_1_and_3 = test.thread(check_gns_engine_for_thread, test, 5)
    thread_mux_2 = test.thread(send_commands_for_thread, test, test.dut.mux_2, 5)
    thread_mux_1_and_3.join()
    thread_mux_2.join()


def check_gns_engine_for_thread(test, iterations):
    for loop in range(iterations):
        check_gns_engine(test)


def check_gns_engine(test):
    test.sleep(5)
    test.expect(test.dut.dstl_switch_on_engine())
    test.expect(test.dut.mux_1.send_and_verify('AT^SGPSC="Nmea/Output","on"', ".*OK.*"))
    test.expect(test.dut.mux_3.wait_for(".*GP.*"))
    test.expect(test.dut.mux_1.send_and_verify('AT^SGPSC="Nmea/Output","off"', ".*OK.*"))
    test.expect(test.dut.dstl_switch_off_engine())


if "__main__" == __name__:
    unicorn.main()
