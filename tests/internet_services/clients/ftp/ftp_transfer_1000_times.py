#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0085686.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: This test checks long time stability of the FTP service.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.ftp_server = FtpServer("IPv4", extended=True, test_duration=30)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file_name = "FtpTransfer1000Times.txt"

    def run(test):
        loops = 1000
        data_length = 1500
        test.log.step("1. Depends on product:\n- Set Connection Profile (GPRS)\n- Define and activate PDP Context.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile(), critical=True)
        test.cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Enable URC mode for Internet Service commands.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        for loop in range(loops):
            test.log.step("Starting {} out of {} loops\r\n3. Configure a FTP \"put\" session.".format(loop+1, loops))
            test.define_and_print_ftp_profile("put")

            test.log.step("4. Open the service profile and wait for \"^SISW:\" URC.")
            test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
            if not test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100", ".*FTP server ready.*"):
                test.log.info("The FTP server is not reachable, TC will be terminated.")
                break

            test.log.step("5. Send some data to the service.")
            test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
            test.expect(len(test.ftp_server.dstl_ftp_server_get_file(test.file_name)) == data_length)

            test.log.step("6. Close the service profile.")
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("7. Configure a FTP \"get\" session. In address field enter the path to the file that you"
                          " created earlier.")
            test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
            test.define_and_print_ftp_profile("get", files_in_address=True)

            test.log.step("8. Open the service profile and wait for \"^SISR:\" URC.")
            test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
            if not test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1")):
                test.log.info("The service profile has not been opened correctly. This loop will be skipped.")
                test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
                continue

            test.log.step("9. Read all data from file on the FTP server and wait for \"^SISW: <id>,2\"")
            test.expect(len(test.ftp_client.dstl_get_service().dstl_read_return_data(data_length)) == data_length)
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("10. Close the service profile.")
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("11. Configure a FTP \"delete\" session. In address field enter the path to the file that you"
                          " created earlier.")
            test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
            test.define_and_print_ftp_profile("delete", files_in_address=True)

            test.log.step("12. Open the service profile and wait until srvState changes to DOWN.")
            test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                                "\"250 DELE command successful\""))
            if not test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2")):
                test.log.info("The service profile has not been opened correctly. This loop will be skipped.")
                test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

            test.log.step("13. Close the service profile.")
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("14. Configure a FTP \"get\" session. In address field enter the path to the file you "
                          "previously removed.")
            test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
            test.define_and_print_ftp_profile("get", files_in_address=True)

            test.log.step("15. Open the service profile and wait for URC indicates that there is no such file.")
            test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "100",
                                                                                ".*No such file or directory.*"))
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

            test.log.step("16. Close the service profile.\r\nEnding {} out of {} loops".format(loop + 1, loops))
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

            if loop != loops-1:
                test.log.step("Repeat Testcase (steps 3-16) 999 times.")

    def cleanup(test):
        try:
            if not test.expect(test.ftp_server.dstl_server_close_port()):
                test.log.warn("Problem during closing port on server.")
            if not test.expect(test.ftp_server.dstl_ftp_server_clean_up_directories()):
                test.log.warn("Problem with cleaning directories.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def define_and_print_ftp_profile(test, cmd, files_in_address=False):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1", host=test.ftp_ip_address,
                                     port=test.ftp_port, files=test.file_name,
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        if files_in_address:
            test.ftp_client.dstl_set_files_in_address(True)
        test.ftp_client.dstl_generate_address()
        if files_in_address:
            test.ftp_client._model.files = None
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))


if __name__ == "__main__":
    unicorn.main()
