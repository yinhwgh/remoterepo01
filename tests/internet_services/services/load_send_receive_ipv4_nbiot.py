#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0104775.001, TC0104777.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_nbiot
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Intention:
        1. The intention is to verify the stability of IP services.
        2. A main tests purpose is to check modules behavior after a huge amount of closing and opening internet
            service connection and sending/receiving some of data.
        3. Test dedicated for IPv4 NBIoT devices
    Args:
        protocol (String): Internet Protocol to be used. Allowed values: 'TCP', 'UDP'."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_nbiot(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer("IPv4", test.protocol)

    def run(test):
        if test.protocol == "TCP":
            test.log.h2("Executing script for test case: 'TC0104775.001 TcLoadSendReceiveTcpClient_IPv4_NBIoT'")
        else:
            test.log.h2("Executing script for test case: 'TC0104777.001 LoadOpenSendUdpClient_IPv4_NBIoT'")

        test.log.step("1) Define connection profile or define and activate PDP context")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())
        test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

        test.log.step("2) Set IPv4 {} client socket profile on module.".format(test.protocol))
        test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol=test.protocol)
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        # executing steps 3-8: send 1358 and 12 bytes, repeat steps 3-7 50 times
        execute_test_scenario(test, step_init=3, data_1=1358, data_2=12, iterations=50)
        # executing steps 9-14: send 10 and 5 bytes, repeat steps 9-13 450 times
        execute_test_scenario(test, step_init=9, data_1=10, data_2=5, iterations=450)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")


def execute_test_scenario(test, step_init, data_1, data_2, iterations):
    for iteration in range(iterations + 1):
        test.log.step("{}) Open service and connect to echo {} server and wait for write URC. "
                      "\nIteration: {} of {} - start.".format(step_init, test.protocol, iteration, iterations))

        test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*O.*"))
        if 'OK' not in test.dut.at1.last_response:
            test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            continue
        test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("{}) Send the following data from module to {} server: \na. {} bytes \nb. {} bytes. "
                      "\nIteration: {} of {}".format(step_init+1, test.protocol, data_1, data_2,  iteration, iterations))

        test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_1))
        test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_2, append=True))

        test.log.step("{}) Read data received from {} echo server. "
                      "\nIteration: {} of {}".format(step_init+2, test.protocol, iteration, iterations))

        test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket.dstl_get_service().dstl_read_data(data_1))
        test.expect(test.socket.dstl_get_service().dstl_read_data(data_1))
        if test.socket.dstl_get_service().dstl_get_confirmed_read_length() == 0:
            test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1", 10)
            test.expect(test.socket.dstl_get_service().dstl_read_data(data_1))

        test.log.step("{}) Check amount of sent and read data. \nIteration: {} of {}".format(step_init+3, iteration, iterations))

        test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == data_1 + data_2)
        if test.protocol == "TCP":
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") == data_1 + data_2)
        else:
            udp_lost_data_counter = 0
            if test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") < data_1 + data_2:
                udp_lost_data_counter += 1
            if iteration == iterations:
                test.log.info("Lost data counter: {} of {}.".format(udp_lost_data_counter, iterations))
                test.expect(udp_lost_data_counter < iterations*0.2)
            else:
                test.log.info("Amount of lost UDP packets will be checked at the end of all iterations.")

        test.log.step("{}) Release connection. \nIteration: {} of {}".format(step_init+4, iteration, iterations))

        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

        if iteration != iterations:
            test.log.step("{}) Repeat steps from {}) to {}) {} times using IPv4 profile. "
                          "\nIteration: {} of {} - end.".format(step_init+5, step_init, step_init+4, iterations, iteration, iterations))


if "__main__" == __name__:
    unicorn.main()
