# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0107427.001 TC0107427.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ To check if secure connection can be established using IPV6"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_enter_pin(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.h2("Executing test script for: TC0096179.001 NonTranspTcpClientSendReceiveDataEod")
        test.server_socket = SslEchoServer("IPv6", "TCP")

        test.log.step("1. Define and activate IPv6 PDP context / connection Profile")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define 2 HTTPs and 2 TCPs profiles with secopt 0, to different IPv6 "
                      "sites/servers (one using IP address second using FQDN)")
        address_fqdn = "wikipedia.org"
        port_fqdn = 443
        wikipedia_ip = "2620::862:ED1A:0:0:0:1"
        address_IP = "[{}]".format(test.server_socket.dstl_get_server_ip_address())
        port_IP = test.server_socket.dstl_get_server_port()
        test.socket_client_first = SocketProfile(test.dut, "0",
                                                 connection_setup_dut.dstl_get_used_cid(),
                                                 protocol="tcp", host=address_fqdn, port=port_fqdn,
                                                 secure_connection=True, secopt="0")
        test.socket_client_first.dstl_generate_address()
        test.expect(test.socket_client_first.dstl_get_service().dstl_load_profile())

        test.socket_client_second = SocketProfile(test.dut, "1",
                                             connection_setup_dut.dstl_get_used_cid(), alphabet=1,
                                             protocol="tcp", host=address_IP, port=port_IP,
                                             secure_connection=True, secopt="0")
        test.socket_client_second.dstl_generate_address()
        test.expect(test.socket_client_second.dstl_get_service().dstl_load_profile())

        test.http_client_first = HttpProfile(test.dut, "2",
                                             connection_setup_dut.dstl_get_used_cid(),
                                             host=address_fqdn, http_command="get",
                                             secure_connection=True, secopt="0")
        test.http_client_first.dstl_generate_address()
        test.expect(test.http_client_first.dstl_get_service().dstl_load_profile())

        test.http_client_second = HttpProfile(test.dut, "3",
                                              connection_setup_dut.dstl_get_used_cid(),
                                              http_command="head", alphabet=1, host=wikipedia_ip,
                                              secure_connection=True, secopt="0", http_path="/")

        test.http_client_second.dstl_generate_address()
        test.expect(test.http_client_second.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open and establish all declared connections")
        test.expect(test.socket_client_first.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client_second.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_client_first.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_client_second.dstl_get_service().dstl_open_service_profile())

        test.log.step("5. Check URC shows that data can be read (HTTPs) or write (TCPs)")
        test.log.info("executed in previous step")

        test.log.step("6. Exchange data with servers")
        test.expect(
            test.socket_client_first.dstl_get_service().dstl_send_sisw_command_and_data(1500,
                                                                                   expected="O"))
        test.expect(
            test.socket_client_second.dstl_get_service().dstl_send_sisw_command_and_data(1500,
                                                                                    expected="O"))
        test.expect(test.socket_client_second.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_client_second.dstl_get_service().dstl_read_data(1500))
        test.expect(test.http_client_first.dstl_get_service().dstl_read_data(1500, repetitions=10,
                                                                             delay_in_ms=800))
        test.expect(test.http_client_second.dstl_get_service().dstl_read_data(100, repetitions=5))

        test.log.step("7. Check sevice states and tx/rx counters using SISO command")
        test.check_state_and_counters(test.socket_client_first, ServiceState.UP.value, 0, 1500)
        test.check_state_and_counters(test.socket_client_second, ServiceState.UP.value, 1500, 1500)
        test.check_state_and_counters(test.http_client_first, ServiceState.UP.value, 13000, 0)
        test.check_state_and_counters(test.http_client_second, ServiceState.UP.value, 500, 0)

    def cleanup(test):
        test.log.step("8. Close connections")
        test.expect(test.socket_client_first.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client_first.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_client_second.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client_second.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.http_client_first.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_first.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.http_client_second.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_client_second.dstl_get_service().dstl_reset_service_profile())

        try:
            test.server_socket.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

    def check_state_and_counters(test, profile, state, rx, tx):
        test.expect(
            profile.dstl_get_parser().dstl_get_service_state() == state)
        test.expect(profile.dstl_get_parser().dstl_get_service_data_counter("RX") >= rx)
        test.expect(
            profile.dstl_get_parser().dstl_get_service_data_counter("TX") == tx)


if "__main__" == __name__:
    unicorn.main()
