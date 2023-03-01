#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0093693.001, TC0093693.002

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
    """ TC0093693.001, TC0093693.002 - PingWithHttpService_IPv6
    Execute ping in IPv6 and check how it's functioning during active http connection.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):
        test.log.info("Start TC0093693.001 / TC0093693.002 - PingWithHttpService_IPv6")
        test.log.step("1) Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) For modules with AT^SICA support: Define IPv6 or dual stack PDP context and activate it.\r"
                      "For modules with AT^SICS support: Define IPv6 or dual stack connection profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        connection_setup.cgdcont_parameters['cid'] = '2'
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3) Define HTTP service profile (if PDP context is working as dualstack then define ipVer).")
        test.http_server = HttpServer("IPv6")
        test.http_service = HttpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), http_command="get", alphabet=1)
        test.http_service.dstl_set_parameters_from_ip_server(ip_server=test.http_server)
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open defined HTTP profile.")
        ip_server_address = test.http_server.dstl_get_server_ip_address()
        test.expect(test.http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_service.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", '"Http connect [{}]:{}"'.
                    format(ip_server_address.upper(), test.http_server.dstl_get_server_port())))
        test.expect(test.http_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("5) Try to open defined profile again.")
        test.expect(test.http_service.dstl_get_service().dstl_open_service_profile(".*ERROR.*"))

        test.log.step("6) Execute ping command with [request]=30 and [timelimit]=6000 with IPv6 address format "
                      "to chosen service (eg. website based on IPv6).")
        requests = 30
        time_limit = 6000
        ping_execution = InternetServiceExecution(test.dut, cid)
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.2)

        test.log.step("7) Read some data on HTTP service.")
        test.expect(test.http_service.dstl_get_service().dstl_read_data(1500))

        test.log.step("8) Execute ping command with [request]=30 and [timelimit]=6000 with IPv6 address format "
                      "to chosen service (eg. website based on IPv6).")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.2)

        test.log.step("9) Close the HTTP service.")
        test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Execute ping command with [request]=30 and [timelimit]=6000 with IPv6 address format "
                      "to chosen service (eg. website based on IPv6).")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=requests, timelimit=time_limit))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.2)

        test.log.step("11) Check service state.")
        test.expect(test.http_service.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

        test.log.step("12) Only for modules with AT^SICA support: Deactivate PDP context.")
        test.expect(connection_setup.dstl_deactivate_internet_connection())

        test.log.step("13) Only for modules with AT^SICA support: Check the state of PDP context.")
        test.log.info("This Step was executed in previous step")

        test.log.step("14) Only for modules with AT^SICA support: Try to execute ping command with IPv6 address format "
                      "to chosen service.")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=requests, timelimit=time_limit,
                                                     expected_response=".*ERROR.*"))

    def cleanup(test):
        test.http_service.dstl_get_service().dstl_close_service_profile()
        test.http_service.dstl_get_service().dstl_reset_service_profile()
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
