# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107992.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.ssl_server import SslServer


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior while basic connection to UDPS server

    Description:
    1) Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2) Define Non-transparent UDPS Client profile using SISS command (connection to UDPS Server)
    - set secopt parameter to 0
    3) Open UDPS client using SISO command
    4) Check service state using AT^SISO? command
    5) Close UDPS client using SISC command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.ssl_server = SslServer("IPv4", "dtls", "DHE-RSA-AES128-SHA")
        test.sleep(5)

    def run(test):
        test.log.info("TC0107992.001 UdpsSecureConnection_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) Define Non-transparent UDPS Client profile using SISS command '
                      '(connection to USPS Server)\r\n- set secopt parameter to 0')
        test.udps_client = SocketProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(),
                                          protocol="udp", secure_connection=True, secopt="0")
        test.udps_client.dstl_set_parameters_from_ip_server(test.ssl_server)
        test.udps_client.dstl_generate_address()
        test.expect(test.udps_client.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)

        test.log.step('3) Open UDPS client using SISO command')
        test.expect(test.udps_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('4) Check service state using AT^SISO? command')
        test.log.info("executed in previous step")
        test.sleep(3)

        test.log.step('5) Close UDPS client using SISC command')
        test.expect(test.udps_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.udps_client.dstl_get_service().dstl_close_service_profile()
        test.udps_client.dstl_get_service().dstl_reset_service_profile()
        try:
            test.ssl_server.dstl_server_close_port()
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()