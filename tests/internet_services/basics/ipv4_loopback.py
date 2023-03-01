#responsible marek.kocela@globallogic.com
#Wroclaw
#TC TC0104804.001
import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs, dstl_get_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_loop import dstl_set_scfg_tcp_loop, dstl_get_scfg_tcp_loop
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Short description:
       To test ipv4 loopback support.

       Detailed description:
       1. Set IPv4 PDP context/connection profile
       2. Set "TCP/LOOP" parameter to "enabled".
       3. Create TCP listener service profile.
       4. Create TCP client service profile with "localhost" as address in address parameter.
       5. Open the listener.
       6. Open the client and send data.
       7. Receive data on listener.
       8. Close service profiles.
       9. Set address in TCP client to host outside of module (e.g. echo server)
       10. Open client.

       Author: marek.kocela@globallogic.com"""

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        data_50 = 50

        test.log.info("Executing script for test case: TC0104804.001 - IPv4Loopback")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer("IPv4", "TCP")

        test.log.step("1) Set IPv4 PDP context/connection profile")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Set \"TCP/LOOP\" parameter to \"enabled\"")
        test.expect(dstl_set_scfg_tcp_loop(test.dut, "enabled"))
        test.expect(dstl_get_scfg_tcp_loop(test.dut) == "enabled")

        test.log.step("3) Create TCP listener service profile.")
        test.local_listener = SocketProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(),
                                            host="listener", port=9999, protocol="tcp")
        test.local_listener.dstl_generate_address()
        test.expect(test.local_listener.dstl_get_service().dstl_load_profile())

        test.log.step("4) Create TCP client service profile with \"localhost\" as address in address parameter.")
        test.local_client = SocketProfile(test.dut, 1, connection_setup_object.dstl_get_used_cid(),
                                          host="localhost", port=9999, protocol="tcp")
        test.local_client.dstl_generate_address()
        test.expect(test.local_client.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open the listener.")
        test.expect(test.local_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.local_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5"))

        test.log.step("6) Open the client and send data.")
        test.expect(test.local_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.local_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.expect(test.local_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.local_client.dstl_get_service().dstl_send_sisw_command_and_data(data_50))

        test.log.step("7) Receive data on listener.")
        test.loopback = SocketProfile(test.dut, 2, connection_setup_object.dstl_get_used_cid())
        test.expect(test.loopback.dstl_get_service().dstl_open_service_profile())
        test.expect(test.loopback.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.loopback.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.loopback.dstl_get_service().dstl_read_data(data_50))

        test.log.step("8) Close service profiles.")
        test.expect(test.local_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(test.local_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.loopback.dstl_get_service().dstl_close_service_profile())

        test.log.step("9) Set address in TCP client to host outside of module (e.g. echo server)")
        test.outside_client = SocketProfile(test.dut, 3, connection_setup_object.dstl_get_used_cid(), protocol="tcp")
        test.outside_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.outside_client.dstl_generate_address()
        test.expect(test.outside_client.dstl_get_service().dstl_load_profile())

        test.log.step("10) Open client.")
        test.expect(test.outside_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.outside_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "122"))



    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.expect(test.local_listener.dstl_get_service().dstl_close_service_profile())
            test.expect(test.local_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.loopback.dstl_get_service().dstl_close_service_profile())
            test.expect(test.outside_client.dstl_get_service().dstl_close_service_profile())

            dstl_set_scfg_tcp_loop(test.dut, "disabled")

        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()