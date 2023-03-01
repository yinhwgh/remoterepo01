# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0094347.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    To check FTP service profile (SIZE)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.srv_id = "0"
        test.file_name = "TestFile"
        test.folder_name = "TestFolder"
        test.file_size = 100
        test.ftp_server = FtpServer("IPv4", extended=True)
        path = ""
        location_amount = 5

        test.ftp_client = FtpProfile(test.dut, test.srv_id,
                                     test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                     command="size", ip_server=test.ftp_server)
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()

        for location_number in range(location_amount):
            test.log.info("Iteration {} out of 4".format(location_number))
            test.log.info("Creating a folders and files")
            directory = test.folder_name + str(location_number)
            test.expect(test.ftp_server.dstl_ftp_server_create_directory(directory,
                                                                         path="/" + path))
            test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name +
                                                                    str(location_number),
                                                                    test.file_size,
                                                                    path="/" + path + directory))

            test.log.step("I. Session define "
                          "1. Define FTP SIZE service profile session using new FTP syntax "
                          '("user", "passwd", "FtpPath" and "files" in separate fields)')

            test.ftp_client.dstl_set_ftpath(path + directory + "/")
            test.ftp_client.dstl_set_files(test.file_name + str(location_number))
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("II. SIZE session")
            test.open_profile_read_check_for_file()

            test.log.step('5. Repeat SIZE session 5 times with different FtpPath and files')

            path += directory + "/"

        test.log.step('III. Repeat steps II for "old" FTP syntax ("user", "passwd" '
                      '"FtpPath" and "files" in address field)')
        path = ""
        test.ftp_client.dstl_set_path_in_address(path_in_address=True)
        test.ftp_client.dstl_set_concatenated_credentials(are_concatenated=True)
        test.ftp_client.dstl_set_files_in_address(files_in_address=True)
        test.ftp_client.dstl_set_parameters_from_ip_server()
        for location_number in range(location_amount):
            directory = test.folder_name + str(location_number)
            test.ftp_client.dstl_set_ftpath(path + directory + "/")
            test.ftp_client.dstl_set_files(test.file_name + str(location_number))
            test.ftp_client.dstl_generate_address()
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("II. SIZE session")
            test.open_profile_read_check_for_file()

            test.log.step('5. Repeat SIZE session 5 times with different FtpPath and files')
            test.log.info("iteration {} out of 4".format(location_number))
            path += directory + "/"

    def cleanup(test):
        try:

            if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, profile_id=test.srv_id, force_reset=True)

    def open_profile_read_check_for_file(test):
        test.log.step('1. Call at^siso for the defined profile (SIZE session)')
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('2. Check for proper URC and displayed file size')
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect((test.file_name in test.dut.at1.last_response),
                    msg="{} file present".format(test.file_name))
        test.expect((str(test.file_size) in test.dut.at1.last_response),
                    msg="{} file size present".format(test.file_name))

        test.log.step('3. Check Internet service state (AT^SISO?)')
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step('4. Call at^sisc to close the service')
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()