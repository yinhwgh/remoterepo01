#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0093652.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        test.log.info("TC0093652.001 - PingBeforeHttpReady")

        test.log.step("1) Log on to the network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Define and activate PDP context")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Set HTTP service profile")
        address = "absolute-redirect/5"
        test.http_server = HttpServer("IPv4")
        test.srv_id = '0'
        http_service = HttpProfile(test.dut, test.srv_id, connection_setup_object.dstl_get_used_cid(), http_command="get")
        http_service.dstl_set_host(test.http_server.dstl_get_server_ip_address())
        http_service.dstl_set_port(test.http_server.dstl_get_server_port())
        http_service.dstl_set_http_path(address)
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open service profile and start ping FQDN address before service is ready")
        ping_execution = InternetServiceExecution(test.dut, connection_setup_object.dstl_get_used_cid())
        server_fqdn_address = test.http_server.dstl_get_server_FQDN()
        test.expect(http_service.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("4.1) Start ping & 4.2) Wait for ^SISR: x,1 after ping execution")
        test.expect(ping_execution.dstl_execute_ping(server_fqdn_address, request=10,
                                                     expected_response="Ping.*OK.*SISR: {},1".format(test.srv_id),
                                                     check_packet_statistics=False))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= 10 * 0.2)

        test.log.step("5) Close service profile.")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())

        test.log.info("6) Re-register to the network")
        test.expect(test.dut.at1.send_and_verify('at+cops=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cops=0', 'OK'))
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        test.log.step("7) Open service profile and start ping IP address before service is ready")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        test.expect(http_service.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("7.1) Start ping & 7.2) Wait for ^SISR: x,1 after ping execution")
        test.expect(ping_execution.dstl_execute_ping(server_ip_address, request=10,
                                                     expected_response="Ping.*OK.*SISR: {},1".format(test.srv_id),
                                                     check_packet_statistics=False))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= 10 * 0.2)

        test.log.step("8) Close service profile.")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(dstl_reset_internet_service_profiles(test.dut, profile_id=test.srv_id, force_reset=True))


if "__main__" == __name__:
    unicorn.main()
