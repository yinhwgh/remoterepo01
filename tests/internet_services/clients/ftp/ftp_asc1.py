# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0010959.001, TC0010959.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Verify correct behaviour of FTP via Asc1 (Second Serial Interface).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.file_name_asc0 = "FtpAsc0.txt"
        test.file_name_asc1 = "FtpAsc1.txt"
        test.data_length = 1500
        test.file_length = 6000
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_port = test.ftp_server.dstl_get_server_port()

    def run(test):
        test.log.h2("Executing script for test case: 'TC0010959.001/002 FtpAsc1'")

        test.log.step("1. Configure a GPRS connection profile / PDP context.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Set FTP PUT profile on ASC0.")
        test.define_ftp_profile("put", "FtpAsc0.txt", "at1")

        test.log.step("3. Send file to FTP server on ASC0.")
        test.send_file_to_ftp_server()

        test.log.step("4. Set FTP GET profile on ASC0.")
        test.define_ftp_profile("get", "FtpAsc0.txt", "at1")

        test.log.step("5. Download file from FTP server on ASC0.")
        test.download_file_from_ftp_server()

        test.log.step("6. Set FTP PUT profile on ASC1.")
        test.define_ftp_profile("put", "FtpAsc1.txt", "at2")

        test.log.step("7. Send file to FTP server on ASC1.")
        test.send_file_to_ftp_server()

        test.log.step("8. Set FTP GET profile on ASC1.")
        test.define_ftp_profile("get", "FtpAsc1.txt", "at2")

        test.log.step("9. Download file from FTP server on ASC1.")
        test.download_file_from_ftp_server()

    def cleanup(test):
            try:
                if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                    test.log.warn("Problem with cleaning directories.")
                if not test.ftp_server.dstl_server_close_port():
                    test.log.warn("Problem during closing port on server.")
            except AttributeError:
                test.log.error("Object was not created.")
            try:
                test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
                test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
            except AttributeError:
                test.log.error("Object was not created.")

    def define_ftp_profile(test, cmd, filename, interface):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1",
                                     host=test.ftp_ip_address,
                                     port=test.ftp_port, files=filename,
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd(),
                                     device_interface=interface)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

    def send_file_to_ftp_server(test):
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.data_length,  repetitions=3,
                                                    expected="OK"))
        test.expect(test.ftp_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.data_length, eod_flag="1"))
        test.sleep(3)
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(
            test.ftp_client.dstl_get_parser().
            dstl_get_service_data_counter("tx") == test.file_length)
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def download_file_from_ftp_server(test):
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(test.data_length,
                                                                      repetitions=4))
        test.sleep(3)
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().
                    dstl_get_service_data_counter("rx") == test.file_length)
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


if __name__ == "__main__":
    unicorn.main()
