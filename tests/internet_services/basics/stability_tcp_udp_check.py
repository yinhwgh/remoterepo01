#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0103837.001


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """To check module stability during TCP and UDP Duration test"""

    def setup(test):
        test.total_hours = 3*24
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.tcp_echo_server = EchoServer("IPv4", "TCP", test_duration=test.total_hours+1)
        test.udp_echo_server = EchoServer("IPv4", "UDP", test_duration=test.total_hours+1)

    def run(test):
        test.log.info("Executing script for test case: 'TC0103837.001 StabilityTcpUdpCheck'")

        test.log.step("1) Attach Module to NW")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Enable on Module\n - URCs related to Internet service commands\n"
                      " - Network Registration Status\n - Error Message Format")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(test.dut.at1.send_and_verify("at+creg=2", expect=".*O.*"))
        test.expect(test.dut.at1.send_and_verify("at+cereg=2"))
        test.expect(test.dut.at1.send_and_verify("at+cmee=2"))

        test.log.step("3) Depends on Module define PDP context and activate it / define IPv4 Connection Profile")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4) Define Transparent TCP Client to any echo server ")
        socket_tcp = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp", etx_char=26)
        socket_tcp.dstl_set_parameters_from_ip_server(test.tcp_echo_server)
        socket_tcp.dstl_generate_address()
        test.expect(socket_tcp.dstl_get_service().dstl_load_profile())

        test.log.step("5) Define Non-Transparent UDP Client to any echo server ")
        socket_udp = SocketProfile(test.dut, "2", connection_setup_object.dstl_get_used_cid(), protocol="udp")
        socket_udp.dstl_set_parameters_from_ip_server(test.udp_echo_server)
        socket_udp.dstl_generate_address()
        test.expect(socket_udp.dstl_get_service().dstl_load_profile())

        for current_hour in range(1, test.total_hours+1):
            test.log.step("6) Every hour perform the following steps: "
                          "- Current hour: {} of {}.".format(current_hour, test.total_hours))
            test.log.step(" - Open TCP Transparent Client")
            test.expect(socket_tcp.dstl_get_service().dstl_open_service_profile())
            test.expect(socket_tcp.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step(" - Enter Transparent (data) Mode")
            test.expect(socket_tcp.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step(" - Send 500 bytes of data")
            data = dstl_generate_data(500)
            test.expect(socket_tcp.dstl_get_service().dstl_send_data(data, expected=""))

            test.log.step(" - Wait for Echo data")
            test.expect(test.dut.at1.wait_for(data, silent=True))

            test.log.step(" - Leave Transparent (data) Mode")
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

            test.log.step(" - Check service states with AT^SISO?")
            test.expect(socket_tcp.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step(" - Close TCP Client")
            test.expect(socket_tcp.dstl_get_service().dstl_close_service_profile())

            test.log.step(" - Open UDP Non-transparent Client")
            test.expect(socket_udp.dstl_get_service().dstl_open_service_profile())
            test.expect(socket_udp.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step(" - Send 300 bytes of data")
            test.expect(socket_udp.dstl_get_service().dstl_send_sisw_command_and_data(60, repetitions=5, append=True))

            test.log.step(" - Wait for Echo data and Read them")
            test.expect(socket_udp.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(len(socket_udp.dstl_get_service().dstl_read_return_data(60, repetitions=5)) >= 60*4)

            test.log.step(" - Check service states with AT^SISO?")
            test.expect(socket_udp.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step(" - Close UDP Client")
            test.expect(socket_udp.dstl_get_service().dstl_close_service_profile())

            test.log.step("7) Perform test for at least 3 days")
            test.log.info("Current test duration: {} of {}. Waiting one hour.".format(current_hour, test.total_hours))
            test.sleep(60*60)
            buffer = test.dut.at1.read()
            test.expect("CEREG: 0" not in buffer and "CEREG: 2" not in buffer and "CEREG: 4" not in buffer)
            test.expect("CREG: 0" not in buffer and "CREG: 2" not in buffer and "CREG: 4" not in buffer)

    def cleanup(test):
        try:
            if not test.tcp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on TCP server.")
            if not test.udp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on UDP server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
