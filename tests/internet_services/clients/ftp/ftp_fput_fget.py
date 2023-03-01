#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0105125.002, TC0105125.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.miscellaneous import access_ffs_by_at_command


class Test(BaseTest):
    """
    To check fput and fget parameters using local flash-file system during FTP session.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.file_name = "test.txt"
        test.directory = "a:/test/"
        test.file_data = 'abcde'
        test.file_path = test.directory + test.file_name
        test.access_file_flag_create_read_write = '10'
        test.expect(dstl_register_to_network(test.dut))
        test.log.info('0. Some txt files on local flash-file system are available on DUT')
        test.expect(test.dut.dstl_create_directory(test.directory))
        test.file_handler = test.dut.dstl_open_file(test.file_path, test.access_file_flag_create_read_write)
        test.expect(test.dut.dstl_write_file(test.file_handler, size=len(test.file_data), data=test.file_data))
        test.expect(test.dut.dstl_close_file(test.file_handler))
        test.expect(test.dut.dstl_list_directory(path=test.directory))

    def run(test):
        test.log.step("1. Define the FTP fput profile (using one or more files from DUT flash-file system)")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv4")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, cid)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_fqdn_address = test.ftp_server.dstl_get_server_FQDN()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.ftp_fput = FtpProfile(test.dut, 0, cid, command="fput", alphabet="1", host=test.ftp_ip_address,
                                   port=test.ftp_port, local_path=test.directory, files=test.file_name,
                                   user=test.ftp_server.dstl_get_ftp_server_user(),
                                   passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_fput.dstl_generate_address()
        test.expect(test.ftp_fput.dstl_get_service().dstl_load_profile())
        dstl_check_siss_read_response(test.dut, [test.ftp_fput])

        test.log.step("2. Open the defined profile")
        test.expect(test.ftp_fput.dstl_get_service().dstl_open_service_profile())

        test.log.step("3. Check for proper URC")
        test.expect(test.ftp_fput.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("4. Check Internet service state")
        test.expect(test.ftp_fput.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("5. Close the defined service profile")
        test.expect(test.ftp_fput.dstl_get_service().dstl_close_service_profile())

        test.log.step("6. Check on FTP server if created files are the same like on DUT flash-file system")
        if test.expect(test.ftp_server.dstl_ftp_server_get_file(test.file_name) == test.file_data):
            test.log.info("The same file with correct content from DUT flash-file is on FTP server")

        test.log.step("7. Delete uploaded files from DUT flash-file system")
        test.expect(test.dut.dstl_clear_directory(test.directory))

        test.log.step("8. Define FTP fget profile (using one or more file names from FTP server)")
        test.ftp_fget = FtpProfile(test.dut, 0, cid, command="fget", alphabet="1", host=test.ftp_ip_address,
                                   port=test.ftp_port, local_path=test.directory, files=test.file_name,
                                   user=test.ftp_server.dstl_get_ftp_server_user(),
                                   passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_fget.dstl_generate_address()
        test.expect(test.ftp_fget.dstl_get_service().dstl_load_profile())
        dstl_check_siss_read_response(test.dut, [test.ftp_fget])

        test.log.step("9. Repeat steps 2-5")
        test.log.step("2. Open the defined profile")
        test.expect(test.ftp_fget.dstl_get_service().dstl_open_service_profile())

        test.log.step("3. Check for proper URC")
        test.expect(test.ftp_fget.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("4. Check Internet service state")
        test.expect(test.ftp_fget.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("5. Close the defined service profile")
        test.expect(test.ftp_fget.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Check on DUT flash-file system if downloaded files are the same like on FTP server")
        test.dut.dstl_open_file(test.file_path, test.access_file_flag_create_read_write)
        file_from_server_data = test.expect(test.dut.dstl_read_file(test.file_handler, size=len(test.file_data)))
        if test.expect(test.ftp_server.dstl_ftp_server_get_file(test.file_name) == file_from_server_data):
            test.log.info("The same file with correct content from FTP server are on DUT flash-file")

    def cleanup(test):
        test.log.step("11. Delete files from DUT flash-file system and FTP server")
        test.expect(test.dut.dstl_close_file(test.file_handler))
        test.expect(test.dut.dstl_clear_directory(test.directory))
        test.expect(test.dut.dstl_remove_directory(test.directory))
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
