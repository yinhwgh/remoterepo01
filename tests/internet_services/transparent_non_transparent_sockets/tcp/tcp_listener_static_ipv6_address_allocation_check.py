#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0105391.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer

from dstl.network_service.register_to_network import dstl_register_to_network

from dstl.identification.get_imei import dstl_get_imei

from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile

from dstl.configuration.scfg_remapping_ipv6 import dstl_enable_remapping_ipv6_iid, \
    dstl_disable_remapping_ipv6_iid

from dstl.packet_domain.select_printing_ip_address_format import \
    dstl_select_printing_ip_address_format


class Test(BaseTest):
    """	Test behavior of TCP/RemappingIpv6IID setting using TCP listener profile."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        localport = 50000

        test.log.info("Executing script for test case: 'TC0105391.001 - "
                      "TcpListenerStaticIPv6AddressAllocationCheck")

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server_1 = EchoServer('IPv6', "TCP", extended=True)
        test.echo_server_2 = EchoServer('IPv6', "TCP", extended=True)

        test.log.step("1. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module")
        dstl_disable_remapping_ipv6_iid(test.dut)
        dstl_restart(test.dut)

        remapping_list = [False, True]
        for remapping in remapping_list:
            test.log.step("2. On DUT and remote modules define and activate IPV6 PDP contexts")
            test.log.info("Echo server is used instead of remote module")
            connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version="IPv6",
                                                                       ip_public=True)
            test.expect(
                connection_setup_object.dstl_load_and_activate_internet_connection_profile())

            test.log.step("3. On DUT set printing IP address format to IPv6-like colon-notation")
            dstl_select_printing_ip_address_format(test.dut, 1)

            test.log.step("4. On DUT define and open IV6 TCP listener profile")

            test.socket_dut = SocketProfile(test.dut, '0',
                                            connection_setup_object.dstl_get_used_cid(),
                                            protocol="tcp",
                                            host="listener", localport=localport)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())

            test.log.step("5. On DUT check and compare adresses assigned in siso and cgpaddr")
            siso_ip = \
            test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port("IPv6").split(
                "]:")[0]

            cgpaddr_ip = connection_setup_object.dstl_get_pdp_address(
                connection_setup_object.dstl_get_used_cid())
            test.expect(cgpaddr_ip[0] not in siso_ip)

            test.log.step("6. On Remote create and open two IPv6 TCP clients profiles to addresses "
                          "displayed in siso and cgpaddr commands on DUT")
            test.log.info("Echo server is used instead of remote module")
            test.log.info("Will be executed in next step")

            test.log.step("7. On DUT accept connection from client and exchange some data.")
            if not remapping:
                test.echo_server_1.dstl_run_ssh_nc_process(siso_ip, localport)
            else:
                test.echo_server_1.dstl_run_ssh_nc_process(cgpaddr_ip[0], localport)
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
            test.socket_server_1 = SocketProfile(test.dut,
                                                 test.socket_dut.dstl_get_urc().
                                                 dstl_get_sis_urc_info_id(),
                                                 connection_setup_object.dstl_get_used_cid())
            test.expect(test.socket_server_1.dstl_get_service().dstl_open_service_profile())

            test.block_size = 100
            data = dstl_generate_data(test.block_size)

            test.expect(test.socket_server_1.dstl_get_service().
                        dstl_send_sisw_command_and_data(100))

            test.echo_server_1.dstl_send_data_from_ssh_server(data)
            test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(test.socket_server_1.dstl_get_service().dstl_read_data(100))

            test.expect(test.socket_server_1.dstl_get_parser().dstl_get_service_data_counter("rx")
                        ==
                        test.socket_server_1.dstl_get_parser().dstl_get_service_data_counter("tx"))

            if not remapping:
                test.echo_server_2.dstl_run_ssh_nc_process(cgpaddr_ip[0], localport)
            else:
                test.echo_server_2.dstl_run_ssh_nc_process(siso_ip, localport)
            test.expect(not test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("1"))

            test.echo_server_1.dstl_stop_ssh_nc_process()
            test.echo_server_2.dstl_stop_ssh_nc_process()


            test.log.step("8. Close profiles on DUT and Remote.")
            test.log.info("Echo server is used instead of remote module")
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

            if not remapping:
                test.log.step("9. On DUT Set the TCP/RemappingIpv6IID setting to 1 "
                              "and restart module")

                dstl_enable_remapping_ipv6_iid(test.dut)
                dstl_restart(test.dut)

                test.log.step("10. Repeat steps 2-8")

        test.log.step("11. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module")
        dstl_disable_remapping_ipv6_iid(test.dut)
        dstl_restart(test.dut)

    def cleanup(test):
        try:
            test.echo_server_1.dstl_stop_ssh_nc_process()
            test.echo_server_2.dstl_stop_ssh_nc_process()
            if not (test.echo_server_1.dstl_server_close_port() and
                    test.echo_server_2.dstl_server_close_port()):
                test.log.warn("Problem during closing port on server.")
            test.socket_dut.dstl_get_service().dstl_close_service_profile()
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
