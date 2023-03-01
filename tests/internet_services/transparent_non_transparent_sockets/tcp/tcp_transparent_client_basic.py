# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107991.001

import unicorn
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior during TCP Transparent Client operations

    Description:
    1. Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2. Set Error Message Format to 2 with AT+CMEE=2 command
    3. Define Transparent TCP Client profile using SISS command (connection to TCP Server)
    - set etx char to 26
    4. Open TCP client using SISO command
    5. Check service state using AT^SISO? command
    6. Enter Transparent (data) mode using SIST command
    7. Send 50 bytes and receive echo data from Server
    8. Exit transparent mode
    9. Check service state and Tx, Rx counters using AT^SISO? command
    10. Close TCP Client using SISC command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer("IPv4", "TCP")
        test.etx = 26
        test.data_length = 50

    def run(test):
        test.log.info("TC0107991.001 TcpTransparentClient_basic")
        test.log.step('1. Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Set Error Message Format to 2 with AT+CMEE=2 command')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('3. Define Transparent TCP Client profile using SISS command '
                      '(connection to TCP Server)\r\n- set etx char to 26')
        test.tcp_client = SocketProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid(),
                                        protocol="tcp", alphabet=1, etx_char=test.etx)
        test.tcp_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.tcp_client.dstl_generate_address()
        test.expect(test.tcp_client.dstl_get_service().dstl_load_profile())

        test.log.step('4. Open TCP client using SISO command')
        test.expect(test.tcp_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('5. Check service state using AT^SISO? command')
        test.log.info("executed in previous step")

        test.log.step('6. Enter Transparent (data) mode using SIST command')
        test.expect(test.tcp_client.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step('7. Send 50 bytes and receive echo data from Server')
        data = dstl_generate_data(test.data_length)
        test.expect(test.tcp_client.dstl_get_service().dstl_send_data(data, expected=""))
        test.sleep(5)

        test.log.step('8. Exit transparent mode')
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, test.etx))

        test.log.step('9. Check service state and Tx, Rx counters using AT^SISO? command')
        test.expect(test.tcp_client.dstl_get_parser().dstl_get_service_state() ==
                                                                        ServiceState.UP.value)
        test.expect(test.tcp_client.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                                                                                test.data_length)
        test.expect(test.tcp_client.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                                                                                test.data_length)

    def cleanup(test):
        test.log.step('10. Close TCP client using SISC command')
        test.expect(test.tcp_client.dstl_get_service().dstl_close_service_profile())
        test.tcp_client.dstl_get_service().dstl_reset_service_profile()
        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()