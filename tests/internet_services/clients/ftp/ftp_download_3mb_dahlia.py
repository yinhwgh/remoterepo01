#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0010960.002

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
    Intention:
    Verify FTP behaviour under load

    Description:
    1. Activate PDP context for internet services
    2. Define FTP client put service
    3. Upload a 3Mb file (2000 x 1500 bytes) to server
    4. Close FTP client profile
    5. Define FTP client get service
    6. Download the same file (2000 x 1500 bytes) from server
    7. Close FTP client profile
    8. Delete this text file on the server (use "del" profile)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.ftp_server = FtpServer("IPv4", extended=True, test_duration=4)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file_name = "FTP3M.txt"
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        send_loops = 1999
        receive_loops = send_loops + 1
        data_length = 1500
        file_length = 3000000

        test.log.info("TC0010960.002 - FTPDownload3Mb_Dahlia")
        test.log.step("1. Activate PDP context for internet services")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Define FTP client put service")
        test.define_and_print_ftp_profile("put")

        test.log.step("3. Upload a 3Mb file (2000 x 1500 bytes) to server")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length,
                                                                    repetitions=send_loops, expected="OK"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") == file_length)

        test.log.step("4. Close FTP client profile")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("5. Define FTP client get service")
        test.define_and_print_ftp_profile("get")

        test.log.step("6. Download the same file (2000 x 1500 bytes) from server")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_length, repetitions=receive_loops))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_data_counter("rx") == file_length)

        test.log.step("7. Close FTP client profile")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("8. Delete this text file on the server (use ""del"" profile)")
        test.define_and_print_ftp_profile("del")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                            "\"250 DELE command successful\""))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        try:
            if not test.expect(test.ftp_server.dstl_server_close_port()):
                test.log.warn("Problem during closing port on server.")
            if not test.expect(test.ftp_server.dstl_ftp_server_clean_up_directories()):
                test.log.warn("Problem with cleaning directories.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def define_and_print_ftp_profile(test, cmd):
        test.ftp_client = FtpProfile(test.dut, 0, test.cid, command=cmd, alphabet="1", host=test.ftp_ip_address,
                                     port=test.ftp_port, files=test.file_name,
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))

if __name__ == "__main__":
    unicorn.main()