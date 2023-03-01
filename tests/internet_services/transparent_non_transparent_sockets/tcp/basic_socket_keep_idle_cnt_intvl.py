#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0095024.001


import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """
    Check if it's possible to configure and activate the "keep-alive" via command AT^SISS with optional parameters
    mentioned below, for Transparent and Non-Transparent TCP socket services (client and server)
    for IPv4 and IPv6 respectively: keepidle, keepcnt, keepintvl
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server_ipv4 = EchoServer("IPv4", "TCP")
        test.echo_server_ipv6 = EchoServer("IPv6", "TCP")

    def run(test):
        test.log.info("Executing script for test case: TC0095024.001 BasicSocketKeepIdleCntIntvl")

        test.log.step("1) Define IPv4 PDP context and activate it.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile(), critical=True)
        con_id = connection_setup_object.dstl_get_used_cid()

        test.log.step("2) Define 4 service profiles with defined correct keepidle, keepcnt and keepintvl values:\r\n"
                      "    - Non-transparent TCP Client to IPv4 echoserver\n"
                      "    - Non-transparent TCP Client to IPv6 echoserver\n"
                      "    - Non-transparent TCP Server IPv4\n"
                      "    - Non-transparent TCP Server IPv6")
        socket1 = SocketProfile(test.dut, "0", con_id, protocol="tcp", alphabet=1, ip_version="IPv4",
                                tcp_keep_idle=100, tcp_keep_cnt=3, tcp_keep_intvl=1)
        socket1.dstl_set_parameters_from_ip_server(test.echo_server_ipv4)
        socket1.dstl_generate_address()
        test.expect(socket1.dstl_get_service().dstl_load_profile())

        socket2 = SocketProfile(test.dut, "1", con_id, protocol="tcp", alphabet=1, ip_version="IPv6",
                                tcp_keep_idle=65535, tcp_keep_cnt=127, tcp_keep_intvl=255)
        socket2.dstl_set_parameters_from_ip_server(test.echo_server_ipv6)
        socket2.dstl_generate_address()
        test.expect(socket2.dstl_get_service().dstl_load_profile())

        listener1 = SocketProfile(test.dut, 2, con_id, protocol="tcp", host="listener", localport=65100,
                                  tcp_keep_idle=1, ip_version="IPv4", tcp_keep_cnt=1, tcp_keep_intvl=39)
        listener1.dstl_generate_address()
        test.expect(listener1.dstl_get_service().dstl_load_profile())

        listener2 = SocketProfile(test.dut, 3, con_id, protocol="tcp", host="listener", ip_version="IPv6",
                                  localport=65100, tcp_keep_idle=999, tcp_keep_cnt=17, tcp_keep_intvl=79)
        listener2.dstl_generate_address()
        test.expect(listener2.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open profiles: IPv4 client and server.")
        test.expect(socket1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(listener1.dstl_get_service().dstl_open_service_profile())
        test.expect(listener1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("4) Close all profiles.")
        test.expect(socket1.dstl_get_service().dstl_close_service_profile())
        test.expect(listener1.dstl_get_service().dstl_close_service_profile())

        test.log.step("5) Deactivate PDP context")
        test.expect(connection_setup_object.dstl_deactivate_internet_connection())
        test.sleep(10)

        test.log.step("6) Define IPv6 PDP context and activate it.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv6')
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile(), critical=True)

        test.log.step("7) Open profiles: IPv6 client and server.")
        test.expect(socket2.dstl_get_service().dstl_open_service_profile())
        test.expect(socket2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(listener2.dstl_get_service().dstl_open_service_profile())
        test.expect(listener2.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("8) Close all profiles.")
        test.expect(socket2.dstl_get_service().dstl_close_service_profile())
        test.expect(listener2.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if (not test.echo_server_ipv4.dstl_server_close_port() or
                    not test.echo_server_ipv6.dstl_server_close_port()):
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
