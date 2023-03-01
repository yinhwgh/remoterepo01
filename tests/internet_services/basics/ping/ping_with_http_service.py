# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0024342.003

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """
    Execute ping and check how it's functioning during active http connetion
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):
        test.log.step("1) Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Define PDP context/connection profile and activate it if needed.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3) Define HTTP service profile.")
        test.http_server = HttpServer("IPv4")
        http_service = HttpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), http_command="get")
        http_service.dstl_set_host(test.http_server.dstl_get_server_ip_address())
        http_service.dstl_set_port(test.http_server.dstl_get_server_port())
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open defined HTTP profile.")
        test.expect(http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(http_service.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", '"Http connect {}:{}"'.
                                                                   format(test.http_server.dstl_get_server_ip_address(),
                                                                            test.http_server.dstl_get_server_port())))
        test.expect(http_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("5) Try to open defined profile again.")
        test.expect(http_service.dstl_get_service().dstl_open_service_profile(".*ERROR.*"))

        test.log.step("6) Execute ping command with maximum available values to chosen service (eg. website).")
        requests = 30
        time_limit = 10000
        ping_execution = InternetServiceExecution(test.dut, cid)
        test.expect(ping_execution.dstl_execute_ping(test.http_server.dstl_get_server_ip_address(),
                                                     request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.3)

        test.log.step("7) Read some data on HTTP service.")
        test.expect(http_service.dstl_get_service().dstl_read_data(1500))

        test.log.step("8) Execute ping command with maximum available values to chosen service (eg. website).")
        test.expect(ping_execution.dstl_execute_ping(test.http_server.dstl_get_server_ip_address(),
                                                     request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.3)

        test.log.step("9) Close the HTTP service.")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Execute ping command with maximum available values to chosen service (eg. website).")
        test.expect(ping_execution.dstl_execute_ping(test.http_server.dstl_get_server_FQDN(),
                                                     request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.3)

        test.log.step("11) Check service state.")
        test.expect(http_service.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

    def cleanup(test):
        try:
            test.http_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
