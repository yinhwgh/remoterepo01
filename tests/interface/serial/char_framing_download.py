#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0092103.002


import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.auxiliary.ip_server.http_otap_server import HttpOtapServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.serial_interface import config_character_framing
from dstl.internet_service.profile_storage import dstl_execute_sips_command

import random


class Test(BaseTest):
    """
        TC0092103.002 - Char.FramingDownLoad
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftp_file = "char_framing_download.txt"
        test.ftp_put_srv_id = 0
        test.ftp_get_srv_id = 1
        test.http_get_srv_id = 2
        test.ftp_file_size = 1024
        test.read_size = 1500
        test.http_file = '100KB'
        # (5,1) - 7E1, (5,0) - 7O1, (2,1) - 8E1, (3) - 8N1 - DEFAULT, (2,0) - 8O1, (1) - 8N2
        # Default value 3 need be excluded
        test.icf_list = ["5,1", "5,0", "2,1", "2,0", "1"]
        test.random_icf = random.choice(test.icf_list)
        test.default_at1 = test.dut.at1

    def run(test):
        test.log.step(f"1. Define FTP profile and HTTP profile, and upload file {test.ftp_file} to FTP server.")
        test.define_ftp_profile_and_upload_file()
        test.define_http_profile()

        test.log.step("2. Test downloading files with ASC0 and ASC1")
        for dut_interface in ['asc_0', 'asc_1']:
            test.dut.at1 = eval('test.dut.' + dut_interface)

            test.log.step(f"{dut_interface} 2.1. Download File from FTP server with get command. "
                          f"- Default ICF: 3 (8N1), dut interface {dut_interface}")
            test.dut.at1.send_and_verify("AT+ICF?", "ICF: 3")
            test.ftp_download_file()

            test.log.step(f"{dut_interface} 2.2. Download File from HTTP server with get command. "
                          f"- Default ICF: 3 (8N1), dut interface {dut_interface}")
            test.http_download_file()

            test.log.step(f"{dut_interface} 2.3. Download file from FTP server with another ICF.")
            test.log.step("2.3.a Setup random ICF.")
            test.expect(test.dut.dstl_execute_sips_command("all", "save"))
            test.expect(test.dut.dstl_configure_character_framing(char_frame=test.random_icf,
                                                                  store_settings=True,
                                                                  restart_after_set=True))
            test.expect(test.dut.at1.send_and_verify("AT+ICF?", f"ICF: {test.random_icf}"))
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
            test.expect(test.dut.dstl_execute_sips_command("all", "load"))

            test.log.step(f"2.3.b. Download file from FTP server with ICF {test.random_icf}")
            test.ftp_download_file()

            test.log.step(f"2.3.c. Download File from HTTP server with ICF {test.random_icf}")
            test.http_download_file()

            test.log.step("2.4 Restore ICF to default: 3")
            test.expect(test.dut.dstl_configure_character_framing(char_frame='3',
                                                                  store_settings=True,
                                                                  restart_after_set=True))
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
            test.expect(test.dut.dstl_execute_sips_command("all", "load"))


    def cleanup(test):
        if not test.dut.at1.send_and_verify("AT+ICF?", f"ICF: 3"):
            test.log.info("Restore ICF to default: 3")
            test.expect(test.dut.dstl_configure_character_framing(char_frame='3',
                                                              store_settings=True,
                                                              restart_after_set=True))
        else:
            try:
                test.http_client_get.dstl_get_service().dstl_close_service_profile()
                test.ftp_client_get.dstl_get_service().dstl_close_service_profile()
                test.ftp_client.dstl_get_service().dstl_close_service_profile()
                test.expect(test.dut.dstl_execute_sips_command("all", "reset"))
            except Exception:
                test.expect(test.dut.dstl_restart())
        test.dut.at1 = test.default_at1

    def define_ftp_profile_and_upload_file(test):
        test.log.info("***** Define the FTP session *****")
        test.log.info("***** a. Define ftp service session for PUT command *****")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.used_cid = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, test.used_cid)
        test.ftp_client = FtpProfile(test.dut, test.ftp_put_srv_id, test.used_cid, command="put", alphabet='1',
                                     ip_server=test.ftp_server, files=test.ftp_file, secopt="1",
                                     secure_connection=False)

        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.dut.at1.send_and_verify("AT^SISS?")

        test.log.info("***** b. Define ftp service session for GET command *****")
        test.ftp_client_get = FtpProfile(test.dut, test.ftp_get_srv_id, test.used_cid, command="get", alphabet='1',
                                         ip_server=test.ftp_server, files=test.ftp_file,
                                         secopt="1", secure_connection=False)

        test.ftp_client_get.dstl_set_parameters_from_ip_server()
        test.ftp_client_get.dstl_generate_address()
        test.expect(test.ftp_client_get.dstl_get_service().dstl_load_profile())
        test.dut.at1.send_and_verify("AT^SISS?")

        test.log.info("***** c. Save profile settings *****")
        test.expect(test.dut.dstl_execute_sips_command("all", "save"))

        test.log.info("***** e. Open ftp service for uploading file *****")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())

        test.log.info("***** f. Wait for proper URC *****")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.info("***** . Check Internet service state *****")
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
            msg="Wrong socket state")


        test.log.info(f"***** g. Upload file with size {test.ftp_file_size} to FTP server *****")
        test.expect(
            test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.ftp_file_size, eod_flag="1"))

        test.log.info("***** i. Close the defined service profile *****")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def ftp_download_file(test):
        # Redefine to init device_interface
        test.ftp_client_get = FtpProfile(test.dut, test.ftp_get_srv_id, test.used_cid, command="get", alphabet='1',
                                         ip_server=test.ftp_server, files=test.ftp_file,
                                         secopt="1", secure_connection=False)
        test.log.info("***** Open ftp service for downloading file *****")
        test.expect(test.ftp_client_get.dstl_get_service().dstl_open_service_profile())

        test.log.info("***** Wait for proper URC *****")
        test.expect(test.ftp_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.info(f"***** Download file with size {test.ftp_file_size} from FTP server *****")
        test.expect(test.ftp_client_get.dstl_get_service().dstl_read_return_data(test.read_size))
        test.expect(test.ftp_client_get.dstl_get_parser().dstl_get_service_data_counter("rx")
                    == test.ftp_file_size)

        test.log.info("***** Check Internet service state *****")
        test.expect(test.ftp_client_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(test.ftp_client_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.info("***** Close the defined service profile *****")
        test.expect(test.ftp_client_get.dstl_get_service().dstl_close_service_profile())

    def define_http_profile(test):
        test.log.info("***** Define HTTP profile for downloading file *****")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.expect(connection_setup.dstl_activate_internet_connection())
        test.used_cid = connection_setup.dstl_get_used_cid()
        test.http_server = HttpOtapServer("IPv4")
        test.http_server_ip_address = test.http_server.dstl_get_server_ip_address()
        test.http_server_port = test.http_server.dstl_get_server_port()
        test.http_client_get = HttpProfile(test.dut, test.http_get_srv_id, test.used_cid, http_command="get",
                                  host=test.http_server_ip_address, port=test.http_server_port)
        test.http_client_get.dstl_generate_address()
        test.expect(test.http_client_get.dstl_get_service().dstl_load_profile())

    def http_download_file(test):
        test.log.info("***** Set up address parameter to {} text file. *****".format(test.http_file))
        test.http_client_get.dstl_set_http_path(test.http_server.dstl_http_get_path_to_file(test.http_file))
        test.http_client_get.dstl_generate_address()
        test.expect(test.http_client_get.dstl_get_service().dstl_write_address())

        test.log.info("***** Check current settings of all Internet service profiles.")
        test.dut.at1.send_and_verify("AT^SISS?", "OK")

        test.log.info("***** Open HTTP profile. *****")
        test.expect(test.http_client_get.dstl_get_service().dstl_open_service_profile())
        test.expect(test.http_client_get.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                                             '"Http connect {}:{}"'.format(
                                                                                 test.http_server_ip_address,
                                                                                 test.http_server_port)))
        test.expect(test.http_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.info("***** Check service state. *****")
        test.expect(
            test.http_client_get.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.info("***** Read all data. *****")
        test.expect(test.http_client_get.dstl_get_service().dstl_read_all_data(1500))

        test.log.info("***** Check number of received bytes *****")
        test.expect(test.http_client_get.dstl_get_parser().dstl_get_service_data_counter(
            'rx') == 100 * 1024)

        test.log.info("***** Check service state. *****")
        test.expect(
            test.http_client_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.info("***** Close HTTP GET service. *****")
        test.expect(test.http_client_get.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
