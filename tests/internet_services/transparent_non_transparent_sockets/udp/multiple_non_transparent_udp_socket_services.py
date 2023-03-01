#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0092153.001, TC0092153.004

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """ TC intention: To test Multiple Non-Transparent UDP socket Services """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.udp_server = EchoServer("IPV4", "UDP")

    def run(test):
        test.log.info("Execution of script for TC0092153.001/004 - Multiple Non-Transparent UDP socket Services")

        test.log.step("1. Start the module registers the module to the network.")
        test.log.info("This will be done together with the next step.")

        test.log.step("2. Create an internet connection profile by at^sics=0, conType, GPRS0.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Set up an internet service profile and the steps as below:")
        test.sockets = []
        test.sockets.append(test.define_non_transparent_udp_client(test, 0))
        test.expect(test.sockets[0].dstl_get_service().dstl_open_service_profile())
        test.expect(test.sockets[0].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Try to set up another 9 internet service profiles which id is from 1 to 9.")
        for i in range(1, 10):
            test.sockets.append(test.define_non_transparent_udp_client(test, i))
            test.expect(test.sockets[i].dstl_get_service().dstl_open_service_profile())
            test.expect(test.sockets[i].dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("5. Close all the internet services.")
        for i in range(len(test.sockets)):
            test.expect(test.sockets[i].dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.udp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    @staticmethod
    def define_non_transparent_udp_client(test, srv_id):
        socket = SocketProfile(test.dut, srv_id, test.connection_setup.dstl_get_used_cid(), protocol="udp",
                                        host=test.udp_server.dstl_get_server_ip_address(),
                                        port=test.udp_server.dstl_get_server_port())
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket


if "__main__" == __name__:
    unicorn.main()
