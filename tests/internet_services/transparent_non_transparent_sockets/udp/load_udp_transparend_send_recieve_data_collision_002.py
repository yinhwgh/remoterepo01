# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0093513.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses, \
    dstl_switch_to_command_mode_by_etxchar


class Test(BaseTest):
    """	Check module stability during upload/download data at the same time
    to/from remote UDP endpoint. Test for CAT-M and NBIoT products.."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer('IPv4', "UDP", test_duration=4, extended=True)

    def run(test):
        data_length = 1024
        data = dstl_generate_data(data_length)
        packet_amount = 8

        test.log.step("1) Setup Internet Service Profile for Transparent UDP client (etx=30) "
                      "if possible use 2 interfaces")
        test.connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
        test.socket_interface_1 = SocketProfile(test.dut, "0",
                                    test.connection_setup_object.dstl_get_used_cid(),
                                    protocol="udp", ip_version='IPv4', etx_char="26")
        test.socket_interface_1.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_interface_1.dstl_generate_address()
        test.socket_interface_1.dstl_get_service().dstl_load_profile()

        test.socket_interface_2 = SocketProfile(test.dut, "1",
                                                test.connection_setup_object.dstl_get_used_cid(),
                                                protocol="udp", ip_version='IPv4', etx_char="26",
                                                device_interface="at2")
        test.socket_interface_2.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_interface_2.dstl_generate_address()
        test.socket_interface_2.dstl_get_service().dstl_load_profile()

        test.log.step("2) Activate Internet Connection/PDP context")
        test.expect(test.connection_setup_object.
                    dstl_load_and_activate_internet_connection_profile(), critical=True)

        test.log.step("3) Open the profile and wait for proper URC, if possible use 2 interfaces")
        test.expect(test.socket_interface_1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_interface_2.dstl_get_service().dstl_open_service_profile())

        test.log.step("4) Switch to Transparent mode if possible use 2 interfaces")
        test.expect(test.socket_interface_1.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_interface_2.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("5) Perform upload/download in parallel (8MB) if possible use 2 interfaces")
        for i in range(1000):
            test.log.info("Loop {} from 10000".format(i))
            test.socket_interface_1.dstl_get_service().dstl_send_data(data,
                                                                      repetitions=packet_amount,
                                                                      expected="", delay_in_ms=50)
            test.socket_interface_2.dstl_get_service().dstl_send_data(data,
                                                                      repetitions=packet_amount,
                                                                      expected="", delay_in_ms=50)

        test.log.step("6) Switch back to command mode (ETX) if possible use 2 interfaces")
        test.sleep(10)
        test.switch_to_command_mode()
        test.sleep(5)

        test.log.step("7) Close the profile if possible use 2 interfaces")
        test.expect(test.socket_interface_1.dstl_get_parser().
                    dstl_get_service_data_counter("tx") > data_length * packet_amount * 0.8)
        test.expect(test.socket_interface_1.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.socket_interface_1.dstl_get_parser().dstl_get_service_data_counter("rx") >
                    (data_length * packet_amount * 0.8))
        test.expect(test.socket_interface_2.dstl_get_parser().
                    dstl_get_service_data_counter("tx") > data_length * packet_amount * 0.8)
        test.expect(test.socket_interface_2.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.socket_interface_2.dstl_get_parser().dstl_get_service_data_counter("rx") >
                    (data_length * packet_amount * 0.8))
        test.expect(test.socket_interface_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_interface_2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_interface_1.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_interface_2.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")

            if not test.socket_interface_1.\
                    dstl_get_service().dstl_check_if_module_in_command_mode() | \
                   test.socket_interface_2.dstl_get_service().\
                           dstl_check_if_module_in_command_mode():
                test.sleep(5)  # sleep so pluses can be used properly
                dstl_switch_to_command_mode_by_pluses(test.dut)
                dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        except AttributeError:
            test.log.error("Object was not created.")

    def switch_to_command_mode(test):
        if not test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26,)) | \
               test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26,
                                                                  device_interface="at2")):
            test.dut.at1.close()
            test.dut.at1.open()
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface="at2"))
        test.expect(test.socket_interface_1.dstl_get_service().
                    dstl_check_if_module_in_command_mode(), critical=True)
        test.expect(test.socket_interface_2.dstl_get_service().
                    dstl_check_if_module_in_command_mode(), critical=True)


if "__main__" == __name__:
    unicorn.main()
