# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107984.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior while basic connection to TCPS server

    Description:
    1) Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2) Define Non-transparent TCPS Client profile using SISS command (connection to TCPS Server)
    - set secopt parameter to 0
    3) Open TCPS client using SISO command
    4) Check service state using AT^SISO? command
    5) Close TCPS client using SISC command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP")
        test.sleep(5)

    def run(test):
        test.log.info("TC0107984.001 TcpsSecureConnection_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) Define Non-transparent TCPS Client profile using SISS command '
                      '(connection to TCPS Server)\r\n- set secopt parameter to 0')
        test.tcps_client = SocketProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(),
                                           secure_connection=True, secopt="0")
        test.tcps_client.dstl_set_parameters_from_ip_server(test.ssl_echo_server)
        test.tcps_client.dstl_generate_address()
        test.expect(test.tcps_client.dstl_get_service().dstl_load_profile())

        test.log.step('3) Open TCPS client using SISO command')
        test.expect(test.tcps_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('4) Check service state using AT^SISO? command')
        test.log.info("executed in previous step")

    def cleanup(test):
        test.log.step('5) Close TCPS client using SISC command')
        test.expect(test.tcps_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.tcps_client.dstl_get_service().dstl_reset_service_profile())
        try:
            test.ssl_echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()