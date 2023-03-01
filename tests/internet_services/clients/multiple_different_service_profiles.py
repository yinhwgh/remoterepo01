#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0104068.001, TC0104068.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState


class Test(BaseTest):
    """Intention:
Checking if multiple internet service profiles can be used in parallel

    description:
1. Define PDP context for Internet services and activate Internet service connection.
2. Define HTTP post profile
3. Open HTTP profile and send data
4. Define FTP put profile.
5. Open FTP profile and send data.
6. Define TCP client profile.
7. Open TCP client profile and send data.
8. Check Service and Socket state for all opened profiles.
9. For TCP profile send data with EOD flag, read data.
10. For HTTP profile send data amount specified in hcContLen parameter, read data if applicable.
11. For FTP profile send data with EOD flag.
12. Close all services."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.tcp_server = EchoServer("IPv4", "TCP")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):

        http_post_server = "http://www.httpbin.org/post"
        try:
            if test.http_post_server_address:
                test.log.info("Detected http_post_server_address parameter will be used: {}"
                              .format(test.http_post_server_address))
                http_post_server = test.http_post_server_address
        except AttributeError:
            test.log.info("http_post_server_address was not detected, therefore the default HTTP server will be "
                          "used: {}".format(http_post_server))

        test.log.step("1. Define PDP context for Internet services and activate Internet service connection.")

        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define HTTP post profile")
        con_id = test.connection_setup.dstl_get_used_cid()
        test.http_profile = HttpProfile(test.dut, 0, con_id, address=http_post_server, http_command="post",
                                        hc_cont_len="10")
        test.expect(test.http_profile.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open HTTP profile and send data ")
        test.expect(test.http_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", '"POST Bytes: 10"'))

        test.expect(test.http_profile.dstl_get_service().dstl_send_sisw_command_and_data(5))

        test.log.step("4. Define FTP put profile.")
        test.ftp_client = FtpProfile(test.dut, 1, con_id, command="put", alphabet="1",
                                     host=test.ftp_server.dstl_get_server_ip_address(),
                                     port=test.ftp_server.dstl_get_server_port(), files="filename",
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open FTP profile and send data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(100))

        test.log.step("6. Define TCP client profile.")
        test.socket_client = SocketProfile(test.dut, 2, con_id,
                                           protocol="tcp", ip_server=test.tcp_server, etx_char=26, ip_version="4")
        test.socket_client.dstl_set_parameters_from_ip_server()
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("7. Open TCP client profile and send data.")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(100))

        test.log.step("8. Check Service and Socket state for all opened profiles.")
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.expect(test.socket_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(test.http_profile.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("9. For TCP profile send data with EOD flag, read data.")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(100, eod_flag="1"))
        test.expect(test.socket_client.dstl_get_service().dstl_read_all_data(100))
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.socket_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("10. For HTTP profile send data amount specified in hcContLen parameter, "
                      "read data if applicable.")
        test.expect(test.http_profile.dstl_get_service().dstl_send_sisw_command_and_data(5))
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_data_counter("tx") == 10)
        test.expect(test.http_profile.dstl_get_service().dstl_read_all_data(100))
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.http_profile.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)


        test.log.step("11. For FTP profile send data with EOD flag.")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(100, eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("12. Close all services.")
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        try:
            test.tcp_server.dstl_server_close_port()
            test.ftp_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("problem with server objects")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
