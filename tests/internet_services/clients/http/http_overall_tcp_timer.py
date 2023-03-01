# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094512.001, TC0094514.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_set_scfg_tcp_mr
from dstl.internet_service.configuration.scfg_tcp_ot import dstl_set_scfg_tcp_ot
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from time import time
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """Check functionality of Overall TCP Timer for outstanding connection."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_register_to_network(test.dut), critical=True)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        test.log.info("Test is executed for IP version: {}".format(test.ip))
        overall_timeout = 90
        test.http_server = HttpServer(test.ip, extended=True)
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        server_port = test.http_server.dstl_get_server_port()

        test.log.step("1. Define PDP context for Internet services. ")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version=test.ip)
        test.expect(connection_setup.dstl_define_pdp_context())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Set up global tcp/MR to maximum value.")
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 30))

        test.log.step("4. Set up global tcp/OT to 90 seconds.")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 90))

        test.log.step("5. Define HTTP POST profile.")
        srv_id = "0"
        con_id = connection_setup.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, srv_id, con_id, ip_version=test.ip, http_command="post",
                                  host=server_ip_address,
                                  port=server_port, alphabet=1, http_path="post")
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())

        test.log.step("6. Set up hcContLen to 1000 bytes.")
        http_client.dstl_set_hc_cont_len(1000)
        http_client.dstl_get_service().dstl_write_hc_cont_len()

        test.log.step("7. Check current settings of all Internet service profiles")
        dstl_check_siss_read_response(test.dut, [http_client])

        test.log.step("8. Open HTTP profile.")
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(
            http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200", '"Http connect.*'))

        test.log.step("9. Check service state.")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("10. Send 200 bytes of data.")
        test.expect(http_client.dstl_get_service().dstl_send_sisw_command_and_data(200))

        test.log.step("11. Activate firewall.")
        test.expect(test.http_server.dstl_server_block_incoming_traffic())

        test.log.step("12. Send 500 bytes of data.")
        start_time = time()
        test.expect(http_client.dstl_get_service().dstl_send_sisw_command_and_data(500))
        test.sleep(5)

        test.log.step("13. Start time measurement.")
        test.log.info("Time measured by appropriate DSTL")

        test.log.step("14. Wait for Connection timed out URC.")
        if test.expect(http_client.dstl_get_urc().
                               dstl_is_sis_urc_appeared("0", "20", "\"Connection timed out\"", 190),
                       msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds.".
                          format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < 48,
                        msg="URC appeared, but not in expected time.")

        test.log.step("15. Check service state.")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step("16. Close HTTP POST service.")
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        try:
            test.expect(test.http_server.dstl_server_accept_incoming_traffic())
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6000))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))


if "__main__" == __name__:
    unicorn.main()
