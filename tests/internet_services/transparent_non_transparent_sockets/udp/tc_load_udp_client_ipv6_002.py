#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093604.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """The intension is to verify the stability of IP service (UDP) during IPv6 connection.
            A main purpose of this test is to check UDP Client behavior while sending/receiving a lot of data.
            Test dedicated for NBIoT products with small data buffer."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        iterations = 21
        amount_of_data_blocks_upload = 10
        data_block_size_1358 = 1358
        data_block_size_42 = 42
        amount_of_data_blocks_download = 20
        data_block_size_859 = 859

        test.log.info("Executing script for test case: 'TC0093604.002 TcLoadUdpClient_IPv6'")

        test.echo_server = EchoServer("IPv6", "UDP", test_duration=2)

        test.log.step("1) Define PDP context and activate it.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())
        test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

        test.log.step("2) Set IPv6 service profile on module for non-transparent UDP client socket.")
        socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="udp",
                                    alphabet=1, ip_version="IPv6")
        socket.dstl_set_parameters_from_ip_server(test.echo_server)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())

        for iteration in range(1, iterations+1):
            test.log.step("3) On module open connection to UDP server and wait for write URC.\nIteration: {} of {}."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Send 100 bytes with End of data flag.\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(100, "1"))

            test.log.step("5) Send the following data from module to UDP server {} times: \na. 1358 bytes "
                          "\nb. 42 bytes\nIteration: {} of {}.".format(amount_of_data_blocks_upload, iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(data_block_size_1358,
                                                                        repetitions=amount_of_data_blocks_upload))
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(data_block_size_42,
                                                                        repetitions=amount_of_data_blocks_upload))

            test.log.step("6) Send End of data flag from module to server.\nIteration: {} of {}."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_send_sisw_command(0, "1", expected="OK"))

            test.log.step("7) Check amount of sent data and service profile state.\nIteration: {} of {}."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("TX")
                        == 100 + amount_of_data_blocks_upload * (data_block_size_1358 + data_block_size_42))
            test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("8) Close service profile.\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("9) Check service profile state.\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

            test.log.step("10) Repeat steps 3-9 {} times.".format(iterations - iteration))

        test.log.step("11) Delete service profile for non-transparent UDP client socket.")
        test.expect(socket.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.echo_server.dstl_server_close_port())
        test.echo_server = EchoServer("IPv6", "UDP", test_duration=2)

        test.log.step("12) Set IPv6 service profile on module for non-transparent UDP client socket.")
        socket.dstl_set_port(test.echo_server.dstl_get_server_port())
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())

        for iteration in range(1, iterations+1):
            test.log.step("13) Open connection to UDP echo server and wait for write URC.\nIteration: {} of {}."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("14) Send 859 bytes from module to UDP echo server {} times.\nIteration: {} of {}."
                          .format(amount_of_data_blocks_download, iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_send_sisw_command_and_data(data_block_size_859,
                                                                    repetitions=amount_of_data_blocks_download))

            test.log.step("15) Read echo data received from UDP server.\nIteration: {} of {} - start."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_read_data(data_block_size_859,
                                                                 repetitions=amount_of_data_blocks_download))

            test.log.step("16) Check amount of sent/received data and service profile state.\nIteration: {} of {}."
                          .format(iteration, iterations))
            test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("TX") ==
                        amount_of_data_blocks_download * data_block_size_859)
            test.expect(socket.dstl_get_parser().dstl_get_service_data_counter("RX") >=
                        amount_of_data_blocks_download * data_block_size_859 * 0.8)
            test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("17) Close service profile.\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("18) Check service profile state.\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

            test.log.step("19) Repeat steps 13-18 {} times.".format(iterations - iteration))

        test.log.step("20) Delete service profile for non-transparent UDP client socket.")
        test.expect(socket.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
