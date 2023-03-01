# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0093691.001, TC0093691.002, TC0012103.003, TC0012103.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_ot import dstl_set_scfg_tcp_ot
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_set_scfg_tcp_mr
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object


class Test(BaseTest):
    """Check functionality of Maximum Number of Retransmissions parameter."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):

        if test.ip_version == "IPv4":
            max_retransmission = 4
            test.log.h2("Executing script for:\n"
                        "TC0012103.003/TC0012103.004 HttpRetransmissionParam ")
        else:
            max_retransmission = 3
            test.log.h2("Executing script for:\n"
                        "TC0093691.001/TC0093691.002 - HttpRetransmissionParam_IPv6")
        overall_timeout = 6000
        timeout = 60
        test.http_server = HttpServer(test.ip_version, extended=True)
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        server_port = test.http_server.dstl_get_server_port()

        test.log.step("1. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version,
                                                            ip_public=True)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Set Global TCP/MR to {}.".format(max_retransmission))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, max_retransmission))

        test.log.step("4. Depends on Module set Global TCP/OT to in order to MR mechanism "
                      "takes effect: \n - maximum value \n - 0")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, overall_timeout))

        test.log.step("5. Define HTTP POST profile.")
        srv_id = "0"
        con_id = connection_setup.dstl_get_used_cid()
        test.http_client = HttpProfile(test.dut, srv_id, con_id, ip_version=test.ip_version,
                                       http_command="post", host=server_ip_address,
                                       port=server_port, alphabet=1, http_path="post")
        test.http_client.dstl_generate_address()
        test.expect(test.http_client.dstl_get_service().dstl_load_profile())

        test.log.step("6. Set up hcContLen to 1000 bytes.")
        test.http_client.dstl_set_hc_cont_len(1000)
        test.http_client.dstl_get_service().dstl_write_hc_cont_len()

        test.log.step("7. Check current settings of all Internet service profiles.")
        dstl_check_siss_read_response(test.dut, [test.http_client])

        test.log.step("8. Enable IP tracing (e.g. with Wireshark).")
        test.log.info("Will be done after closing port")

        test.log.step("9. Open HTTP profile.")
        test.expect(test.http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                                             '"Http connect.*'))

        test.log.step("10. Check service state.")
        test.expect(test.http_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)
        if test.ip_version == "IPv4":
            dut_ip_address = \
                test.http_client.dstl_get_parser().dstl_get_service_local_address_and_port(
                    'IPv4').split(':')[0]
        else:
            dut_ip_address = \
                test.http_client.dstl_get_parser().dstl_get_service_local_address_and_port(
                    "IPv6").split("[")[1].split("]:")[0].upper()

        test.log.step("11. Send 200 bytes of data.")
        test.expect(test.http_client.dstl_get_service().dstl_send_sisw_command_and_data(200))

        test.log.step("12. Activate firewall.")
        test.expect(test.http_server.dstl_server_block_incoming_traffic(dut_ip_address))
        test.tcpdump_thread = test.thread(test.http_server.dstl_server_execute_linux_command,
                                          "sudo timeout {0} tcpdump host {1} -A -i ens3".
                                          format(timeout, dut_ip_address), timeout=timeout)

        test.log.step("13. Send 500 bytes of data.")
        test.expect(test.http_client.dstl_get_service().dstl_send_sisw_command_and_data(500))

        test.log.step("14. Wait for Connection timed out URC.")
        test.expect(test.http_client.dstl_get_urc().dstl_is_sis_urc_appeared(
            "0", "20", "\"Connection timed out\"", timeout), msg="Expected URC not appeared.")

        test.log.step("15. Check service state.")
        test.expect(test.http_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("16. Close HTTP POST service..")
        test.expect(test.http_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("17. Stop IP tracing.")
        test.tcpdump_thread.join()
        test.expect(test.http_server.dstl_server_accept_incoming_traffic())

        test.log.step("18. Analize IP trace logs.")
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.http_server.linux_server_response)
        test.expect(test.http_server.linux_server_response.count("length 500") ==
                    (max_retransmission+1))     # original packet, and retransmissions

    def cleanup(test):
        try:
            test.tcpdump_thread.join()
        except AttributeError:
            test.log.error("Problem with tcpdump thread, possibly already closed")
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 10))


if "__main__" == __name__:
    unicorn.main()
