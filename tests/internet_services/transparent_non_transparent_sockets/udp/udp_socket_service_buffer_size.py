# responsible dominik.tanderys@globallogic.com
# Wroclaw
# TC0094666.001, TC0094666.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr, \
    dstl_switch_to_command_mode_by_pluses
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.configuration.configure_dtr_line_mode import dstl_set_dtr_line_mode
from dstl.devboard.configure_dtr_detection_devboard import dstl_enable_devboard_dtr_detection

class Test(BaseTest):
    """	This test checks behavior of the module with different buffer sizes and amount of data
    sent with UDP Transparent service."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.h2("Executing script for test case: TC0094666.002 - UDPSocketServiceBufferSize")
        bufsize = ['10', '100', '1460', '0', '1461', "1500", 'lizard', '-1']
        data_short = dstl_generate_data(730)
        test.socket_server = EchoServer("IPv4", "UDP", extended=True)
        test.expect(dstl_set_dtr_line_mode(test.dut, "2"))
        #test.expect(dstl_enable_devboard_dtr_detection(test.dut))

        test.log.step("1. Define and activate internet connection")
        test.expect(dstl_register_to_network(test.dut), critical=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define transparent UDP client on DUT to server with echo response.")
        srv_id = "0"
        test.socket_client = SocketProfile(test.dut, srv_id, test.connection_setup.
                                           dstl_get_used_cid(), ip_server=test.socket_server,
                                           protocol='UDP', etx_char="26", nagle_timer=500)
        test.socket_client.dstl_set_parameters_from_ip_server()
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        for bufsize_value in range(3):
            test.log.info("iteration: {}".format(bufsize_value))
            test.log.step('3. Set up "bufsize" parameter to {}.'.format(bufsize[bufsize_value]))
            test.socket_client.dstl_set_bufsize(bufsize[bufsize_value])
            test.socket_client.dstl_generate_address()
            test.expect(test.socket_client.dstl_get_service().dstl_write_address())

            test.log.step("4. Enable wireshark logging on server side.")
            test.log.info("Executed in next step")

            test.log.step("5. Open client service.")
            test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
            dut_ip_address = test.socket_client.dstl_get_parser() \
                .dstl_get_service_local_address_and_port('IPv4').split(':')[0]
            test.tcpdump_thread = test.thread(test.socket_server.dstl_server_execute_linux_command,
                                              "sudo timeout {0} tcpdump host {1} -A -i ens3".
                                              format(60, dut_ip_address), timeout=60*2)

            test.log.step("6. Establish transparent mode on DUT side and wait for proper URC.")
            test.expect(test.socket_client.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("7. Send 1460 bytes from client to endpoint.")
            test.expect(test.socket_client.dstl_get_service().dstl_send_data(data_short
                                                                             , expected="",
                                                                             repetitions=2,
                                                                             timeout=1))

            test.log.step("8. Switch to command mode by DTR.")
            test.sleep(20)  # so all data can be received and printed on interface
            #if not test.expect(dstl_switch_to_command_mode_by_dtr(test.dut)):
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut), critical=True)

            test.expect(test.socket_client.dstl_get_parser().dstl_get_service_data_counter("rx") >=
                        test.socket_client.dstl_get_parser().dstl_get_service_data_counter("tx")
                        * 0.9)
            test.log.step("9. Close the service.")
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

            test.tcpdump_thread.join()
            response_list = list(test.socket_server.linux_server_response.split("\n"))
            dut_identificator = response_list[2][19:35]
            bufsize_lines = []
            correct_bufsize = 0
            for line in response_list:
                if (dut_identificator in line) and ("bad" not in line) and ("length" in line):
                    length = line.split("length ")[1]
                    bufsize_lines.append(length)
                    if length == bufsize[bufsize_value]:
                        correct_bufsize += 1
            test.expect(correct_bufsize > 0)
            test.expect(correct_bufsize >= len(bufsize_lines)*0.7)
            #for larger bufsizes 0.9 would be something like one datagram, and procedure counts
            #datagrams going both ways

        for bufsize_value in range(3, len(bufsize)):
            test.log.info("iteration: {}".format(bufsize_value))
            test.log.step('3. Set up "bufsize" parameter to {}.'.format(bufsize[bufsize_value]))
            test.socket_client.dstl_set_bufsize(bufsize[bufsize_value])
            test.socket_client.dstl_generate_address()
            test.expect(not test.socket_client.dstl_get_service().dstl_write_address())

    def cleanup(test):
        try:
            test.tcpdump_thread.join()
        except AttributeError:
            test.log.error("Problem with tcpdump thread, possibly already closed")
        try:
            test.socket_server.dstl_server_close_port()
            test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        if not (test.socket_client.dstl_get_service().dstl_check_if_module_in_command_mode()):
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
