#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093706.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Check if module allows to establish more than one client connection for TCP server using IPv4 address."""

    def setup(test):
        prepare_module(test, test.dut, True)
        prepare_module(test, test.r1, False)
        prepare_module(test, test.r2, False)

    def run(test):
        test.log.h2("Executing test script for: TC0093706.001 NonTransparentTcpServerTwoClients_IPv4")

        test.log.step("1) On DUT and on both Remotes define (depends on product): \n"
                      "- Connection profile \n- PDP context and activate it.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r2 = dstl_get_connection_setup_object(test.r2)
        test.expect(connection_setup_r2.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) On DUT define and open non-transparent TCP Server profile.")
        test.socket_listener = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address = test.socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("3) On both Remotes define non-transparent TCP Client, then open defined profile on one Remote.")
        test.socket_client_r1 = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(),
                                      protocol="tcp", host=dut_ip_address, port=65100)
        test.socket_client_r1.dstl_generate_address()
        test.expect(test.socket_client_r1.dstl_get_service().dstl_load_profile())

        test.socket_client_r2 = SocketProfile(test.r2, "0", connection_setup_r2.dstl_get_used_cid(),
                                         protocol="tcp", host=dut_ip_address, port=65100)
        test.socket_client_r2.dstl_generate_address()
        test.expect(test.socket_client_r2.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_client_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4) Wait for ^SIS URC and accept incoming connection from Remote on DUT.")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_1 = SocketProfile(test.dut, test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                      connection_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server_1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("5) Check service state on DUT.")
        test.expect(test.socket_server_1.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("6) Send 100 bytes from Remote1 to DUT.")
        test.expect(test.socket_client_r1.dstl_get_service().dstl_send_sisw_command_and_data(100))

        test.log.step("7) Read received data on DUT.")
        test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_server_1.dstl_get_service().dstl_read_data(100))

        test.log.step("8) Open defined profile on Remote2.")
        test.expect(test.socket_client_r2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client_r2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("9) Wait for ^SIS URC and accept incoming connection from second Remote on DUT.")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_2 = SocketProfile(test.dut, test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                        connection_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server_2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_server_2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("10) Check service state on DUT.")
        test.expect(test.socket_server_2.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("11) Send 100 bytes from Remote2 to DUT.")
        test.expect(test.socket_client_r2.dstl_get_service().dstl_send_sisw_command_and_data(100))

        test.log.step("12) Read received data on DUT.")
        test.expect(test.socket_server_2.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_server_2.dstl_get_service().dstl_read_data(100))

        test.log.step("13) Close all services.")
        test.expect(test.socket_client_r1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client_r2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server_2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.log.step("14) Delete all defined profiles.")
        test.expect(test.socket_client_r1.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_client_r2.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server_2.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_reset_service_profile())


def prepare_module(test, device, is_dut):
    dstl_detect(device)
    dstl_get_imei(device)
    if not is_dut:
        test.expect(dstl_restart(device))
        dstl_set_scfg_urc_dst_ifc(device)
    test.expect(dstl_set_scfg_tcp_with_urcs(device, "on"))
    test.expect(dstl_enter_pin(device))


if "__main__" == __name__:
    unicorn.main()
