# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0107274.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """	The intention is to verify the stability of IP services (TCP).
        A main tests purpose is to check modules behavior after a huge amount of closing and opening
        internet service connection and sending/receiving some of data in transparent mode.
        Test dedicated for IPv4
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        iterations = 500
        etx = 26
        data_2048 = 2048

        test.log.info("Executing script for test case: 'TC0107274.001 TcpTransparentSendReceiveLoad_ipv4'")
        test.log.step("1) Depends on Module: \r\n"
                      "- define connection profile using SICS command \r\n"
                      "- define PDP context/ NV bearer and activate it using SICA command")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile(),
                    critical=True)

        test.log.step("2) Define IPv4 TCP transparent client socket profile on module"
                      " (connection to echo server)")
        test.echo_server = EchoServer('IPv4', "TCP", test_duration=25)
        fqdn_server_address = test.echo_server.dstl_get_server_FQDN()
        test.socket = SocketProfile(test.dut, "9", connection_setup_object.dstl_get_used_cid(),
                                    protocol="tcp", ip_version='IPv4', etx_char="26",
                                    host=fqdn_server_address,
                                    port=test.echo_server.dstl_get_server_port())
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        for iteration in range(iterations+1):
            test.log.step("3) Open TCP client service and wait for write URC"
                          "\nIteration: {} of {} - start.".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile
                        (expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration"
                                       " will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Enter transparent (data) mode"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("5) Send 2048 bytes of data and receive echo from server"
                          "\nIteration: {} of {}".format(iteration, iterations))
            bytes_generated = dstl_generate_data(data_2048)
            test.expect(test.socket.dstl_get_service().dstl_send_data(bytes_generated, expected=""))
            test.sleep(3)

            test.log.step("6) Exit transparent mode"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, etx))

            test.log.step("7) Check amount of sent and read data"
                          " \nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == data_2048)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") == data_2048)

            test.log.step("8) Release connection. \nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("9) Wait 2,5 minutes. \nIteration: {} of {}".format(iteration, iterations))
            test.sleep(150)

            if iteration != iterations:
                test.log.step("10) Repeat steps from 3) to 9) {} times"
                              "\nIteration: {} of {} - end.".format(iterations, iteration, iterations))

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")


if "__main__" == __name__:
    unicorn.main()
