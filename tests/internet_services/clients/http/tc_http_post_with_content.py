#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093318.001, TC0093318.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ TC intention: Check functionality of http post command with hcContent parameter. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        """ Due to issue described in IPIS100310012, TC must be performed using an external HTTP
        server (e.g.httpbin.org) instead of IP server. Therefore, the HTTP server address has been
        hardcoded. """
        http_post_server = "http://www.httpbin.org/post"
        try:
            if test.http_post_server_address:
                test.log.info("Detected http_post_server_address parameter will be used: {}"
                              .format(test.http_post_server_address))
                http_post_server = test.http_post_server_address
        except AttributeError:
            test.log.info("http_post_server_address was not detected, therefore the default HTTP "
                          "server will be used: {}".format(http_post_server))

        test.log.step("1. Define PDP context for Internet services.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP POST profile to server with echo response "
                      "(e.g http://www.httpbin.org/post).")
        srv_id = 0
        con_id = test.connection_setup.dstl_get_used_cid()
        test.http_profile = HttpProfile(test.dut, srv_id, con_id, address=http_post_server,
                                        http_command="post")
        test.expect(test.http_profile.dstl_get_service().dstl_load_profile())

        hc_content_values = [255, 1, 265]

        for hc_content_value in hc_content_values:

            if hc_content_value == 1:
                test.log.step("A) Repeat points 4-11 with hcContent set to minimum data length.")
            elif hc_content_value == 265:
                test.log.step("B) Repeat points 4-11 with hcContent set to maximum data length"
                              " + 10 bytes.")

            test.log.step("4. Set up hcContent parameter with maximum data length.")
            hc_cont_len = '0'
            hc_content = dstl_generate_data(hc_content_value)
            test.http_profile.dstl_set_hc_content(hc_content)
            test.http_profile.dstl_set_hc_cont_len(hc_cont_len)
            test.expect(test.http_profile.dstl_get_service().dstl_write_hc_cont_len())
            if hc_content_value == 265:
                test.expect(test.dut.at1.send_and_verify('AT^SISS={},hccontent,"{}"'.format(srv_id,
                                                        hc_content), expect='.*ERROR.*'))
                break
            test.expect(test.http_profile.dstl_get_service().dstl_write_hc_content())

            test.log.step("5. Check current settings of all Internet service profiles.")
            dstl_check_siss_read_response(test.dut, [test.http_profile])

            test.log.step("6. Open HTTP profile.")
            test.expect(test.http_profile.dstl_get_service().dstl_open_service_profile())
            test.expect(test.http_profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                    '"POST Bytes: {}"'.format(len(hc_content))))
            test.expect(test.http_profile.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

            test.log.step("7. Check service state.")
            test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state()
                                                                    == ServiceState.UP.value)

            test.log.step("8. Read all data.")
            sisr_response = test.http_profile.dstl_get_service().dstl_read_return_data(1500)
            while test.http_profile.dstl_get_service().dstl_get_confirmed_read_length() > 0:
                sisr_response += test.http_profile.dstl_get_service().dstl_read_return_data(1500)

            test.log.step("9. Compare transmitted/received data.")
            test.expect('"Content-Length": "{}"'.format(len(hc_content)) in sisr_response)
            test.expect('"data": "{}"'.format(hc_content) in sisr_response)
            test.expect(test.http_profile.dstl_get_parser().dstl_get_service_data_counter("tx")
                                                                            == len(hc_content))

            test.log.step("10. Check service state.")
            test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state()
                                                                    == ServiceState.DOWN.value)

            test.log.step("11. Close HTTP POST service.")
            test.expect(test.http_profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.log.step("11. Close HTTP POST service.")
        test.expect(test.http_profile.dstl_get_service().dstl_close_service_profile())
        test.expect(test.http_profile.dstl_get_service().dstl_reset_service_profile())


if __name__ == "__main__":
    unicorn.main()