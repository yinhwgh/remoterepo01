#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0105249.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer



class Test(BaseTest):
    """Intention:
    Check if it%#39;s possible to configure and activate the "keep-alive" via command AT^SISS with optional parameters
    mentioned below, for Transparent TCP socket services (client and server) for IPv4 and IPv6 respectively.
    keepidle
    keepcnt
    keepintvlÂ

    description:
    1. Define IPv4 PDP context and activate it.
    2. Define 4 service profiles with defined correct keepidle, keepcnt and keepintvl values:
    - Transparent TCP Client to IPv4 echoserver with maximum allowed values of parameters
    - Transparent TCP Client to IPv6 echoserver with minimum allowed values of parameters
    - Transparent TCP Server IPv4 with minimum allowed values of parameters
    - Transparent TCP Server IPv6 with maximum allowed values of parameters
    3. Open profiles: IPv4 client and server.
    4. Close all profiles.
    5. Deactivate PDP context.
    6. Define IPv6 PDP context and activate it.
    7. Open profiles: IPv6 client and server.
    8. Close all profiles.
    9. Try to define service profile with invalid values (repeat separately for keepidle, keepcnt and keepintvl)."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut))
        test.ip_server_ipv4 = EchoServer("IPv4", "TCP")
        test.ip_server_ipv6 = EchoServer("IPv6", "TCP")

    def run(test):

        test.log.step("1. Define IPv4 PDP context and activate it.")

        connection_setup_ipv4 = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_ipv4.dstl_load_and_activate_internet_connection_profile())

        connection_setup_ipv6 = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")

        test.log.step("2. Define 4 service profiles with defined correct keepidle, keepcnt and keepintvl values:\n"
                      "- Transparent TCP Client to IPv4 echoserver with maximum allowed values of parameters\n"
                      "- Transparent TCP Client to IPv6 echoserver with minimum allowed values of parameters\n"
                      "- Transparent TCP Server IPv4 with minimum allowed values of parameters\n"
                      "- Transparent TCP Server IPv6 with maximum allowed values of parameters\n")
        cid_ipv4 = connection_setup_ipv4.dstl_get_used_cid()
        cid_ipv6 = connection_setup_ipv6.dstl_get_used_cid()
        socket_client_ipv4 = SocketProfile(test.dut, 0, cid_ipv4,
                                                protocol="tcp", ip_server=test.ip_server_ipv4, etx_char=26,
                                                tcp_keep_idle="65535", tcp_keep_cnt="127", tcp_keep_intvl="255",
                                                ip_version="4")
        socket_client_ipv4.dstl_set_parameters_from_ip_server()
        socket_client_ipv4.dstl_generate_address()
        test.expect(socket_client_ipv4.dstl_get_service().dstl_load_profile())

        socket_client_ipv6 = SocketProfile(test.dut, 1, cid_ipv6,
                                                protocol="tcp", ip_server=test.ip_server_ipv6, etx_char=26,
                                                tcp_keep_idle="1", tcp_keep_cnt="1", tcp_keep_intvl="1", alphabet=1,
                                                ip_version="6")
        socket_client_ipv6.dstl_set_parameters_from_ip_server()
        socket_client_ipv6.dstl_generate_address()
        test.expect(socket_client_ipv6.dstl_get_service().dstl_load_profile())

        socket_listener_ipv4 = SocketProfile(test.dut, 2, cid_ipv4,
                                                protocol="tcp", host="listener", localport="8888", etx_char=26,
                                                tcp_keep_idle="1", tcp_keep_cnt="1", tcp_keep_intvl="1", ip_version="4")
        socket_listener_ipv4.dstl_generate_address()
        test.expect(socket_listener_ipv4.dstl_get_service().dstl_load_profile())

        socket_listener_ipv6 = SocketProfile(test.dut, 3, cid_ipv6,
                                                  protocol="tcp", host="listener", localport="8889", etx_char=26,
                                                  tcp_keep_idle="65535", tcp_keep_cnt="127", tcp_keep_intvl="255",
                                                  ip_version="6", alphabet=1)
        socket_listener_ipv6.dstl_generate_address()
        test.expect(socket_listener_ipv6.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open profiles: IPv4 client and server.")

        test.expect(socket_client_ipv4.dstl_get_service().dstl_open_service_profile(), msg="problem with profile")
        test.expect(socket_client_ipv4.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.expect(socket_listener_ipv4.dstl_get_service().dstl_open_service_profile(),
                    msg="problem with profile")
        test.expect(socket_listener_ipv4.dstl_get_urc().dstl_is_sis_urc_appeared("5"))

        test.log.step("4. Close all profiles.")
        test.expect(socket_client_ipv4.dstl_get_service().dstl_close_service_profile(), msg="problem with profile")
        test.expect(socket_listener_ipv4.dstl_get_service().dstl_close_service_profile(),
                    msg="problem with profile")

        test.log.step("5. Deactivate PDP context.")
        test.expect(connection_setup_ipv4.dstl_detach_from_packet_domain())
        test.expect(test.dut.at1.send_and_verify("at^sica=0,{}".format(cid_ipv4), "OK"))
        test.expect(connection_setup_ipv4.dstl_attach_to_packet_domain())

        test.log.step("6. Define IPv6 PDP context and activate it.")
        test.expect(connection_setup_ipv6.dstl_load_and_activate_internet_connection_profile())

        test.log.step("7. Open profiles: IPv6 client and server.")
        test.expect(socket_client_ipv6.dstl_get_service().dstl_open_service_profile(), msg="problem with profile")
        test.expect(socket_client_ipv6.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.expect(socket_listener_ipv6.dstl_get_service().dstl_open_service_profile(),
                    msg="problem with profile")
        test.expect(socket_listener_ipv6.dstl_get_urc().dstl_is_sis_urc_appeared("5"))

        test.log.step("8. Close all profiles.")
        test.expect(socket_client_ipv6.dstl_get_service().dstl_close_service_profile(), msg="problem with profile")
        test.expect(socket_listener_ipv6.dstl_get_service().dstl_close_service_profile(),
                    msg="problem with profile")

        test.log.step("9. Try to define service profile with invalid values (repeat separately for keepidle, keepcnt "
                      "and keepintvl).")
        socket_client_ipv4.dstl_set_tcp_keep_idle("0")
        socket_client_ipv4.dstl_generate_address()
        test.expect(not socket_client_ipv4.dstl_get_service().dstl_write_address())

        socket_client_ipv4.dstl_set_tcp_keep_idle("1")
        socket_client_ipv4.dstl_set_tcp_keep_cnt("0")
        socket_client_ipv4.dstl_generate_address()
        test.expect(not socket_client_ipv4.dstl_get_service().dstl_write_address())

        socket_client_ipv4.dstl_set_tcp_keep_cnt("1")
        socket_client_ipv4.dstl_set_tcp_keep_intvl("0")
        socket_client_ipv4.dstl_generate_address()
        test.expect(not socket_client_ipv4.dstl_get_service().dstl_write_address())

    def cleanup(test):
        try:
            test.ip_server_ipv4.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server ipv4 object was not created.")
        try:
            test.ip_server_ipv6.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server ipv6 object was not created.")


if "__main__" == __name__:
    unicorn.main()
