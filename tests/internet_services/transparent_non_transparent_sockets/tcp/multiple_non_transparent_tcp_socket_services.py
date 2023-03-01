# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0092152.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Intention: To test Multiple Non-Transparent TCP socket Services.

       Description:
         1. Start the module registers the module to the network.
         2. Create (activate) an internet connection profile or PDP context.
         3. Set up maximum number of non-transparent TCP client profiles (connection to echoserver).
         4. Open all the TCP profiles.
         5. Close all the TCP profiles."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut))
        test.ip_server_tcp = EchoServer("IPv4", "TCP")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):

        test.log.step("1. Start the module registers the module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Create (activate) an internet connection profile or PDP context.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Set up maximum number of non-transparent TCP client profiles (connection to echoserver).")
        socket_dut = []
        for srv_id in range(0, 10):
            socket_dut.append(SocketProfile(test.dut, srv_id, connection_setup_dut.dstl_get_used_cid(),
                                                protocol="tcp", ip_server=test.ip_server_tcp))
            socket_dut[srv_id].dstl_set_parameters_from_ip_server()
            socket_dut[srv_id].dstl_generate_address()
            test.expect(socket_dut[srv_id].dstl_get_service().dstl_load_profile())

        test.log.step("4. Open all the TCP profiles.")
        for profile in socket_dut:
            test.expect(profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("5. Close all the TCP profiles.")
        for profile in socket_dut:
            test.expect(profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        try:
            test.ip_server_tcp.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
