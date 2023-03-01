#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC0106041.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_vbatt_via_dev_board
from dstl.configuration.shutdown_smso import dstl_shutdown_smso

class Test(BaseTest):
    """The intention is to verify the stability of IP services (TCP).
         Check if the module is robust against unexpected loss after tcp send and receive.
    Args:
        ip_version (String): Internet Protocol version to be used. Allowed values: 'IPv4', 'IPv6'.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        iterations = 2000
        data_1460 = 1460
        data_12 = 12

        test.log.info("Executing script for test case: 'TcLoadSendReceiveTcpClient_{}'".format(test.ip_version))

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer(test.ip_version, "TCP", test_duration=2)

        for iteration in range(iterations + 1):
             test.expect(dstl_enter_pin(test.dut))
             test.expect(dstl_register_to_network(test.dut))
             test.log.step("1) Define connection profile or define and activate PDP context""\nIteration: {} of {} - start.".format(iteration, iterations))

             connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version)
             test.expect(connection_setup_object.dstl_load_internet_connection_profile())
             test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

             test.log.step("2) Set {} TCP client socket profile on module".format(test.ip_version))

             test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp",
                                    alphabet=1, ip_version=test.ip_version)
             test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
             test.socket.dstl_generate_address()
             test.expect(test.socket.dstl_get_service().dstl_load_profile())

             test.log.step("3) Open service and connect to echo TCP server and wait for write URC. ")

             test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*O.*"))
             test.sleep(10)
             if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
             test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

             test.log.step("4) Send the following data from module to TCP server: \na. 1460 bytes \nb. 12 bytes. "
                          "\nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_1460))
             test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_12, append=True))

             test.log.step("5) Read data received from TCP echo server. "
                          "\nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
             test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))
             test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))
             if test.socket.dstl_get_service().dstl_get_confirmed_read_length() == 0:
                test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1", 10)
                test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))

             test.log.step("6) Check amount of sent and read data. \nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == data_1460 + data_12)
             test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") == data_1460 + data_12)

             test.log.step("7) Release connection. \nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
             test.dut.dstl_turn_off_vbatt_via_dev_board()
             test.sleep(2)
             test.dut.dstl_turn_on_vbatt_via_dev_board()
             test.dut.devboard.send_and_verify("MC:IGT=555", ".*OK.*")

             if iteration != iterations:
                test.log.step("8) Repeat steps from 1) to 7) {} times using {} profile. "
                              "\nIteration: {} of {} - end.".format(iterations, test.ip_version, iteration, iterations))


        for iteration in range(iterations + 1):
             test.expect(dstl_enter_pin(test.dut))
             test.expect(dstl_register_to_network(test.dut))
             test.log.step("1) Define connection profile or define and activate PDP context""\nIteration: {} of {} - start.".format(iteration, iterations))

             connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version)
             test.expect(connection_setup_object.dstl_load_internet_connection_profile())
             test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

             test.log.step("2) Set {} TCP client socket profile on module".format(test.ip_version))

             test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp",
                                    alphabet=1, ip_version=test.ip_version)
             test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
             test.socket.dstl_generate_address()
             test.expect(test.socket.dstl_get_service().dstl_load_profile())

             test.log.step("3) Open service and connect to echo TCP server and wait for write URC. ")

             test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*O.*"))
             if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
             test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

             test.log.step("4) Send the following data from module to TCP server: \na. 1460 bytes \nb. 12 bytes. "
                          "\nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_1460))
             test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_12, append=True))

             test.log.step("5) Read data received from TCP echo server. "
                          "\nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
             test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))
             test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))
             if test.socket.dstl_get_service().dstl_get_confirmed_read_length() == 0:
                test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1", 10)
                test.expect(test.socket.dstl_get_service().dstl_read_data(data_1460))

             test.log.step("6) Check amount of sent and read data. \nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == data_1460 + data_12)
             test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") == data_1460 + data_12)

             test.log.step("7) Release connection. \nIteration: {} of {}".format(iteration, iterations))

             test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
             test.expect(dstl_shutdown_smso(test.dut))
             test.dut.dstl_turn_off_vbatt_via_dev_board()
             test.sleep(4)
             test.dut.dstl_turn_on_vbatt_via_dev_board()
             test.dut.devboard.send_and_verify("MC:IGT=555", ".*OK.*")

             if iteration != iterations:
                test.log.step("8) Repeat steps from 1) to 7) {} times using {} profile. "
                              "\nIteration: {} of {} - end.".format(iterations, test.ip_version, iteration, iterations))

    def cleanup(test):
             pass


if "__main__" == __name__:
    unicorn.main()
