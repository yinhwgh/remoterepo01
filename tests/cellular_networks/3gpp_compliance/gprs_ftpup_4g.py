#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095893.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import network_monitor
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import SocketState
from dstl.internet_service.profile_storage import dstl_execute_sips_command

class Test(BaseTest):
    '''
    TC0095893.001 - GPRS_ftpup_4G
    Intention: ftp transfer upload
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.ftp_file = "gprs_ftpup_4g.txt"
        test.ftp_put_srv_id = 0
        test.ftp_file_size = 1024

    def run(test):
        test.log.step("1. Register module to 4G network.")
        test.dut.dstl_register_to_lte()
        test.expect(test.dut.dstl_monitor_network_act()=='4G', msg="Module is not in 4G mode.",
                    critical=True)

        test.log.step("2. Define the FTP profile")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.used_cid = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, test.used_cid)
        test.ftp_client = FtpProfile(test.dut, test.ftp_put_srv_id, test.used_cid, command="dir",
                                     alphabet='1',
                                     ip_server=test.ftp_server, files=test.ftp_file, secopt="1",
                                     secure_connection=False)

        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.dut.at1.send_and_verify("AT^SISS?")

        test.log.step("3. Delete file if it exists in FTP server before uploading.")
        if test.file_exists_in_ftp():
            test.expect(test.delete_file_from_ftp())
            test.expect(not test.file_exists_in_ftp(), msg="Fail to delete file from FTP server.")

        test.log.step("4. Upload file to FTP server.")
        test.ftp_client.dstl_set_ftp_command("put")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(
            test.ftp_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
            msg="Wrong socket state")
        test.expect(
            test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.ftp_file_size,
                                                                               eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("5. File was uploaded and exists in FTP server.")
        test.expect(test.file_exists_in_ftp(), msg=f"File {test.ftp_file} was not uploaded to FTP.")


    def cleanup(test):
        try:
            test.expect(test.delete_file_from_ftp())
            test.expect(test.dut.dstl_execute_sips_command("all", "reset"))
            test.dut.at1.send_and_verify("AT+COPS=2")
            test.dut.at1.send_and_verify("AT+COPS=0")
        except Exception:
            test.expect(test.dut.dstl_restart())

    def file_exists_in_ftp(test):
        test.ftp_client.dstl_get_service().dstl_close_service_profile()
        test.ftp_client.dstl_set_ftp_command("dir")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("\d")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(1500))
        file_exists = test.ftp_file in test.dut.at1.last_response
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.sleep(1)
        return file_exists

    def delete_file_from_ftp(test):
        test.ftp_client.dstl_get_service().dstl_close_service_profile()
        test.ftp_client.dstl_set_ftp_command("del")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        deleted = test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                '"250 DELE command successful"')
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.sleep(1)
        return deleted


if "__main__" == __name__:
    unicorn.main()