# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0093714.001, TC0093715.001, TC0093715.002

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
    """Check the functionality of Nagle timer. Loadtest of data transmission (upload/download)
    in transparent mode."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_enter_pin(test.dut))
        test.echo_server = EchoServer(test.ip_version, "TCP", extended=True)
        test.timeout = 240
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.length = 0
        dstl_select_printing_ip_address_format(test.dut, 1)

    def run(test):
        test.log.h2("Executing test script for: TransparentTCPSendReceiveDataNagleAlgorithm_{}".
                    format(test.ip_version))
        test.log.info("echo server is used instead of remote module")

        test.log.step("1. Attach both modules to the network")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True,
                                                                ip_version=test.ip_version)
        test.expect(connection_setup_dut.
                    dstl_load_and_activate_internet_connection_profile())
        nagle_timer = [0, 200, 400]
        for timer in nagle_timer:

            test.log.step("2. Set up TCP Socket Transparent Client service profile on DUT, "
                          f"using {test.ip_version} protocol stack. Set Nagle algorithm timer to "
                          "[T_n] {0, 200, 400}. Set the buffer size to maximum.")
            test.socket_dut = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp", bufsize=1460, alphabet=1,
                                            nagle_timer=str(timer), etx_char=26,
                                            ip_version=test.ip_version)
            test.socket_dut.dstl_set_parameters_from_ip_server(test.echo_server)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

            test.log.step("3. Set up TCP Socket Transparent Listener service profile on Remote.")
            test.log.info("echo server is used instead of remote module")

            test.log.step("4. Start TCP trace on DUT: use command line parameters to generate "
                          "splitted output log file. Open service on Remote. Open service on DUT "
                          "and check its state.")
            test.log.info("Starting trace will be done after opening the profile")
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(
                test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("5. Establish transparent connection both on the Listener and client.")
            dut_ip_address_and_port = test.socket_dut.dstl_get_parser().\
                dstl_get_service_local_address_and_port(ip_version=test.ip_version)
            dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]
            tcpdump_port = test.echo_server.dstl_get_server_port()

            test.tcpdump_thread = test.thread(test.echo_server.dstl_server_execute_linux_command,
                                              "sudo timeout {0} tcpdump dst port {1} -A -i ens3".
                                              format(test.timeout, tcpdump_port),
                                              timeout=test.timeout)

            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step(
                "6. Send data from TE to DUT in parts smaller than TCP header (e.g. 5 bytes). "
                "Data should be sent with short delay (e.g. 100 ms). Total amount of data: 5kB. "
                "Paralelly receive the data on Remote. Verification of delay between actual "
                "subsequently outgoing TCP packets shall be possible, using recorded TCP trace. "
                "Check size of packets sent out by DUT. Perform TCP trace for whole transmission, "
                "but check Nagle timer operation only for representative samples of transmission.")
            data_block_size = 5
            amount_of_data_blocks = 1024
            data = dstl_generate_data(data_block_size)
            test.expect(test.socket_dut.dstl_get_service().dstl_send_data(data, expected="",
                                                                          repetitions=
                                                                          amount_of_data_blocks,
                                                                          delay_in_ms=100))

            test.log.step("7. Escape transparent mode on both modules. Check socket state "
                          "and compare transmitted / received data..")
            test.sleep(5)
            test.expect(
                dstl_switch_to_command_mode_by_pluses(test.dut))
            if not test.expect(test.socket_dut.dstl_get_service().
                                       dstl_check_if_module_in_command_mode()):
                test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
            test.expect(
                test.socket_dut.dstl_get_parser().dstl_get_socket_state() ==
                SocketState.CLIENT.value)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("RX") ==
                        data_block_size*amount_of_data_blocks)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("TX") ==
                        data_block_size*amount_of_data_blocks)

            test.log.step("8. Close and release Internet services on both modules.")
            test.log.info("Echo server is used instead of remote module")
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

            test.tcpdump_thread.join()
            test.log.info("TCPDUMP RESPONSE:")
            test.log.info(test.echo_server.linux_server_response)
            response_list = list(test.echo_server.linux_server_response.splitlines())
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
            test.expect(proper_size >= wrong_size)

            test.log.step("9. Repeat the test (Steps 2-8) for all combinations of [T_n].")
            if timer == 400:
                test.log.info("All combinations of [T_n] specified in step 2 have been performed")

        test.log.step("10. Analize IP trace logs. Verify how much data were actually sent over the "
                      "network (including headers of TCP frames - e.g. use Endpoint Statistics "
                      "feature of Wireshark).")
        test.log.info("Log analyzed in each iteration of step 8")

    def cleanup(test):
        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
