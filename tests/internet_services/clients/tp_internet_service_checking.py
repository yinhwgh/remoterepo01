#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0092725.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """Intention: Checking if three Internet Service Setup Profile's can be used in parallel."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        data_50 = 50

        test.log.info("TC0092725.001 - TpInternetServiceChecking")
        test.log.step("1) Define PDP context for Internet services and activate Internet service connection")
        test.connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Define HTTP post profile")
        http_profile_id = "0"
        hc_cont_len_150 = 150
        test.http_server = HttpServer("IPv4")
        http_service = HttpProfile(test.dut, http_profile_id, test.connection_setup_object.dstl_get_used_cid(),
                                   hc_cont_len=hc_cont_len_150, http_path="post", http_command="post",
                                   host=test.http_server.dstl_get_server_ip_address(),
                                   port=test.http_server.dstl_get_server_port())
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open HTTP profile and send data")
        http_service.dstl_get_service().dstl_open_service_profile()
        test.expect(http_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(http_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50))

        test.log.step("4) Define FTP put profile")
        ftp_profile_id = "1"
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup_object.dstl_get_used_cid())
        ftp_service = FtpProfile(test.dut, ftp_profile_id, test.connection_setup_object.dstl_get_used_cid(),
                                      alphabet="1", command="put", files="test.txt")
        ftp_service.dstl_set_parameters_from_ip_server(test.ftp_server)
        ftp_service.dstl_generate_address()
        test.expect(ftp_service.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open FTP profile and send data.")
        test.expect(ftp_service.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(ftp_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50))

        test.log.step("6) Define Socket profile.")
        ftp_profile_id = "2"
        test.echo_server = EchoServer("IPv4", "TCP")
        tcp_service = SocketProfile(test.dut, ftp_profile_id, test.connection_setup_object.dstl_get_used_cid())
        tcp_service.dstl_set_parameters_from_ip_server(test.echo_server)
        tcp_service.dstl_generate_address()
        test.expect(tcp_service.dstl_get_service().dstl_load_profile())

        test.log.step("7) Open Socket profile and send data.")
        test.expect(tcp_service.dstl_get_service().dstl_open_service_profile())
        test.expect(tcp_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(tcp_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50))

        test.log.step("8) Check Service and Socket state for all opened profiles")
        test.expect(http_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(ftp_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(tcp_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.expect(http_service.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(ftp_service.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(tcp_service.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("9) For Socket profile send data with EOD flag")
        test.expect(tcp_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50, eod_flag="1"))

        test.log.step("10) For HTTP profile send data with EOD flag (if supported)")
        if test.dut.project == "SERVAL" or "COUGAR":
            test.log.info("Product {} doesn't support EOD flag for HTTP profile".format(test.dut.project))
        else:
            test.log.error("Step not implemented for product {}".format(test.dut.project))

        test.log.step("11) For FTP profile send data with EOD flag")
        test.expect(ftp_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50, eod_flag="1"))

        test.log.step("12) Close all services")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())
        test.expect(ftp_service.dstl_get_service().dstl_close_service_profile())
        test.expect(tcp_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_delete_file("test.txt")
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
