#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0093727.001, TC0093727.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_get_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """To test HTTP with IPv6."""
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_scfg_tcp_with_urcs(test.dut, "on")
        dstl_enter_pin(test.dut)

    def run(test):
        test.log.step("	1. Define PDP context with PDP_type = IPv6 and activate it.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("2. Set up 3 HTTP service profiles (including get, post and head methods)")
        test.server = HttpServer("IPv6")
        test.profile = []
        for profile_id in range(3):
            test.profile.append(HttpProfile(test.dut, profile_id, test.connection_setup.dstl_get_used_cid(), alphabet="1"))
            test.profile[profile_id].dstl_set_parameters_from_ip_server(test.server)

            if profile_id == 0:
                test.profile[profile_id].dstl_set_http_command("get")
            elif profile_id == 1:
                test.profile[profile_id].dstl_set_http_command("head")
            else:
                test.profile[profile_id].dstl_set_http_command("post")
                test.profile[profile_id].dstl_set_hc_cont_len("0")
                test.profile[profile_id].dstl_set_hc_content("content")
                test.profile[profile_id].dstl_set_http_path("post")

            test.profile[profile_id].dstl_generate_address()
            test.expect(test.profile[profile_id].dstl_get_service().dstl_load_profile())

        test.log.step("3. Open all defined profiles.")

        for profile_id in range(3):
            test.expect(test.profile[profile_id].dstl_get_service().dstl_open_service_profile())
            test.expect(test.profile[profile_id].dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("4. Read some of received data for all services.")

        for profile_id in range(3):
            test.expect(test.profile[profile_id].dstl_get_service().dstl_read_data(10))

        test.log.step("5. Check status of services.")
        for profile_id in range(3):
            test.expect(test.profile[profile_id].dstl_get_parser().dstl_get_service_state() == 4)

        test.log.step("6. Close all HTTP service profiles. ")
        for profile_id in range(3):
            test.expect(test.profile[profile_id].dstl_get_service().dstl_close_service_profile())

        test.log.step("7. Check status of services.")

        for profile_id in range(3):
            test.expect(test.profile[profile_id].dstl_get_parser().dstl_get_service_state() == 2)

    def cleanup(test):
        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

        for profile_id in range(3):
            test.profile[profile_id].dstl_get_service().dstl_close_service_profile()

if "__main__" == __name__:
    unicorn.main()
