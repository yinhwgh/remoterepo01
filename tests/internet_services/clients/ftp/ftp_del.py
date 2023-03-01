# responsible: michalhabrych@globallogic.com
# location: Wroclaw
# TC0094352.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.network_service.register_to_network import dstl_enter_pin
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
    """ To check FTP service profile (DELETE)"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")


    def run(test):
        test.filetable = ['File1.txt', 'File2.txt', 'File_123456789.txt',
                          'File#123.bin', 'File-111.bin', 'Secondfile.txt']
        test.foldertable = ['Folder1', 'Folder_2', 'Folder-3', 'Folder1/Test01',
                            'Folder1/Test_02']
        test.file_size = 100
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.location_amount = 5
        test.file_name2 = test.filetable[5]

        for location_number in range(test.location_amount):
            test.file_name = test.filetable[location_number]
            test.folder_name = test.foldertable[location_number]
            test.log.info("iteration {} out of 4".format(location_number))
            test.log.info("creating a folders and files")
            test.create_directory_and_file_on_server()

            test.log.step("I. Session define"
                          "1. Define FTP DEL service profile session using new FTP syntax "
                          '("user", "passwd" and "FtpPath" in separate fields)')
            test.ftp_client = FtpProfile(test.dut, 0,
                                         test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                         command="del", ip_server=test.ftp_server,
                                         ftpath=test.folder_name, files=test.file_name)
            test.ftp_client.dstl_set_parameters_from_ip_server()
            test.ftp_client.dstl_generate_address()
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("2. Define FTP LIST or FTP DIR profile.")
            test.create_list_profile()

            test.log.step("II. DELETE session")
            test.open_profile_del_file(test.ftp_client)

            test.log.step('5. Repeat DEL session 5 times with different FtpPath and files')
            test.log.step('6. Check if file were correctly deleted using LIST or DIR session')
            test.open_profile_check_file(test.ftp_client2)

        test.log.step('III. Repeat steps II for "old" FTP syntax ("user", "passwd" '
                      'and "FtpPath" in address field)')
        for location_number in range(test.location_amount):
            test.file_name = test.filetable[location_number]
            test.folder_name = test.foldertable[location_number]
            test.log.info("iteration {} out of 4".format(location_number))
            test.log.info("creating a folders and files")
            test.create_directory_and_file_on_server()

            test.log.info("I. Session define"
                          "1. Define FTP DEL service profile session using old FTP syntax")
            test.ftp_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                        alphabet=1, command="del", ip_server=test.ftp_server,
                                        are_concatenated=True, path_in_address=True,
                                        files_in_address=True, ftpath=test.folder_name,
                                        files=test.file_name)
            test.ftp_client.dstl_set_parameters_from_ip_server()
            test.ftp_client.dstl_generate_address()
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("2. Define FTP LIST or FTP DIR profile.")
            test.create_list_profile()

            test.log.step("II. DELETE session")
            test.open_profile_del_file(test.ftp_client)

            test.log.step('5. Repeat DIR session 5 times with different FtpPath')
            test.log.step('6. Check if file were correctly deleted using LIST or DIR session')
            test.open_profile_check_file(test.ftp_client2)


    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        for location_number in range(test.location_amount):
            test.folder_name = test.foldertable[location_number]
            try:
                if not test.ftp_server.dstl_ftp_server_delete_directory(test.folder_name):
                    test.log.warn("Problem with cleaning directories.")
            except AttributeError:
                test.log.error("Object was not created.")


    def create_directory_and_file_on_server(test):
        path = ""
        test.ftp_server.dstl_ftp_server_create_directory(test.folder_name)
        test.ftp_server.dstl_ftp_server_create_file(test.file_name, test.file_size,
                                                    path="/{}".format(path + test.folder_name))
        test.ftp_server.dstl_ftp_server_create_file(test.file_name2, test.file_size,
                                                    path="/{}".format(path + test.folder_name))


    def create_list_profile(test):
        test.ftp_client2 = FtpProfile(test.dut, 9,
                                      test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                      command="list", ip_server=test.ftp_server,
                                      ftpath=test.folder_name, files=test.file_name)
        test.ftp_client2.dstl_set_parameters_from_ip_server()
        test.ftp_client2.dstl_generate_address()
        test.expect(test.ftp_client2.dstl_get_service().dstl_load_profile())


    def open_profile_del_file(test, profile):
        test.log.step('1. Call at^siso for the defined profile (LIST session)')
        test.log.step('2. Check for proper URC')
        test.expect(profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                            "\"250 DELE command successful\""))

        test.log.step('3. Check Internet service state (AT^SISO?)')
        test.expect(profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step('4. Call at^sisc to close the service')
        test.expect(profile.dstl_get_service().dstl_close_service_profile())


    def open_profile_check_file(test, profile):
        test.expect(profile.dstl_get_service().dstl_open_service_profile())
        test.expect(profile.dstl_get_service().dstl_read_data(1500))
        test.expect(test.file_name not in test.dut.at1.last_response)

        test.expect(profile.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()