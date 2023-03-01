# responsible grzegorz.dziublinski@globallogic.com
# Wroclaw
# TC0094545.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """Check http get command."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.info("Executing script for test case: 'TC0094545.001 HttpGetBasic'")

        test.http_server = HttpServer("IPv4")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        server_port = test.http_server.dstl_get_server_port()

        test.log.step("1. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTTP web page.")
        srv_id = "0"
        con_id = connection_setup.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, srv_id, con_id, http_command="get", host=server_ip_address, port=server_port)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Check current settings of all Internet service profiles.")
        test.expect(test.dut.at1.send_and_verify('AT^SISS?'))
        test.expect('^SISS: {},"srvType","Http"'.format(srv_id) in test.dut.at1.last_response)
        test.expect('^SISS: {},"conId","{}"'.format(srv_id, con_id) in test.dut.at1.last_response)
        test.expect('^SISS: {},"address","http://{}:{}"'.format(srv_id, server_ip_address, server_port) in test.dut.at1.last_response)
        test.expect('^SISS: {},"cmd","get"'.format(srv_id) in test.dut.at1.last_response)
        for profile_id in range(1, 10):
            test.expect('^SISS: {},"srvType",""'.format(profile_id) in test.dut.at1.last_response)

        test.log.step("5. Open HTTP profile.")
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                    '"Http connect {}:{}"'.format(server_ip_address, server_port)))
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("6. Check service state.")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("7. Read all data.")
        read_data=http_client.dstl_get_service().dstl_read_all_data(1500)

        test.log.step("8. Check received URCs.")
        test.expect("SIS: {},0,48,\"Remote peer has closed the connection\"".format(srv_id)
                    in http_client.dstl_get_service().sisr_last_response)
        test.expect("SISR: {},2\r\n".format(srv_id) in http_client.dstl_get_service().sisr_last_response)

        test.log.step("9. Check service state.")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("10. Close HTTP GET service.")
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
