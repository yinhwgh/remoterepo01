# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0012061.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_ot \
                                                import dstl_set_scfg_tcp_ot, dstl_get_scfg_tcp_ot
from dstl.internet_service.configuration.scfg_tcp_mr import dstl_set_scfg_tcp_mr
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service \
                                                        import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from time import time


class Test(BaseTest):
    """Verify the overall timeout parameter for the FTP service."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.h2("Executing script for test case: 'TC0012061.001 FtpOverallTimeout'")
        overall_timeout_scfg = 30
        overall_timeout_siss = 60
        overall_timeout = overall_timeout_scfg
        test.ftp_server = FtpServer("IPv4", extended=True)

        test.log.step("1. Configure global value <tcpOT> (at^scfg) - if supported. Set <tcpMR> = 15.\n"
                      "If global setting is not supported, set those values in service profile.")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, overall_timeout_scfg))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 15))

        test.log.step("2. Activate PDP context (if needed). If product use connection profile, skip"
                      " this step.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Configure a FTP put service profile.")
        srv_id = "0"
        ftp_client = FtpProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(),
                                command="put", ip_server=test.ftp_server, files="test.txt")
        ftp_client.dstl_set_parameters_from_ip_server()
        ftp_client.dstl_generate_address()
        test.expect(ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Open the FTP service.")
        test.expect(ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        dut_ip_address = \
          ftp_client.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(':')[0]

        test.log.step("5. Send some data.")
        test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200))

        test.log.step("6. Block the IP traffic on server side.")
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_address))
        start_time = time()

        test.log.step("7. Call send command at^sisw in a loop.")
        for iteration in range(4):
            test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200,
                                                                            skip_data_check=True))
            test.sleep(5)

        test.log.step("8. Wait for Error URC or error of at^sisw.")
        if test.expect(ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                                "\"Connection timed out\"", 60), msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                                                    .format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < overall_timeout/2,
                                                msg="URC appeared, but not in expected time.")

        test.log.step("9. Close profile.")
        test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

        test.log.step("10. Configure the service based value <tcpOT>.")
        overall_timeout = overall_timeout_siss
        ftp_client.dstl_set_tcp_ot(overall_timeout)
        test.expect(ftp_client.dstl_get_service().dstl_write_tcpot())

        test.log.step("11. Repeat steps 4. - 9.")
        test.log.step("11.4. Open the FTP service.")
        test.expect(ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("11.5. Send some data.")
        test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200))

        test.log.step("11.6. Block the IP traffic on server side.")
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_address))
        start_time = time()

        test.log.step("11.7. Call send command at^sisw in a loop.")
        for iteration in range(8):
            test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(200,
                                                                            skip_data_check=True))
            test.sleep(5)

        test.log.step("11.8. Wait for Error URC or error of at^sisw.")
        if test.expect(ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                            "\"Connection timed out\"", 120), msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                                                        .format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < overall_timeout/2,
                                                    msg="URC appeared, but not in expected time.")

        test.log.step("11.9. Close profile.")
        test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("12. Try to set <tcpOT> to some illegal values and check the configured "
                      "values")
        test.expect(dstl_set_scfg_tcp_ot(test.dut, -2, expected=".*CME ERROR.*"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6001, expected=".*CME ERROR.*"))
        test.expect(dstl_set_scfg_tcp_ot(test.dut, "OT", expected=".*CME ERROR.*"))
        test.expect(int(dstl_get_scfg_tcp_ot(test.dut)) == overall_timeout_scfg)

    def cleanup(test):
        test.expect(dstl_set_scfg_tcp_ot(test.dut, 6000))
        test.expect(dstl_set_scfg_tcp_mr(test.dut, 10))
        try:
            test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())
            test.ftp_server.dstl_ftp_server_clean_up_directories()
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()