# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0107264.001


import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr


class Test(BaseTest):
    """ The intention is to verify the stability of IP services (TCP).
    A main tests purpose is to check modules behavior after a huge amount of closing
    and opening internet service connection and sending/receiving some of data.
    Test dedicated for IPv4 """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, 'on')
        test.expect(test.dut.at1.send_and_verify('AT&D2'))
        try:
            test.dut.devboard.send_and_verify("mc:asc0=ext", "OK")
        except AttributeError:
            test.log.warn("dut_devboard is not defined in configuration file")
        test.echo_server = EchoServer('IPv4', 'TCP', test_duration=40)

    def run(test):
        test.log.info("Executing script for test case: 'TC0107264.001 "
                      "TcLoadSendReceiveTcpClientPdp_ipv4'")
        iterations = 3000
        data_packet_size = 1024

        test.log.step("1) Attach Module to network on first APN")
        conn_setup_1st = dstl_get_connection_setup_object(test.dut)
        test.expect(conn_setup_1st.dstl_load_internet_connection_profile())
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Define connection profile or define and activate PDP context "
                      "on second APN (IPv4)")
        test.conn_setup_2nd = dstl_get_connection_setup_object(test.dut, ip_public='True',
                                                               device_interface='at2')
        test.conn_setup_2nd.cgdcont_parameters['cid'] = '2'
        test.expect(test.conn_setup_2nd.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Set IPv4 TCP client socket profile on module (connection on second APN)")
        test.socket = SocketProfile(test.dut, "1", test.conn_setup_2nd.dstl_get_used_cid(),
                                    device_interface='at2', protocol="tcp")
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        for iteration in range(1, iterations+1):
            test.log.step("4) On second interface activate ppp connection using ATD*99***1# command"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.dut.at1.send_and_verify('ATD*99***1#', expect='CONNECT',
                                                     wait_for='CONNECT'))

            test.log.step("5) Open service and connect to echo TCP server and wait for write URC"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile())

            test.log.step("6) Send the following data from module to TCP server: "
                          "\r\n a. 1024 bytes \r\n b. 1024 bytes"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service()
                        .dstl_send_sisw_command_and_data(data_packet_size))
            test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
            test.expect(test.socket.dstl_get_service()
                        .dstl_send_sisw_command_and_data(data_packet_size))

            test.log.step("7) Read data received from TCP echo server"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_read_data(data_packet_size,
                                                                      repetitions=2))

            test.log.step("8) Check amount of sent and read data"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter('tx')
                        == data_packet_size*2)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter('rx')
                        == data_packet_size*2)

            test.log.step("9) Close TCP Clients profile"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("10) Deactivate PDP context (or wait inactTo timer for SICS profile)"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.conn_setup_2nd.dstl_deactivate_internet_connection())

            test.log.step("11) On second interface deactivate ppp connection (toggle DTR line)"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))

            test.log.step("12) On second interface enable AT commands echo using ATE1 command"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.dut.at1.send_and_verify('ATE1'))

            test.log.step("13) Activate second PDP context again."
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.conn_setup_2nd.dstl_activate_internet_connection())

            test.log.step("14) Repeat steps from 4) to 13) {} times using IPv4 profile"
                          "\nAlready done {} iterations".format(iterations, iteration))

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            if not test.socket.dstl_get_service().dstl_check_if_module_in_command_mode():
                dstl_switch_to_command_mode_by_dtr(test.dut)
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")
        try:
            test.conn_setup_2nd.dstl_deactivate_internet_connection()
        except AttributeError:
            test.log.error("Socket object was not created.")


if "__main__" == __name__:
    unicorn.main()
