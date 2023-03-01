# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0092197.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """ To test socket client service in nontransparent mode with ipv6 """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.tcp_echo_server = EchoServer('IPv6', "TCP")
        test.udp_echo_server = EchoServer('IPv6', "UDP")

    def run(test):
        test.log.info("Executing script for test case: 'TpSocketClientServiceNonTransparent.'")
        amount_of_data = 1000

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_enter_pin(test.dut))
        test.log.info("Attach to network will be done during step 4.")

        test.log.step("2) Depends on product: set Connection Profile (GPRS6) "
                      "/ Define PDP Context (ipv6).")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6')
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        for pdp_type in ['ipv6', 'ipv4v6']:
            test.log.step("3) Set service profiles: TCP Client on DUT and TCP Listener on Remote.")
            test.tcp_client = SocketProfile(test.dut, "1", cid, protocol="tcp", alphabet=1,
                                            ip_version='IPv6')
            test.tcp_client.dstl_set_parameters_from_ip_server(test.tcp_echo_server)
            test.tcp_client.dstl_generate_address()
            test.expect(test.tcp_client.dstl_get_service().dstl_load_profile())

            test.log.step("4) Depends on product - Activate PDP Context.")
            test.expect(connection_setup.dstl_activate_internet_connection(), critical=True)

            test.log.step("5) Open services - firstly open Remote then DUT.")
            test.expect(test.tcp_client.dstl_get_service().dstl_open_service_profile())

            test.log.step("6) Accept incoming connection on Remote.")
            test.log.info("Skipped as echo server is used that accepts request automatically.")

            test.log.step("7) Send some data from DUT to Remote.")
            test.expect(test.tcp_client.dstl_get_service()
                        .dstl_send_sisw_command_and_data(amount_of_data))
            test.expect(test.tcp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(test.tcp_client.dstl_get_service().dstl_read_data(amount_of_data))
            test.expect(test.tcp_client.dstl_get_parser().dstl_get_service_data_counter("rx")
                        == amount_of_data)

            test.log.step("8) Close services.")
            test.expect(test.tcp_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("9) Set service profiles: UDP Client on DUT and UDP Endpoint on Remote.")
            test.udp_client = SocketProfile(test.dut, "1", cid, protocol="udp", alphabet=1,
                                            ip_version='IPv6')
            test.udp_client.dstl_set_parameters_from_ip_server(test.udp_echo_server)
            test.udp_client.dstl_generate_address()
            test.expect(test.udp_client.dstl_get_service().dstl_load_profile())

            test.log.step("10) Open services - firstly open Remote then DUT.")
            test.expect(test.udp_client.dstl_get_service().dstl_open_service_profile())

            test.log.step("11) Send some data from DUT to Remote.")
            test.expect(test.udp_client.dstl_get_service()
                        .dstl_send_sisw_command_and_data(amount_of_data, repetitions=5, append=True))
            test.expect(test.tcp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(test.udp_client.dstl_get_service().dstl_read_data(amount_of_data,
                                                                          repetitions=5))
            test.expect(test.udp_client.dstl_get_parser().dstl_get_service_data_counter("rx")
                        >= amount_of_data*4)

            test.log.step("12) Close services.")
            test.expect(test.udp_client.dstl_get_service().dstl_close_service_profile())

            if 'ipv6' in pdp_type:
                test.log.step("13) Create an internet connection profile (GPRS6) "
                              "/ Define PDP Context (ipv4v6).")
                connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6')
                connection_setup.cgdcont_parameters['pdp_type'] = 'IPv4v6'
                test.expect(connection_setup.dstl_load_internet_connection_profile())

                test.log.step("14) Repeat steps 3 - 12.")

    def cleanup(test):
        try:
            if not test.tcp_echo_server.dstl_server_close_port() or \
                    not test.udp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.tcp_client.dstl_get_service().dstl_close_service_profile()
        test.tcp_client.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
