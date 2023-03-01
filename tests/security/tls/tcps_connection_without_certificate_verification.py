#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0094947.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP")

    def run(test):
        data_50 = 50
        test.log.info("TC0094947.001 - TcpsConnectionWithoutCertificateVerification")

        test.log.step("1) Define and activate PDP context / internet connection profile.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Define tcp client profile to SSL/TLS echo server and server certificate check parameter set "
                      "to off (0).")
        test.socket_service = SocketProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(),
                                            secure_connection=True, secopt="0")
        test.socket_service.dstl_set_parameters_from_ip_server(test.ssl_echo_server)
        test.socket_service.dstl_generate_address()
        test.expect(test.socket_service.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open socket profile")
        test.expect(test.socket_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4) Send some data from module to server and read echoed data")
        test.expect(test.socket_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50))
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_service.dstl_get_service().dstl_read_data(data_50))

        test.log.step("5) Compare sent/received data")
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_data_counter("tx") == data_50)
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_data_counter("rx") == data_50)

        test.log.step("6) Check client srv state")
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("7) Close socket.")
        test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("8) Open socket profile")
        test.expect(test.socket_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("9) Send some data with EOD flag from module to server.")
        test.expect(test.socket_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50, eod_flag="1"))
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("10) Check client srv state")
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_state() == ServiceState.CLOSING.value)

        test.log.step("11) Read data.")
        test.expect(test.socket_service.dstl_get_service().dstl_read_data(data_50))

        test.log.step("12) Check client srv state")
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("13) Compare sent/received data")
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_data_counter("tx") == data_50)
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_data_counter("rx") == data_50)

        test.log.step("14) Close and reset internet service profile.")
        test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_service.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):

        try:
            if not test.ssl_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("GenericIpServer was not created.")


if "__main__" == __name__:
    unicorn.main()