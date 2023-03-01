# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094696.001 TC0094696.002

import unicorn
from core.basetest import BaseTest

from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState

from dstl.network_service.register_to_network import dstl_enter_pin

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.generate_data import dstl_generate_data

from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses

from dstl.configuration.configure_dcd_line_mode import dstl_set_dcd_line_mode

from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """This test is provided to verify the behavior of the ME's of the DCD line. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut), critical=True)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        data_length = 100
        test.log.info("Executing script for test case: TC0094696.001/002 - "
                      "TransparentUDPClientCheckDCDLine")

        test.log.step("1. Enable DCD line detection for IP services (AT&C2)")
        test.expect(dstl_set_dcd_line_mode(test.dut, 2))

        test.log.step("2. Defined and activated internet connection.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.expect(connection_setup.dstl_activate_internet_connection(), critical=True)

        test.log.step("3. Configure and open UDP endpoint on Remote, or start echo server.")
        test.echo_server = EchoServer('IPv4', "UDP")

        test.log.step("4. Configure transparent UDP client on DUT.")
        test.socket = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                    protocol="udp", etx_char=26)
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open service on DUT.")
        test.expect(test.socket.dstl_get_service().dstl_open_service_profile())

        test.log.step("6. Check service state and DCD line state on DUT side.")
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step("7. Send some data from DUT to Remote and send it back to DUT.")
        test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_length))
        test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=10)

        test.log.step("8. Check service state and DCD line state on DUT side.")
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step("9. Establish transparent mode on DUT and send some data to Remote.")
        test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())
        data = dstl_generate_data(data_length)
        test.expect(test.socket.dstl_get_service().dstl_send_data(data, expected=""))
        test.expect(test.dut.at1.wait_for(data))

        test.log.step("10. Leave the transparent mode (+++). Check service state and DCD "
                      "line state on DUT side.")
        test.sleep(2) # sleep so pluses can work
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.expect(test.socket.dstl_get_service().dstl_check_if_module_in_command_mode())
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.dut.at1.connection.cd)

        test.log.step("11. Close services. Check service state and DCD line state on DUT side.")
        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.ALLOCATED.value)
        test.expect(not test.dut.at1.connection.cd)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
