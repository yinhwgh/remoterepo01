#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0092204.001, TC0092204.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """To test IPv6 Ping Service."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.h2("TC0092204.001 TpIpv6PingService'")

        test.http_server = HttpServer("IPv6")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        server_port = test.http_server.dstl_get_server_port()

        test.log.step("1. Start the module and register to network.")
        test.expect(dstl_register_to_network(test.dut), critical=True)

        test.log.step("2.  Create an IPv6 internet connection profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Set up an HTTP internet service profile and and download some data.")
        srv_id = "0"
        con_id = connection_setup.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, srv_id, con_id, ip_version="IPV6", http_command="get", host=server_ip_address,
                                  port=server_port, alphabet=1)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", '"Http connect.*'))
        check_ip_and_port = str.upper(http_client.dstl_get_urc().dstl_get_sis_urc_info_text())
        test.expect("[{}]:{}".format(str.upper(server_ip_address), str(server_port)) in check_ip_and_port)
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(http_client.dstl_get_service().dstl_read_data(200))
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("4. PING IPv6 address.")
        ping_execution = InternetServiceExecution(test.dut, connection_setup.dstl_get_used_cid())
        test.expect(ping_execution.dstl_execute_ping(server_ip_address, request=15))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= 15*0.2)
        test.expect(ping_execution.dstl_get_time_statistic()[2] > 0)

        test.log.step("5. Close the internet service.")
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()