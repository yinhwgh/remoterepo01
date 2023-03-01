#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094917.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """The intention is to verify the stability of IP services (TCP).
        A main tests purpose is to check modules behavior after a huge amount of closing and opening internet
        service connection and sending/receiving some of data.\n
        Test dedicated for IPv4."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))

    def run(test):
        iterations = 1200
        data_1460 = 1460
        data_12 = 12

        test.log.info("Executing script for test case: 'TcLoadSendReceiveTcpClient_IPv4'")

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer('IPv4', "TCP", test_duration=8)

        test.log.step("1) Define connection profile or define and activate PDP context")

        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())
        test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

        test.log.step("2) Set IPv4 TCP client socket profile on module")

        test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp", ip_version='IPv4')
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        for iteration in range(iterations+1):
            test.log.step("3) Open service and connect to echo TCP server and wait for write URC. "
                          "\nIteration: {} of {} - start.".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Send the following data from module to TCP server: \na. 1460 bytes \nb. 12 bytes. "
                          "\nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_1460))
            test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_12))

            test.log.step("5) Read data received from TCP echo server. "
                          "\nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))
            test.expect(test.socket.dstl_get_service().dstl_read_data(data_12, skip_data_check=True))
            if test.socket.dstl_get_service().dstl_get_confirmed_read_length() == 0:
                test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1", 10)
                test.expect(test.socket.dstl_get_service().dstl_read_data(data_12))

            test.log.step("6) Check amount of sent and read data. \nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == data_1460 + data_12)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") == data_1460 + data_12)

            test.log.step("7) Release connection. \nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            if iteration != iterations:
                test.log.step("8) Repeat steps from 3) to 7) {} times using IPv4 profile. "
                              "\nIteration: {} of {} - end.".format(iterations, iteration, iterations))

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
