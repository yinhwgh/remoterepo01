# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107986.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """
    Intention:
    To check that disconnecting client by server works fine

    Description:
    1) Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2) On DUT define Transparent TCP Listener profile using SISS command
    3) On DUT open TCP Listener using SISO command
    4) On DUT check service state using AT^SISO? command
    5) On REM define TCP Client and send connection request to Listener
    6) On DUT wait for connection request and reject it using SISH command
    7) On DUT check service state using AT^SISO? command
    8) From REM send second connection request to Listener
    9) On DUT accept incoming connection using SISO command
    10) On DUT check service state using AT^SISO? command
    11) On DUT finish connection with Client using SISH command
    12) On DUT check service state using AT^SISO? command
    13) Close TCP Listener and Client profiles
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.listener_port = 50000
        test.etx_char = 26
        test.ip_version = "IPv4"
        test.echo_server = EchoServer(test.ip_version, 'TCP', extended=True)

    def run(test):
        test.log.info("TC0107986.001 TcpListenerSish_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) On DUT define Transparent TCP Listener profile using SISS command')
        test.tcp_listener = SocketProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid(),
                                        protocol="tcp", alphabet=1, host="listener",
                                        localport=test.listener_port, etx_char=test.etx_char)
        test.tcp_listener.dstl_generate_address()
        test.expect(test.tcp_listener.dstl_get_service().dstl_load_profile())

        test.log.step('3) On DUT open TCP Listener using SISO command')
        test.expect(test.tcp_listener.dstl_get_service().dstl_open_service_profile())
        dut_ip_address_and_port = test.tcp_listener.dstl_get_parser() \
            .dstl_get_service_local_address_and_port(ip_version=test.ip_version)
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

        test.log.step('4) On DUT check service state using AT^SISO? command')
        test.log.info("executed in previous step")

        test.log.step('5) On REM define TCP Client and send connection request to Listener')
        test.echo_server.dstl_run_ssh_nc_process(dut_ip_address, test.listener_port)

        test.log.step('6) On DUT wait for connection request and reject it using SISH command')
        test.expect(test.tcp_listener.dstl_get_urc().dstl_is_sis_urc_appeared("3"))
        test.sleep(3)
        test.expect(test.tcp_listener.dstl_get_service().dstl_disconnect_remote_client())

        test.log.step('7) On DUT check service state using AT^SISO? command')
        test.expect(test.tcp_listener.dstl_get_parser().dstl_get_service_state() ==
                                                                            ServiceState.UP.value)

        test.log.step('8) From REM send second connection request to Listener')
        test.echo_server.dstl_run_ssh_nc_process(dut_ip_address, test.listener_port)

        test.log.step('9) On DUT accept incoming connection using SISO command')
        test.expect(test.tcp_listener.dstl_get_urc().dstl_is_sis_urc_appeared("3"))
        test.expect(test.tcp_listener.dstl_get_service().dstl_open_service_profile())

        test.log.step('10) On DUT check service state using AT^SISO? command')
        test.expect(test.tcp_listener.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.CONNECTED.value)

        test.log.step('11) On DUT finish connection with Client using SISH command')
        test.expect(test.tcp_listener.dstl_get_service().dstl_disconnect_remote_client())
        test.sleep(3)

        test.log.step('12) On DUT check service state using AT^SISO? command')
        test.expect(test.tcp_listener.dstl_get_parser().dstl_get_service_state() ==
                                                                        ServiceState.UP.value)

    def cleanup(test):
        test.log.step('13) Close TCP Listener and Client profiles')
        test.expect(test.tcp_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(test.tcp_listener.dstl_get_service().dstl_reset_service_profile())
        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()