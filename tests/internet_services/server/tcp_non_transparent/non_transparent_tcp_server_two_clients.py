# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0093707.001, TC0093706.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    """Check if module allows to establish more than one client connection for TCP server
    using IPv4 or IPv6 address - depending on test case to be executed.
        param: ip_version - Internet Protocol version. Allowed values: 'IPv4', 'IPv6'."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server1 = EchoServer(test.ip_version, 'TCP', extended=True)
        test.echo_server2 = EchoServer(test.ip_version, 'TCP', extended=True)

    def run(test):
        test.log.h2("Executing test script for: NonTransparentTcpServerTwoClients_{}".format(test.ip_version))

        test.log.step("1) On DUT and on both Remotes define (depends on product): \n"
                      "- Connection profile \n- PDP context and activate it.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version,
                                                                ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) On DUT define and open non-transparent TCP Server profile.")
        port = 65100
        test.socket_dut = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp", host="listener", localport=port, alphabet=1,
                                        ip_version=test.ip_version)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        dut_ip_address_and_port = test.socket_dut.dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version=test.ip_version)
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

        test.log.step("3) On both Remotes define non-transparent TCP Client, then open defined profile "
                      "on one Remote (or open connection to DUT from first remote server).")
        test.echo_server1.dstl_run_ssh_nc_process(dut_ip_address, port)

        test.log.step("4) Wait for ^SIS URC and accept incoming connection from Remote on DUT.")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_1 = SocketProfile(test.dut, test.socket_dut.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                             connection_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server_1.dstl_get_service().dstl_open_service_profile())

        test.log.step("5) Check service state on DUT.")
        test.expect(test.socket_server_1.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("6) Send 100 bytes from Remote1 to DUT.")
        test.block_size = 100
        data = dstl_generate_data(test.block_size)
        test.echo_server1.dstl_send_data_from_ssh_server(data)

        test.log.step("7) Read received data on DUT.")
        test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_server_1.dstl_get_service().dstl_read_data(100))

        test.log.step("8) Open defined profile on Remote2 (or open connection to DUT from second "
                      "remote server).")
        test.echo_server2.dstl_run_ssh_nc_process(dut_ip_address, port, ssh_server_property='ssh_server_3')

        test.log.step("9) Wait for ^SIS URC and accept incoming connection from second Remote on DUT.")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_2 = SocketProfile(test.dut, test.socket_dut.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                         connection_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server_2.dstl_get_service().dstl_open_service_profile())

        test.log.step("10) Check service state on DUT.")
        test.expect(test.socket_server_2.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("11) Send 100 bytes from Remote2 to DUT.")
        test.echo_server2.dstl_send_data_from_ssh_server(data, ssh_server_property='ssh_server_3')

        test.log.step("12) Read received data on DUT.")
        test.expect(test.socket_server_2.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_server_2.dstl_get_service().dstl_read_data(100))

        test.log.step("13) Close all services.")
        test.expect(test.socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server_2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.echo_server1.dstl_stop_ssh_nc_process()
        test.echo_server2.dstl_stop_ssh_nc_process()

    def cleanup(test):
        test.log.step("14) Delete all defined profiles.")
        try:
            if not test.echo_server1.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.echo_server1.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Problem with server object.")
        try:
            if not test.echo_server2.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.echo_server2.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Problem with server object.")
        if not test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile()):
            test.socket_dut.dstl_get_service().dstl_close_service_profile()
            test.socket_dut.dstl_get_service().dstl_reset_service_profile()
        if not test.expect(test.socket_server_1.dstl_get_service().dstl_reset_service_profile()):
            test.socket_server_1.dstl_get_service().dstl_close_service_profile()
            test.socket_server_1.dstl_get_service().dstl_reset_service_profile()
        if not test.expect(test.socket_server_2.dstl_get_service().dstl_reset_service_profile()):
            test.socket_server_2.dstl_get_service().dstl_close_service_profile()
            test.socket_server_2.dstl_get_service().dstl_reset_service_profile()

if "__main__" == __name__:
    unicorn.main()