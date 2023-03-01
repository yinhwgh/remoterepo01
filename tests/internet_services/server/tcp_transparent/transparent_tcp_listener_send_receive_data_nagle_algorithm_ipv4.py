# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0103469.001 TC0103469.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar, \
    dstl_switch_to_command_mode_by_pluses
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.packet_domain.select_printing_ip_address_format import \
    dstl_select_printing_ip_address_format


class Test(BaseTest):
    """	To test Nagle algorithm for TCP listener"""

    def setup(test):
        test.ip_version = "IPv4"
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_enter_pin(test.dut))
        test.echo_server = EchoServer(test.ip_version, "TCP", extended=True)
        test.timeout = 180
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.length = 0
        dstl_select_printing_ip_address_format(test.dut, 1)

    def run(test):

        test.log.info("netcat is used instead of remote module")
        test.log.step("1. Define and activate internet connection.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True,
                                                                ip_version=test.ip_version)
        test.expect(connection_setup_dut.
                    dstl_load_and_activate_internet_connection_profile())
        nagle_timer = [0, 200, 400]
        for timer in nagle_timer:

            test.log.step("2. Define transparent TCP client on Remote.")
            test.log.info("netcat is used instead of remote module")

            test.log.step(r'3. Define TCP listener on DUT and set "timer" parameter to 0ms.')
            localport = "8888"
            test.socket_dut = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp", bufsize=1460,
                                            nagle_timer=str(timer), etx_char=26, host="listener",
                                            ip_version=test.ip_version, localport=localport)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

            test.log.step("4. Start collecting Wireshark IP traffic logs.")
            test.log.info("Starting trace will be done after opening the profile")

            test.log.step("5. Open services - firstly open Listener then client and wait for "
                          "proper URC.")
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(
                test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            if timer == 0:
                dut_ip_address_and_port = test.socket_dut.dstl_get_parser().\
                    dstl_get_service_local_address_and_port(ip_version=test.ip_version)
                dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

            test.tcpdump_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                              "sudo timeout {0} tcpdump src {1} -A -i ens3".
                                              format(test.timeout, dut_ip_address),
                                              timeout=test.timeout)
            test.echo_server.dstl_run_ssh_nc_process(dut_ip_address, localport)

            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3"))

            test.log.step(
                "6. Establish transparent mode on DUT side and wait for proper URC.")
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("7. Send 5 bytes from DUT to Remote every 100 ms. Total amount of data: "
                          "500B.")
            data_block_size = 5
            amount_of_data_blocks = 100
            data = dstl_generate_data(data_block_size)
            test.socket_dut.dstl_get_service().dstl_send_data(data, expected="",
                                                              repetitions=amount_of_data_blocks)

            test.log.step("8. Switch to command mode.")
            test.sleep(5)
            test.expect(
                dstl_switch_to_command_mode_by_pluses(test.dut))
            if not test.expect(test.socket_dut.dstl_get_service().
                                       dstl_check_if_module_in_command_mode()):
                test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

            test.log.step("9. Check socket state and compare transmitted / received data.")
            test.expect(
                test.socket_dut.dstl_get_parser().dstl_get_socket_state() ==
                SocketState.SERVER.value)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("TX") ==
                        data_block_size*amount_of_data_blocks)

            test.log.step("10. Close the services and save Wireshark log.")
            test.log.info("Echo server is used instead of remote module")
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

            test.tcpdump_thread.join()
            test.echo_server.dstl_stop_ssh_nc_process()

            test.log.info("TCPDUMP RESPONSE:")
            test.log.info(test.echo_server.linux_server_response)
            response_list = list(test.echo_server.linux_server_response.split("\n"))
            proper_size = 0
            wrong_size = 0
            if timer == 0:
                timer = 200
                test.log.info(test.length)

            test.length = int(timer * data_block_size / 200)

            for line in response_list:
                if "length {}".format(test.length) in line:  # 200 because time
                    # between sending each packet is about 200 ms if delay is set to 100 ms
                    proper_size = proper_size+1
                elif "length" in line:
                    wrong_size = wrong_size+1

            test.log.info("Searched packet length is {}".format(test.length))
            test.log.info("Correct packet size amount: {}, Wrong packet size amount: {}".format(
                proper_size, wrong_size))
            test.expect(proper_size >= (wrong_size+proper_size)*0.8)

            if timer is not 400:
                test.log.step("11. Repeate steps for Nagle timer 200ms and 400ms.")

        test.log.step("12. Analize IP traffic Wireshark logs.")
        test.log.info("Log analyzed in each iteration of step 10")

    def cleanup(test):
        try:
            test.echo_server.dstl_server_close_port()
            test.echo_server.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
