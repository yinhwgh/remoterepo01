#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0024338.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """	Execute ping and socket but use explicitly open/close connection profile."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_imei(test.dut)


    def run(test):
        test.log.info("TC0024338.002 PingSocketServiceWithExplicitOpen")

        test.log.step("1. Prepare internet connections and pdp contexts.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv4")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Activate URC messages. ")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("3. Set socket TCP or UDP client on DUT and connect to echo server.")
        test.echo_server = EchoServer("IPv4", "TCP")
        client_profile = SocketProfile(test.dut, 1, cid, protocol="TCP")
        client_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(client_profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.expect(client_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("4. On second interface start pinging echo server from DUT.")
        ping_execution = InternetServiceExecution(test.dut.at2, connection_setup.dstl_get_used_cid())
        server_ip_address = test.echo_server.dstl_get_server_ip_address()
        test.ping = test.thread(ping_execution.dstl_execute_ping, server_ip_address,
                                request=30, expected_response=".*Ping.*")
        test.ping.join()
        test.sleep(2)

        test.log.step("5. Close socket connection and on second interface still ping echo server from DUT.")
        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())
        test.expect(test.dut.at2.wait_for(".*2,{},30,[1-30].*".format(cid), timeout=60))

        test.log.step("6. Close all services.")
        test.log.info("Done in previous step")

        test.log.step("7. Check service state.")
        test.expect(client_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
