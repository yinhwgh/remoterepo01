#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093526.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.call.switch_to_command_mode import *
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """Testing operation of specific characters and data line transitions on UDP Transparent Socket Service."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut), critical=True)
        test.echo_server = EchoServer('IPv4', "UDP")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.connection_setup.dstl_load_and_activate_internet_connection_profile()
        test.dut.at1.send_and_verify("AT&D2")

    def run(test):
        test.log.info("Executing script for test case: 'TC0093526.001 SocketUdpTransparentToCommandMode'")

        test.log.step("1. Set up Socket Transparent UDP Client service to the UDP echo server. "
                      "Open the service and check its IP address.")
        test.socket = SocketProfile(test.dut, "1", test.connection_setup.dstl_get_used_cid(), protocol="udp", etx_char=26)
        test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.expect(test.socket.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.socket.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4'))

        test.log.step("2. Enter transparent mode, then send 5x100 bytes of data and receive echoed bytes.")
        test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())
        data = dstl_generate_data(100)
        test.expect(test.socket.dstl_get_service().dstl_send_data(data, expected="", repetitions=5))
        test.expect(test.dut.at1.wait_for(data*5))
        amount_of_sent_data = len(data)*5

        test.log.step("3. Send \"+++\" sequence, but followed by any other character.")
        test_sequence = "+++a"
        test.expect(test.socket.dstl_get_service().dstl_send_data(test_sequence, expected=""))
        test.dut.at1.wait_for(test_sequence)
        test.sleep(5)
        test.expect('OK' not in test.dut.at1.last_response)
        amount_of_sent_data += len(test_sequence)

        test.log.step("4. Send and receive DLE character to the echo server (DLE + DLE).")
        test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        test.expect(test.socket.dstl_get_service().dstl_send_data(bytes(chr(16), encoding='ascii'), expected=""))
        test.sleep(5)
        test.expect('OK' not in test.dut.at1.last_response)
        amount_of_sent_data += 1

        test.log.step("5. Escape transparent mode using \"+++\" sequence. Check amount of sent data.")
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.expect(test.socket.dstl_get_service().dstl_check_if_module_in_command_mode())
        test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_sent_data)

        test.log.step("6. Repeat step 2 and escape transparent mode using ETX character (DLE + ETX)."
                      "Check amount of sent data.")
        test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())
        data = dstl_generate_data(100)
        test.expect(test.socket.dstl_get_service().dstl_send_data(data, expected="", repetitions=5))
        test.expect(test.dut.at1.wait_for(data*5, silent=True))
        amount_of_sent_data += len(data)*5

        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_sent_data)

        test.log.step("7. Repeat step 2 and escape transparent mode using DTR toggle method. Check amount of sent data.")
        test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())
        data = dstl_generate_data(100)
        test.expect(test.socket.dstl_get_service().dstl_send_data(data, expected="", repetitions=5))
        test.expect(test.dut.at1.wait_for(data*5, silent=True))
        amount_of_sent_data += len(data)*5

        test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
        test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_sent_data)

        test.log.step("8. Close and release all services.")
        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
