# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107952.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior while opening and closing socket connection

    Description:
    1) Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2) Define non-transparent tcp client profile using SISS command (connection to tcp server)
    3) Open TCP client using SISO command
    4) Check service state using AT^SISO? command
    5) Close TCP client using SISC command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer("IPv4", "TCP")

    def run(test):
        test.log.info("TC0107952.001 TcpSocketOpenClose_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) Define non-transparent tcp client profile using SISS command '
                      '(connection to tcp server)')
        test.tcp_client = SocketProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid(),
                                        protocol="tcp", alphabet=1)
        test.tcp_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.tcp_client.dstl_generate_address()
        test.expect(test.tcp_client.dstl_get_service().dstl_load_profile())

        test.log.step('3) Open TCP client using SISO command')
        test.expect(test.tcp_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('4) Check service state using AT^SISO? command')
        test.log.info("executed in previous step")

    def cleanup(test):
        test.log.step('5) Close TCP client using SISC command')
        test.expect(test.tcp_client.dstl_get_service().dstl_close_service_profile())
        test.tcp_client.dstl_get_service().dstl_reset_service_profile()
        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()