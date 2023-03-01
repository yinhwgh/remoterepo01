# responsible dominik.tanderys@globallogic.com
# Wroclaw
# TC0012057.001, TC0012057.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_compare_internet_service_profiles import \
    dstl_compare_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_ot import dstl_set_scfg_tcp_ot
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_set_scfg_tcp_mr, \
    dstl_get_scfg_tcp_mr
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """Verify the maximum retransmission parameter."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.h2("Executing script for test case: TC0012057.001/002 - FtpMaxRetransmissions")
        max_retransmissions = ['7', '4', '31', 'illegal']
        overall_timeout = 6000
        timeout = 190
        timeout_2 = 46
        test.ftp_server = FtpServer("IPv4", extended=True)

        test.log.step("1. Set Global TCP/MR parameter using AT^SCFG command. Depends on Module "
                      "set Global TCP/OT to (in order to MR mechanism takes effect): \r\n- "
                      "maximum value \r\n- 0.")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, overall_timeout))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, max_retransmissions[0]))
        test.execute_steps_2_to_12(timeout=timeout, max_retransmissions=max_retransmissions[0])

        test.log.step("13. Repeat steps 2. - 12 with different <tcpMR> values.")
        test.execute_steps_2_to_12(timeout=timeout_2, max_retransmissions=max_retransmissions[1])

        test.log.step("14. Try to set <tcpMR> to illegal values and check the configured ones "
                      "(global and service base value)")
        test.expect(not dstl_set_scfg_tcp_mr(test.dut, max_retransmissions[2]))
        test.expect(not dstl_set_scfg_tcp_mr(test.dut, max_retransmissions[3]))
        test.expect(dstl_get_scfg_tcp_mr(test.dut) == max_retransmissions[0])

        test.ftp_client.dstl_set_tcp_mr(max_retransmissions[2])
        test.expect(not test.ftp_client.dstl_get_service().dstl_write_tcpmr())
        test.ftp_client.dstl_set_tcp_mr(max_retransmissions[3])
        test.expect(not test.ftp_client.dstl_get_service().dstl_write_tcpmr())
        test.ftp_client.dstl_set_tcp_mr(max_retransmissions[1])

        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               test.defined_profiles_list)

    def execute_steps_2_to_12(test, timeout, max_retransmissions, tcpmr=False):
        srv_id = "0"
        test.log.step("2. Enable IP trace.")
        test.log.info("Will be done after closing port")

        test.log.step("3. Activate PDP context (if needed)")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4. Configure a FTP service profile")
        test.ftp_client = FtpProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(),
                                command="put",
                                ip_server=test.ftp_server, files="test.txt")
        test.ftp_client.dstl_set_parameters_from_ip_server()
        if tcpmr:
            test.ftp_client.dstl_set_tcp_mr(max_retransmissions)
        test.ftp_client.dstl_generate_address()

        test.log.step("5. Open the FTP profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.defined_profiles_list = dstl_get_siss_read_response(test.dut)
        dut_ip_address = test.ftp_client.dstl_get_parser() \
            .dstl_get_service_local_address_and_port('IPv4').split(':')[0]

        test.log.step("6. Send some data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200))

        test.log.step("7. Block the IP traffic by a firewall "
                      "(on FTP server side) or use a shield box.")
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_address))
        test.tcpdump_thread = test.thread(test.ftp_server.dstl_server_execute_linux_command,
                                              "sudo timeout {0} tcpdump host {1} -A -i ens3".
                                             format(timeout, dut_ip_address), timeout=timeout)

        test.log.step("8. Call the write at^sisw command once and try to send data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200,
                                                                            skip_data_check=True))

        test.log.step("9. Wait for Error URC that indicates network problems.")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                                                                            '"Connection timed '
                                                                            'out"',
                                                                            timeout),
                    msg="Expected URC not appeared.")

        test.log.step("10. Close profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

        test.log.step("11. Check the number of retransmissions by analysing the IP trace.")
        test.tcpdump_thread.join()
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.ftp_server.linux_server_response)
        test.expect(test.ftp_server.linux_server_response.count("length 200") ==
                    int(max_retransmissions)+1)  # original packet, and retransmissions

        test.log.step("12. Configure the service based value <tcpMR>.")
        test.ftp_client.dstl_set_tcp_mr(max_retransmissions)
        test.ftp_client.dstl_get_service().dstl_write_tcpmr()

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6000))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 10))
        try:
            test.tcpdump_thread.join()
        except AttributeError:
            test.log.error("Problem with tcpdump thread, possibly already closed")
        try:
            test.ftp_server.dstl_server_accept_incoming_traffic()
            test.ftp_server.dstl_ftp_server_clean_up_directories()
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
