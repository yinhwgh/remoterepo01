#responsible grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0093321.002, TC0093321.003

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_otap_server import HttpOtapServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response


class Test(BaseTest):
    """Check http get with different sizes (100 kB and 1 MB)."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.info("Executing script for test case: 'TC0093321.002/003 TcHttpGet'")

        test.log.step("1. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile.")
        test.http_server = HttpOtapServer("IPv4")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        server_port = test.http_server.dstl_get_server_port()
        test.http_client = HttpProfile(test.dut, '0', connection_setup.dstl_get_used_cid(), http_command="get",
                                       host=server_ip_address, port=server_port)
        test.http_client.dstl_generate_address()
        test.expect(test.http_client.dstl_get_service().dstl_load_profile())

        files_list = ['100kB', '1MB']
        for file in files_list:
            test.log.step("4. Set up address parameter to {} text file.".format(file))
            test.http_client.dstl_set_http_path(test.http_server.dstl_http_get_path_to_file(file))
            test.http_client.dstl_generate_address()
            test.expect(test.http_client.dstl_get_service().dstl_write_address())

            test.log.step("5. Check current settings of all Internet service profiles.")
            dstl_check_siss_read_response(test.dut, [test.http_client])

            test.log.step("6. Open HTTP profile.")
            test.expect(test.http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                    '"Http connect {}:{}"'.format(server_ip_address, server_port)))
            test.expect(test.http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

            test.log.step("7. Check service state.")
            test.expect(test.http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("8. Read all data.")
            test.expect(test.http_client.dstl_get_service().dstl_read_all_data(1500))

            test.log.step("9. Check number of received bytes")
            if file == '100kB':
                test.expect(test.http_client.dstl_get_parser().dstl_get_service_data_counter('rx') == 100*1024)
            else:
                test.expect(test.http_client.dstl_get_parser().dstl_get_service_data_counter('rx') == 1024*1024)

            test.log.step("10. Check service state.")
            test.expect(test.http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

            test.log.step("11. Close HTTP GET service.")
            test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())

            if file == '100kB':
                test.log.step("A) Repeat test for 1 MB text file.")

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
