# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094348.001

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
    """ To check FTP service profile (LIST)"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        srv_id_1 = 0
        test.file_name = "FileSoFolderIsNotEmpty"
        test.folder_name = "TestFolderName"
        test.file_size = 111
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.log.info("creating a folders and files")
        path = ""
        location_amount = 5

        test.ftp_client = FtpProfile(test.dut, srv_id_1,
                                     test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                     command="list", ip_server=test.ftp_server)
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()

        for location_number in range(location_amount):
            test.log.info("iteration {} out of 4".format(location_number))
            test.expect(test.ftp_server.dstl_ftp_server_create_directory(test.folder_name +
                                                                         str(location_number),
                        path="/{}".format(path)))
            test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name+
                                                                    str(location_number),
                                                                    test.file_size,
                                                                    path="/{}".
                                                                    format(path + test.folder_name +
                                                                           str(location_number))))


            test.log.step("I. Session define"
                          "1. Define FTP LIST service profile session using new FTP syntax "
                          '("user", "passwd" and "FtpPath" in separate fields)')

            test.ftp_client.dstl_set_ftpath("{}/".format(path + test.folder_name +
                                                         str(location_number)))
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("II. LIST session")
            test.open_profile_read_check_for_file(test.ftp_client)

            test.log.step('6. Repeat LIST session 5 times with different FtpPath')

            path += test.folder_name + str(location_number) + "/"

        test.log.step('III. Repeat steps II for "old" FTP syntax ("user", "passwd" '
                      'and "FtpPath" in address field)')
        path = ""
        test.ftp_client = FtpProfile(test.dut, srv_id_1,
                                     test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                     command="list", ip_server=test.ftp_server,
                                     are_concatenated=True, path_in_address=True)
        test.ftp_client.dstl_set_parameters_from_ip_server()
        for location_number in range(location_amount):

            test.ftp_client.dstl_set_ftpath("{}/".format(path + test.folder_name +
                                                         str(location_number)))
            test.ftp_client.dstl_generate_address()
            test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

            test.log.step("II. LIST session")
            test.open_profile_read_check_for_file(test.ftp_client)

            test.log.step('6. Repeat LIST session 5 times with different FtpPath')
            test.log.info("iteration {} out of 4".format(location_number))
            path += test.folder_name + str(location_number) + "/"


    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_directory(test.folder_name+"0"):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


    def open_profile_read_check_for_file(test, profile):
        test.log.step('1. Call at^siso for the defined profile (LIST session)')
        test.expect(profile.dstl_get_service().dstl_open_service_profile())

        test.log.step('2. Check for proper URC')
        test.expect(profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step('3. Check for presence of the already stored files')
        test.expect(profile.dstl_get_service().dstl_read_data(1500))
        test.expect((test.file_name in test.dut.at1.last_response),
                    msg="{} file not present".format(test.file_name))
        test.expect((str(test.file_size) not in test.dut.at1.last_response),
                    msg="{} file size present, when it should not be".format(test.file_name))

        test.log.step('4. Check Internet service state (AT^SISO?)')
        test.expect(profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step('5. Call at^sisc to close the service')
        test.expect(profile.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
