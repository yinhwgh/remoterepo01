# responsible: damian.latacz@globallogic.com
# location: Wroclaw
# TC0102310.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser, ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Check UDP connection in polling mode
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()
        test.echo_server = EchoServer("IPv4", "UDP")

    def run(test):
        sockets = ["UDP client", "UDP endpoint"]
        for loop, test.profile in enumerate(sockets, 1):
            test.log.step("1.{} Disable IP services URCs".format(loop))
            test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))

            test.log.step("2.{} Set {} connection to echo server".format(loop, test.profile))
            test.define_socket(test.profile)

            test.log.step("3.{} Open connection".format(loop))
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile())
            if test.profile == "UDP client":
                test.expect(not test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            else:
                test.expect(not test.socket.dstl_get_urc().dstl_is_sis_urc_appeared("5"))

            test.log.step("4.{} Check for ERROR with SISE command".format(loop))
            test.expect(test.dut.at1.send_and_verify("AT^SISE={}".format(test.profile_id)))
            test.expect("SISE: {},0".format(test.profile_id) in test.dut.at1.last_response)

            test.log.step("5.{} Check service state".format(loop))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("6.{} Write data".format(loop))
            test.write_data(test.profile)

            test.log.step("7.{} Check if there is data to read using peek operator".format(loop))
            test.expect(test.socket.dstl_get_parser().dstl_get_peek_value_of_data_to_read() > 0)

            test.log.step("8.{} Read data".format(loop))
            test.expect(len(test.socket.dstl_get_service().dstl_read_return_data(test.data_amount)) == test.data_amount)

            test.log.step("9.{} Close connection and check service state".format(loop))
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

            if test.profile == "UDP client":
                test.log.step("10. Repeat steps with UDP endpoint")

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            else:
                test.log.info("The server port has been closed successfully.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def define_socket(test, profile):
        test.profile_id = 0
        test.socket = SocketProfile(test.dut, test.profile_id, test.cid, protocol="udp")
        if profile == "UDP endpoint":
            test.socket.dstl_set_local_port(55555)
        else:
            test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

    def write_data(test, profile):
        test.data_amount = 1500
        if profile == "UDP client":
            test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(test.data_amount))
        else:
            udp_rem_client = "{}:{}".format(test.echo_server.dstl_get_server_ip_address(),
                                            test.echo_server.dstl_get_server_port())
            test.expect(test.socket.dstl_get_service().
                        dstl_send_sisw_command_and_data_UDP_endpoint(test.data_amount, udp_rem_client, eod_flag=0))
        test.sleep(10)


if "__main__" == __name__:
    unicorn.main()
