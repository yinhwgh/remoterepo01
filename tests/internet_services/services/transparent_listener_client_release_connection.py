# responsible: damian.latacz@globallogic.com
# Wroclaw
# TC0095040.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from ipaddress import IPv4Address


class Test(BaseTest):
    """
       TC intention: Client release connection while server is in command mode.
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_detect(test.r1)
        test.expect(dstl_enter_pin(test.r1))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2"))

    def run(test):
        test.log.step("1. Define and activate PDP context, then get IP address of it (for defining client connection "
                      "in step 3).")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True, device_interface="at2")
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        dut_ip_addresses = test.connection_setup_dut.dstl_get_pdp_address()
        test.expect(test.check_ip_address(dut_ip_addresses[0]))
        remote_ip_addresses = test.connection_setup_r1.dstl_get_pdp_address()
        test.expect(test.check_ip_address(remote_ip_addresses[0]))

        test.log.step("2. Define TCP socket transparent listener with parameters: "
                      "localport=9996;timer=100;etx=27;autoconnect=0;connecttimeout=30;keepidle=1;keepcnt=not "
                      "set;keepintvl=75;addrfilter=[IP address of client module].")
        etx = 27
        test.socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=9996, nagle_timer=100, etx_char=etx, autoconnect="0",
                                        connect_timeout=30, tcp_keep_idle=1, tcp_keep_intvl=75,
                                        addr_filter=remote_ip_addresses[0])
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open listener. Define and open client service.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        test.socket_r1 = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                       host=dut_ip_addresses[0], port=9996, etx_char=etx, device_interface="at2")
        test.socket_r1.dstl_generate_address()
        test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Wait for SIS URC on listener side.")
        ip_address_and_port_regex = "\"(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([0-9]|[1-9][0-9]|1[" \
                                    "0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]{3,5}\""
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0", ip_address_and_port_regex))

        test.log.step("5. Check service state and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)

        test.log.step("6. Accept the connection with at^siso on listener side.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("7. Check service state and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)

        test.log.step("8. Switch to transparent mode on both modules.")
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_r1.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("9. Remote client sends data = 10x1500 bytes.")
        for loop in range(10):
            test.socket_r1.dstl_get_service().dstl_send_data(dstl_generate_data(1500), expected="")
        test.sleep(5)

        test.log.step("10. Server sends data = 1024 bytes.")
        test.socket_dut.dstl_get_service().dstl_send_data(dstl_generate_data(1024), expected="")
        test.sleep(5)

        test.log.step("11. Switch to command mode on client.")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, etx, device_interface="at2"))
        test.expect(test.socket_r1.dstl_get_service().dstl_check_if_module_in_command_mode())

        test.log.step("12. Remote client closes the connection.")
        test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())

        test.log.step("13. Check URCs on server side.")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48", "\"Remote peer has closed the "
                                                                                       "connection\""))
        test.expect("NO CARRIER" in test.dut.at1.last_response)

        test.log.step("14. Check service state, socket state and amount of transferred data.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)
        test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx") == 0)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") == 0)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") == 0)

        test.log.step("15. Send new request from client.")
        test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        is_sis_appeared = test.expect(test.socket_dut.dstl_get_urc().
                                      dstl_is_sis_urc_appeared("3", "0", ip_address_and_port_regex))

        test.log.step("16. Check service state and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.SERVER.value)

        test.log.step("17. If request received, reject the connection with at^sish.")
        if is_sis_appeared:
            test.expect(test.socket_dut.dstl_get_service().dstl_disconnect_remote_client())
            test.expect(test.socket_r1.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48", "\"Remote peer has closed "
                                                                                          "the connection\""))

        test.log.step("18. Check service state and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.LISTENER_ENDPOINT.value)

        test.log.step("19. Close all services.")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())

        test.log.step("20. Check service state and socket state.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)

    def cleanup(test):
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_r1.dstl_get_service().dstl_reset_service_profile())

    def check_ip_address(test, ip_address):
        try:
            IPv4Address(ip_address)
            test.log.info("IPv4 address format is correct.")
            return True
        except ValueError:
            test.log.error("IPv4 address format is not correct.")
            return False


if "__main__" == __name__:
    unicorn.main()
