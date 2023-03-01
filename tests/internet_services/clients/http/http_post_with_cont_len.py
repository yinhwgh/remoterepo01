# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0093319.001, TC0093319.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ TC intention: Check functionality of http post command with hcContLen parameter. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        """ Due to issue described in IPIS100310012, TC must be performed using an external HTTP server (e.g.
        httpbin.org) instead of IP server. Therefore, the HTTP server address has been hardcoded. """
        http_post_server = "http://www.httpbin.org/post"
        try:
            if test.http_post_server_address:
                test.log.info("Detected http_post_server_address parameter will be used: {}"
                              .format(test.http_post_server_address))
                http_post_server = test.http_post_server_address
        except AttributeError:
            test.log.info("http_post_server_address was not detected, therefore the default HTTP server will be "
                          "used: {}".format(http_post_server))

        test.log.step("1. Define PDP context for Internet services.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP POST profile to server with echo response (e.g http://www.httpbin.org/post).")
        test.srv_id = 0
        con_id = test.connection_setup.dstl_get_used_cid()
        test.http_profile = HttpProfile(test.dut, test.srv_id, con_id, address=http_post_server, http_command="post")
        test.expect(test.http_profile.dstl_get_service().dstl_load_profile())

        test.log.step("4. Set up hcContLen parameter to 150000 bytes.")
        data_amount = 150000
        test.http_profile.dstl_set_hc_cont_len(data_amount)
        test.expect(test.http_profile.dstl_get_service().dstl_write_hc_cont_len())

        test.log.step("5. Check current settings of all Internet service profiles.")
        dstl_check_siss_read_response(test.dut, [test.http_profile])

        test.log.step("6. Open HTTP profile.")
        test.expect(test.http_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                                              "\"POST Bytes: {}".format(data_amount)))
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("7. Check service state.")
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("8. Send 150000 bytes.")
        packet_size = 1500
        loops_number = int(data_amount / packet_size)
        for loop in range(loops_number):
            test.expect(test.http_profile.dstl_get_service().dstl_send_sisw_command_and_data(packet_size))
            test.sleep(1)
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sisw_urc_appeared(2))

        test.log.step("9. Read all data.")
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.expect(
            test.http_profile.dstl_get_service().dstl_read_return_data(packet_size, repetitions=loops_number + 1))
        test.expect(test.http_profile.dstl_get_urc().dstl_is_sisr_urc_appeared(2))

        test.log.step("10. Compare transmitted/received data.")
        test.expect("\"Content-Length\": \"{}\",".format(data_amount) in test.dut.at1.last_response)
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_data_counter("tx") == data_amount)
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_data_counter("rx") >= data_amount)

        test.log.step("11. Check service state.")
        test.expect(test.http_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

    def cleanup(test):
        test.log.step("12. Close HTTP POST service.")
        test.expect(test.http_profile.dstl_get_service().dstl_close_service_profile())


if __name__ == "__main__":
    unicorn.main()
