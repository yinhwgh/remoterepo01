#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0095086.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses


class Test(BaseTest):
    """	Check module stability after huge amount of open / close action.
        After opening the service, module have to send and receive data."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


    def run(test):
        iterations = 30
        data_length = 1024
        data = dstl_generate_data(data_length)
        packet_amount = 1024

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.echo_server = EchoServer('IPv4', "UDP", test_duration=8, extended=True)
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        repetition_command = test.echo_server.dstl_server_get_repeat_command(2)
        repetition_command_end = test.echo_server.dstl_server_get_repeat_command(1)
        repetition_command_len = len(repetition_command)

        test.log.step("	1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_enter_pin(test.dut), critical=True)
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Activate URC mode.")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.log.step("3) Depends on product: set Connection Profile (GPRS) / Define PDP Context.")
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())

        test.log.step("4) Setup Internet Service Profile for Transparent UDP Client to the remote "
                      "UDP Endpoint (set etx only for compatibility).")
        test.socket = SocketProfile(test.dut, "0", connection_setup_object.dstl_get_used_cid(),
                                    protocol="udp", ip_version='IPv4', etx_char="26")
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.log.step("5) Depends on product - Activate PDP context.")
        test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

        test.log.step("6) Check for address assignment.")
        test.expect(connection_setup_object.dstl_get_pdp_address(cid="1"))

        for iteration in range(iterations+1):
            test.log.step("7) Open the service and wait for proper URC."
                          "\nIteration: {} of {} - start.".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_open_service_profile
                        (expected=".*OK.*|.*ERROR.*"))
            if 'OK' not in test.dut.at1.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration "
                                       "will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue

            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("8) Switch to transparent Mode."
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("9) Send 1024KB and wait for 2048KB of data."
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.log.info("correctness of amount of data will be checked in later step")
            if iteration == 0:
                test.socket.dstl_get_service().dstl_send_data(repetition_command, expected="")

            test.socket.dstl_get_service().dstl_send_data(data, repetitions=packet_amount,
                                                          expected="", delay_in_ms=200)

            if iteration == iterations:
                test.socket.dstl_get_service().dstl_send_data(repetition_command_end, expected="")

            test.log.step("10) Switch to command mode"
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.sleep(5)  # sleep so pluses can be used properly
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))

            test.log.step("11) Check amount of send and received data."
                          "\nIteration: {} of {}".format(iteration, iterations))
            test.expect((test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                        data_length*packet_amount + repetition_command_len) or
                        (test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                        data_length*packet_amount))
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.UP.value)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("rx") > (
                        data_length*2*packet_amount*0.8))

            test.log.step("12) Close the connection.")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            if iteration != iterations:
                test.log.step("13) Wait 2s and repeat step 7-12 {} times."
                              "\nIteration: {} of {} - end.".format(iterations, iteration,
                                                                    iterations))
                test.sleep(2)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")

            if not test.socket.dstl_get_service().dstl_check_if_module_in_command_mode():
                test.sleep(5)  # sleep so pluses can be used properly
                dstl_switch_to_command_mode_by_pluses(test.dut)

            dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
