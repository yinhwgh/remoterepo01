# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0095023.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses, \
    dstl_switch_to_command_mode_by_etxchar
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState


class Test(BaseTest):
    """
    Define simple socket profile and establish session with server, enter transparent mode,
    send eod flag and close the connection.
    Check if 10 profiles can be defined at the same time.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.echo_server = EchoServer("IPv4", "TCP", extended=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.step("1. Define PDP context and activate it.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define service profile - Transparent TCP client.")
        test.socket_dut = SocketProfile(test.dut, "0",
                                        test.connection_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp", etx_char=26)
        test.socket_dut.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined profile.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())

        test.log.step("4. Send some data to the echo server in command mode.")
        test.data_length = 1500
        test.all_data = 0
        test.expect(
            test.socket_dut.dstl_get_service().dstl_send_sisw_command_and_data(test.data_length))
        test.sleep(5)
        test.all_data += test.data_length
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "tx") == test.all_data)

        test.log.step("5. Read received data.")
        test.expect(test.socket_dut.dstl_get_service().dstl_read_data(test.data_length))
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "rx") == test.all_data)

        test.log.step("6. Enter transparent mode and send some data to echo server.")
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
        amount_of_data_blocks = 1
        data = dstl_generate_data(test.data_length)
        test.expect(test.socket_dut.dstl_get_service().dstl_send_data(data, expected=data,
                                                                      repetitions=
                                                                      amount_of_data_blocks))
        test.sleep(5)
        test.all_data += test.data_length*amount_of_data_blocks

        test.log.step("7. Exit from transparent mode.")
        test.sleep(5)
        test.expect(
            dstl_switch_to_command_mode_by_pluses(test.dut))
        if not test.expect(test.socket_dut.dstl_get_service().
                                   dstl_check_if_module_in_command_mode()):
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "tx") == test.all_data)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "rx") == test.all_data)

        test.log.step("8. Send some data with eod flag in command mode, then read them.")
        test.expect(
            test.socket_dut.dstl_get_service().dstl_send_sisw_command_and_data(test.data_length,
                                                                               eod_flag="1"))
        test.sleep(5)
        test.all_data += test.data_length
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "tx") == test.all_data)
        test.expect(test.socket_dut.dstl_get_service().dstl_read_data(test.data_length))
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter(
            "rx") == test.all_data)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state(
            at_command=Command.SISO_WRITE) == ServiceState.DOWN.value)

        test.log.step("9. Close service profile.")
        test.socket_dut.dstl_get_service().dstl_close_service_profile()

        test.log.step("10. Deactivate PDP context.")
        test.expect(test.connection_setup_dut.dstl_detach_from_packet_domain())

        test.log.step("11. Define 10 the same Transparent TCP client service profiles.")
        for srv_id in range(1, 10):
            test.socket_dut = SocketProfile(test.dut, srv_id,
                                            test.connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp", etx_char=26)
            test.socket_dut.dstl_set_parameters_from_ip_server(test.echo_server)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

    def cleanup(test):
        test.log.info("Reset Internet profiles.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")

        except AttributeError:
            test.log.error("Object was not created.")


if __name__ == "__main__":
    unicorn.main()