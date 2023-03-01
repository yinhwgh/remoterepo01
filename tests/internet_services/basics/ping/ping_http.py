#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0093527.001 TC0093527.002

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.info("TC0093527.002 - PingHttp")
        ping_request = 10

        test.log.step("1. Start module with SIM.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Define and activate PDP context.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Set HTTP service profile.")
        test.http_server = HttpServer("IPv4")
        test.http_service = HttpProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(), http_command="get")
        test.http_service.dstl_set_host(test.http_server.dstl_get_server_ip_address())
        test.http_service.dstl_set_port(test.http_server.dstl_get_server_port())
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_load_profile())

        test.log.step("4. Open HTTP service profile.")
        test.expect(test.http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_service.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                                        '"Http connect {}:{}"'.format
                                                                        (test.http_server.dstl_get_server_ip_address(),
                                                                         test.http_server.dstl_get_server_port())))
        test.expect(test.http_service.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("5. Start ping service.")
        ping_execution = InternetServiceExecution(test.dut, connection_setup_object.dstl_get_used_cid())
        test.expect(ping_execution.dstl_execute_ping(test.http_server.dstl_get_server_ip_address(),
                                                     request=ping_request, expected_response="Ping.*OK.*"))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= ping_request * 0.2)

        test.log.step("6. Read data from the HTTP server.")
        test.expect(test.http_service.dstl_get_service().dstl_read_all_data(1500))

        test.log.info("7. Ping again after data readout.")
        test.expect(ping_execution.dstl_execute_ping(test.http_server.dstl_get_server_ip_address(),
                                                     request=ping_request, expected_response="Ping.*OK.*"))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= ping_request * 0.2)

    def cleanup(test):
        test.log.step("8. Close HTTP service profile.")
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()