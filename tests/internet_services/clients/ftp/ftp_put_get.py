# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094349.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention: To check FTP service profile (PUT, GET)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.file_name = "tps_put_get.txt"
        test.folder_name = "TestFolderName"

    def run(test):
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        used_cid = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, used_cid, extended=True)
        ftp_client = FtpProfile(test.dut, 0, used_cid, command="put", alphabet=1,
                                ip_server=test.ftp_server, files=test.file_name)
        ftp_client.dstl_set_parameters_from_ip_server()

        ftp_client_get = FtpProfile(test.dut, 1, used_cid, command="get", alphabet=1,
                                    ip_server=test.ftp_server, files=test.file_name)
        ftp_client_get.dstl_set_parameters_from_ip_server()

        for address_type in range(2):
            package_size = 1024
            path = ""
            location_amount = 5
            for location_number in range(location_amount):
                test.expect(test.ftp_server.dstl_ftp_server_create_directory(test.folder_name +
                                                                             str(location_number),
                                                                             path="/{}".format(
                                                                                 path)))
                test.log.step("I. Session define")
                test.log.step(
                    '1. Define FTP PUT service profile session using new FTP syntax ("user", '
                    '"passwd", "FtpPath" and "files" in separate fields)')
                ftp_client.dstl_set_ftpath(
                    "{}/".format(path + test.folder_name + str(location_number)))
                ftp_client.dstl_generate_address()
                test.expect(ftp_client.dstl_get_service().dstl_load_profile())

                test.log.step(
                    '2. Define FTP GET service profile session using new FTP syntax ("user", '
                    '"passwd", "FtpPath" and "files" in separate fields) for the same file '
                    'that in PUT session.')
                ftp_client_get.dstl_set_ftpath("{}/".format(path + test.folder_name +
                                                            str(location_number)))
                ftp_client_get.dstl_generate_address()
                test.expect(ftp_client_get.dstl_get_service().dstl_load_profile())

                test.log.step("II. PUT session")
                test.log.step("1. Call at^siso for the defined profile (PUT session)")
                test.expect(ftp_client.dstl_get_service().dstl_open_service_profile())

                test.log.step("2. Check the service profile (AT^SISO?)")
                test.expect(
                    ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
                    msg="Wrong service state")
                test.expect(
                    ftp_client.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value, msg="Wrong socket state")

                test.log.step("3. Send some data")
                test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(package_size))

                test.log.step("4. Send some data with eodFlag")
                test.expect(ftp_client.dstl_get_service().
                            dstl_send_sisw_command_and_data(package_size, eod_flag="1"))

                test.log.step("5. Check for proper URC")
                test.expect(ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

                test.log.step("6. Check Internet service state (AT^SISO?)")
                test.expect(
                    ftp_client.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value, msg="Wrong service state")
                test.expect(
                    ftp_client.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value, msg="Wrong socket state")
                test.expect(
                    ftp_client.dstl_get_parser().dstl_get_service_data_counter("tx") == 2*package_size)

                test.log.step("7. Call at^sisc to close the service")
                test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())

                test.log.step("III. GET session")
                test.log.step("1. Call at^siso for the defined profile (GET session)")
                test.expect(ftp_client_get.dstl_get_service().dstl_open_service_profile())

                test.log.step("2. Check the service profile (AT^SISO?)")
                test.expect(
                    ftp_client_get.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value,
                    msg="Wrong service state")
                test.expect(
                    ftp_client_get.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value, msg="Wrong socket state")

                test.log.step("3. Download some data")
                test.expect(ftp_client_get.dstl_get_service().dstl_read_return_data(package_size))

                test.log.step("4. Download rest of data till no more data is available.")
                test.expect(ftp_client_get.dstl_get_service().dstl_read_return_data(package_size))

                test.log.step("5. Check for proper URC")
                test.expect(ftp_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
                test.expect(
                    ftp_client_get.dstl_get_parser().dstl_get_service_data_counter("rx") == 2*package_size)

                test.log.step("6. Check Internet service state (AT^SISO?)")
                test.expect(
                    ftp_client_get.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value, msg="Wrong service state")
                test.expect(
                    ftp_client_get.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value, msg="Wrong socket state")

                test.log.step("7. Call at^sisc to close the service")
                test.expect(ftp_client_get.dstl_get_service().dstl_close_service_profile())

                path += test.folder_name + str(location_number) + "/"

                test.log.step("IV. Compare amount of transmitted and received data from "
                              "PUT and GET session")
                test.log.info("done in previous steps")

                test.log.step('V. Repeat steps from II to III 5 times for different "FtpPath"')
                test.log.info("Next path is: {}".format(path))

            test.log.step('VI. Repeat steps from I to V for "old" FTP syntax ("user", "passwd", '
                          '"FtpPath" and "files" in address field)')
            test.expect(ftp_client.dstl_get_service().dstl_reset_service_profile())
            test.expect(ftp_client_get.dstl_get_service().dstl_reset_service_profile())

            test.ftp_server.dstl_ftp_server_delete_directory(test.folder_name + "0")

            ftp_client.dstl_set_concatenated_credentials(True)
            ftp_client.dstl_set_files_in_address(True)
            ftp_client.dstl_set_path_in_address(True)

            ftp_client_get.dstl_set_concatenated_credentials(True)
            ftp_client_get.dstl_set_files_in_address(True)
            ftp_client_get.dstl_set_path_in_address(True)

    def cleanup(test):

        try:
            if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if __name__ == "__main__":
    unicorn.main()
