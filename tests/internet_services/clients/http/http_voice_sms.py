#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0011788.001, TC0011788.002

import unicorn
import re
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_functions import dstl_enable_sms_urc


class Test(BaseTest):
    """ Download different sizes of http-data and setup voice call / send/receive SMS on different MUX interfaces. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.http_server = HttpServer("IPv4", test_duration=5)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.dut.at1.close()
        if test.dut.project.upper() == "SERVAL":
            mux_interface = 'dut_mux_2'
        else:
            mux_interface = 'dut_mux_3'
        test.remap({'dut_at1': mux_interface})
        test.prepare_sms_support(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_register_to_network(test.r1)
        test.prepare_sms_support(test.r1)
        test.iterations = 50

    def run(test):
        test.log.info("Executing script for test case: 'TC0011788.001/002 HttpVoiceSms'")

        test.log.step("During http download setup voice call / send/receive SMS in parallel according to steps below:")

        test.log.step("Http part - repeat on MUX1:")
        test.thread(test.execute_http_service)
        test.sleep(10)
        test.http_thread_continue = True

        test.log.step("Voice call part - execute 50 times on MUX2:")
        for iteration in range(1, test.iterations + 1):
            test.execute_voice_call(iteration)

        test.log.step("SMS part - execute 50 times - execute on MUX3 (if not supported use MUX2 instead):")
        for iteration in range(1, test.iterations+1):
            test.execute_sms_exchange(iteration)
            if iteration%10 == 0:
                test.expect(dstl_delete_all_sms_messages(test.r1))
        test.http_thread_continue = False

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.http_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("HTTP profile object was not created.")
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.dut.mux_1.close()
        test.dut.mux_2.close()
        if not test.dut.project.upper() == "SERVAL":
            test.dut.mux_3.close()


    def execute_http_service(test):
        data_amount = 100
        for iteration in range(200):
            data_packages = 20 + iteration*5
            test.log.step("1h) Define and open HTTP service profile (different sizes of http-data) "
                          "\r\nIteration no {}.".format(iteration))
            test.http_client = HttpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), http_command="get",
                                           device_interface='mux_1', host=test.http_server.dstl_get_server_ip_address(),
                                           port=test.http_server.dstl_get_server_port(),
                                           http_path='bytes/{}'.format(data_amount*data_packages))
            test.http_client.dstl_generate_address()
            test.expect(test.http_client.dstl_get_service().dstl_load_profile())

            test.expect(test.http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=80))

            test.log.step("2h) Download data as long as data available for reading. "
                          "\r\nIteration no {}.".format(iteration))
            test.expect(test.http_client.dstl_get_service().dstl_read_all_data(data_amount))
            test.expect(test.http_client.dstl_get_parser().dstl_get_service_data_counter('rx') == data_amount*data_packages)

            test.log.step("3h) Close connection and wait 30 seconds. \r\nIteration no {}.".format(iteration))
            test.dut.mux_1.read()
            test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())
            test.sleep(30)
            if not test.http_thread_continue:
                break


    def execute_voice_call(test, iteration):
        test.log.step("1v) Establish a voice call (MO) to the other module. "
                      "\r\nIteration no {} of {}.".format(iteration, test.iterations))
        test.expect(test.dut.mux_2.send_and_verify('ATD{};'.format(test.r1.sim.int_voice_nr)))
        if test.expect(test.r1.at1.wait_for("RING")):
            test.log.step("2v) Other module accepts the call, after 60 sec hangs up the call, wait 90 sec "
                          "for the next call. \r\nIteration no {} of {}.".format(iteration, test.iterations))
            test.expect(test.r1.at1.send_and_verify("ATA", "OK"))
            test.sleep(60)
        test.expect(test.r1.at1.send_and_verify("AT+CHUP", "OK"))
        test.expect(test.dut.mux_2.wait_for("NO CARRIER"))
        test.sleep(90)


    def prepare_sms_support(test, module):
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_set_preferred_sms_memory(module))
        test.expect(dstl_set_sms_center_address(module))
        test.expect(dstl_enable_sms_urc(module))
        test.expect(module.at1.send_and_verify('AT+CSMP=17,167,0,0', '.*OK.*'))

    def execute_sms_exchange(test, iteration):
        test.log.step("1s) DUT receive SMS from the second module. "
                      "\r\nIteration no {} of {}.".format(iteration, test.iterations))
        test.send_and_receive_sms(iteration, test.r1, test.dut)
        test.log.step("2s) DUT send SMS to the second module. "
                      "\r\nIteration no {} of {}.".format(iteration, test.iterations))
        test.send_and_receive_sms(iteration, test.dut, test.r1)

    def send_and_receive_sms(test, iteration, sender, receiver):
        ready_to_send = sender.at1.send_and_verify('AT+CMGS="{}"'.format(receiver.sim.int_voice_nr), ".*>.*", wait_for=".*>.*")
        if ready_to_send:
            test.expect(sender.at1.send_and_verify('SMS no. {}'.format(iteration), end="\u001A", expect=".*OK.*", timeout=120))
        else:
            test.expect(False, msg="Fail to send SMS")
        test.expect(dstl_check_urc(sender, ".*CMGS.*"))
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=200))
        sms_received = re.search(r"CMTI.*\",\s*(\d)", receiver.at1.last_response)
        if test.expect(sms_received, msg="SMS was not received."):
            test.expect(dstl_read_sms_message(receiver, sms_received[1]))


if "__main__" == __name__:
    unicorn.main()
