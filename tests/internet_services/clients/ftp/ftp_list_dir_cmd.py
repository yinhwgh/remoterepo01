# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0093312.001, TC0093312.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Test FTP directory listing using parameter 'cmd' set to: DIR and LIST."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        srv_id_1 = 0
        srv_id_2 = 1
        test.file_name = "FileSoFolderIsNotEmpty"
        test.folder_name = "TestFolderName"
        wrong_folder = "WrongFolderName"
        test.file_size = 111

        test.ftp_server = FtpServer("IPv4", extended=True)
        test.log.info("creating a file, so folder is not empty, and list command does return SISR")
        test.expect(test.ftp_server.dstl_ftp_server_create_directory(test.folder_name))
        test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name, test.file_size,
                                                                path="/{}".format(test.folder_name)))

        test.log.step("Configure the mandatory FTP parameters."
                      "Define FTP path, try to open and read list of files in cases as described below:")
        test.log.step("1. Use valid path to directory - add path to parameter 'address'")
        test.log.step('a. Set "cmd" parameter to "list" (without showing file size)')

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.ftp_client = FtpProfile(test.dut, srv_id_1, test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                     command="list", ip_server=test.ftp_server,  path_in_address=True,
                                     ftpath="{}/".format(test.folder_name))
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.open_profile_read_check_for_file(test.ftp_client)

        test.log.step('b. Set "cmd" parameter to "dir" (with shown file size)')
        test.ftp_client.dstl_set_ftp_command("dir")
        test.expect(test.ftp_client.dstl_get_service().dstl_write_cmd())

        test.open_profile_read_check_for_file(test.ftp_client, size_in_data=True)

        test.log.step("2. Use valid path to directory - path define with parameter 'ftPath'")
        test.log.step('a. Set "cmd" parameter to "list" (without showing file size)')
        test.ftp_client_second = FtpProfile(test.dut, srv_id_2, test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                            command="list", ip_server=test.ftp_server, ftpath=test.folder_name)
        test.ftp_client_second.dstl_set_parameters_from_ip_server()
        test.ftp_client_second.dstl_generate_address()
        test.expect(test.ftp_client_second.dstl_get_service().dstl_load_profile())

        test.open_profile_read_check_for_file(test.ftp_client_second)

        test.log.step('b. Set "cmd" parameter to "dir" (with shown file size)')

        test.ftp_client_second.dstl_set_ftp_command("dir")
        test.expect(test.ftp_client_second.dstl_get_service().dstl_write_cmd())

        test.open_profile_read_check_for_file(test.ftp_client_second, size_in_data=True)

        test.log.step('3. Use path to not existing directory - use path added to parameter "address"')
        test.ftp_client.dstl_set_ftpath("{}/".format(wrong_folder))
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "100",
                                                                            '"ERR: 550 WrongFolderName: No such '
                                                                            'file or directory"'))

        test.log.step('4. Use path to not existing directory - use path from parameter "ftPath"')
        test.ftp_client_second.dstl_set_ftpath(wrong_folder)
        test.expect(test.ftp_client_second.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client_second.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.ftp_client_second.dstl_get_urc().dstl_is_sis_urc_appeared("0", "100",
                                                                                   '"ERR: 550 WrongFolderName: No such '
                                                                                   'file or directory"'))

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name, path="/{}".format(test.folder_name))\
                    or not test.ftp_server.dstl_ftp_server_delete_directory(test.folder_name):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


    def open_profile_read_check_for_file(test, profile, size_in_data=False):
        test.expect(profile.dstl_get_service().dstl_open_service_profile())
        test.expect(profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.expect(profile.dstl_get_service().dstl_read_data(1500))
        test.expect((test.file_name in test.dut.at1.last_response),
                    msg="{} file not present".format(test.file_name))
        if not size_in_data:
            test.expect((str(test.file_size) not in test.dut.at1.last_response),
                        msg="{} file size present, when it should not be".format(test.file_name))
        else:
            test.expect((str(test.file_size) in test.dut.at1.last_response),
                        msg="{} file size not present, when it should be".format(test.file_name))

        test.expect(profile.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
