# responsible: damian.latacz@globallogic.com
# location: Wroclaw
# TC0104180.001, TC0104180.002

import unicorn

from core.basetest import BaseTest

from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.generate_data import dstl_generate_data

from dstl.identification.get_imei import dstl_get_imei

from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr

from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile

from ipaddress import IPv6Address, AddressValueError

from dstl.configuration.configure_dtr_line_mode import dstl_set_dtr_line_mode

from dstl.devboard.configure_dtr_detection_devboard import dstl_enable_devboard_dtr_detection


class Test(BaseTest):
    """Test socket service client transparent mode with ipv6"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.tcp_echo_server = EchoServer('IPv6', "TCP")
        test.udp_echo_server = EchoServer('IPv6', "UDP")
        dstl_set_dtr_line_mode(test.dut, "2")
        dstl_enable_devboard_dtr_detection(test.dut)

    def run(test):
        test.log.step("1. Define PDP context or internet connection profile (IPv6).")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        for iteration in range(2):
            if iteration == 0:
                test.log.step("2. Set up TCP transparent client service profile to echo server.")
                test.define_transparent_socket_profile(test, "TCP")
            else:
                test.log.step("2. Set up UDP transparent client service profile to echo server.")
                test.define_transparent_socket_profile(test, "UDP")

            test.log.step("3. Open service profile.")
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile())

            test.log.step("4. Check service state and assigned IPv6 address.")
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.UP.value)
            test.expect(test.check_correctness_of_ipv6_address(test))

            test.log.step("5. Switch to transparent mode.")
            test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("6. Transfer some data.")
            data_to_send = dstl_generate_data(100)
            test.expect(test.socket.dstl_get_service().dstl_send_data(data_to_send,
                                                                      expected=data_to_send))

            test.log.step("7. Toggle DTR line to enter the command mode.")
            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))

            test.log.step("8. Check service state and assigned IPv6 address. "
                          "Check if data was transferred.")
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.UP.value)
            test.expect(test.check_correctness_of_ipv6_address(test))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                        test.socket.dstl_get_parser().dstl_get_service_data_counter("rx"))

            test.log.step("9. Close service.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            if iteration == 0:
                test.log.step("10. Repeat steps 2-9 for UDP transparent client service profile.")

    @staticmethod
    def define_transparent_socket_profile(test, protocol):
        test.socket = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                    protocol=protocol,
                               alphabet=1, ip_version='IPv6', empty_etx=True)
        if protocol == "TCP":
            test.socket.dstl_set_parameters_from_ip_server(test.tcp_echo_server)
        else:
            test.socket.dstl_set_parameters_from_ip_server(test.udp_echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())
        return test.socket

    @staticmethod
    def check_correctness_of_ipv6_address(test):
        assigned_ip_address = \
            test.socket.dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version='IPv6').split(
                "[")[1].split("]")[0]
        test.log.info("Assigned IPv6 address: {}".format(assigned_ip_address))
        try:
            IPv6Address(assigned_ip_address)
            return True
        except AddressValueError:
            return False

    def cleanup(test):
        try:
            if not test.tcp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on TCP server.")
            if not test.udp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on UDP server.")
        except (AttributeError, IndexError):
            test.log.error("Object was not created.")
        test.socket.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
