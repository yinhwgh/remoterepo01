# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0107071.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    Intention: To verify IPIS100325729 cOmega: FTP get service fail if file name contains space.

    I. Session define
        1. Define FTP PUT service profile session using new FTP syntax,file name must contains
        space,for example "Put test.txt". ("user", "passwd", "FtpPath" and "files" in separate
        fields)
        2. Define FTP GET service profile session using new FTP syntax ("user", "passwd",
        "FtpPath" and "files" in separate fields) for the same file that in PUT session.

    II. PUT session
        1. Call at^siso for the defined profile (PUT session)
        2. Check the service profile (AT^SISO?)
        3. Send some data
        4. Send some data with eodFlag
        5. Check for proper URC
        6. Check Internet service state (AT^SISO?)
        7. Call at^sisc to close the service

    III. GET session
        1. Call at^siso for the defined profile (GET session)
        2. Check the service profile (AT^SISO?)
        3. Download some data
        4. Download rest of data ll no more data is available.
        5. Check for proper URC
        6. Check Internet service state (AT^SISO?)
        7. Call at^sisc to close the service

    IV. Compare amount of transmitted and received data from PUT and GET session

    V. Repeat steps from II to III 5 times for different "FtpPath"

    VI. Repeat steps from I to V for "old" FTP syntax ("user", "passwd", "FtpPath" and "files"
     in address field)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.used_cid = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, test.used_cid, extended=True)
        test.files = [{'folder': "folder", "file": "test file.txt", "data_part1": 1000,
                       "data_part2": 1000},
                      {'folder': "folder2", "file": "te 12 fi 32 .txt", "data_part1": 823,
                       "data_part2": 1200},
                      {'folder': "veylongnamefolderwithoutspaces", "file": "test file.t x t",
                       "data_part1": 530, "data_part2": 140},
                      {'folder': "dr", "file": "te st fi le.log", "data_part1": 700,
                       "data_part2": 1500},
                      {'folder': "folde_r", "file": "t e s t f i l e . t x t", "data_part1": 10,
                       "data_part2": 15}]

    def run(test):
        test.ftp_put_client = FtpProfile(test.dut, 0, test.used_cid, command="put", alphabet=1,
                                         ip_server=test.ftp_server, files="")
        test.ftp_put_client.dstl_set_parameters_from_ip_server()

        test.ftp_get_client = FtpProfile(test.dut, 1, test.used_cid, command="get", alphabet=1,
                                         ip_server=test.ftp_server, files="")
        test.ftp_get_client.dstl_set_parameters_from_ip_server()

        for syntax in [False, True]:
            for path_dict in test.files:
                if syntax:
                    test.log.step('VI. Repeat steps from I to V for "old" FTP syntax ("user", '
                                  '"passwd", "FtpPath" and "files" in address field)')
                test.setup_internet_profile(path_dict["folder"], path_dict["file"], syntax)
                test.check_put_get(path_dict["data_part1"], path_dict["data_part2"])

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        try:
            test.expect(test.ftp_put_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftp_put_client.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.ftp_get_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftp_get_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")

    def setup_internet_profile(test, folder_name, file_name, old_syntax):
        if old_syntax:
            syntax = "old"
            syntax_description = '("user", "passwd", "FtpPath" and "files" in address field)'
        else:
            syntax = "new"
            syntax_description = '("user", "passwd", "FtpPath" and "files" in separate fields)'

        test.log.step("I. Session define")

        folder_name += syntax
        test.expect(test.ftp_server.dstl_ftp_server_create_directory(folder_name))

        for session in [test.ftp_get_client, test.ftp_put_client]:
            session.dstl_set_path_in_address(old_syntax)
            session.dstl_set_concatenated_credentials(old_syntax)
            session.dstl_set_files_in_address(old_syntax)

        test.log.step('1. Define FTP PUT service profile session using {} FTP syntax, file name '
                      'must contains space, for example "Put test.txt". {}'.format
                      (syntax, syntax_description))
        test.ftp_put_client.dstl_set_ftpath("{}/".format(folder_name))
        test.ftp_put_client.dstl_set_files(file_name)
        test.ftp_put_client.dstl_generate_address()
        test.expect(test.ftp_put_client.dstl_get_service().dstl_load_profile())

        test.log.step('2. Define FTP GET service profile session using {} "FTP syntax" {} for the '
                      'same file that in PUT session.'.format(syntax, syntax_description))
        test.ftp_get_client.dstl_set_ftpath("{}/".format(folder_name))
        test.ftp_get_client.dstl_set_files(file_name)
        test.ftp_get_client.dstl_generate_address()
        test.expect(test.ftp_get_client.dstl_get_service().dstl_load_profile())

    def check_put_get(test, len_data_part1, len_data_part2):
        test.log.step("II. PUT session")
        test.log.step("1. Call at^siso for the defined profile (PUT session)")
        test.expect(test.ftp_put_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("2. Check the service profile (AT^SISO?)")
        test.expect(
            test.ftp_put_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
            msg="Wrong service state")
        test.expect(
            test.ftp_put_client.dstl_get_parser().dstl_get_socket_state() ==
            SocketState.CLIENT.value, msg="Wrong socket state")

        test.log.step("3. Send some data")
        test.expect(test.ftp_put_client.dstl_get_service().dstl_send_sisw_command_and_data(
            len_data_part1))

        test.log.step("4. Send some data with eodFlag")
        test.expect(test.ftp_put_client.dstl_get_service().dstl_send_sisw_command_and_data(
            len_data_part2, eod_flag="1"))

        test.log.step("5. Check for proper URC")
        test.expect(test.ftp_put_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("6. Check Internet service state (AT^SISO?)")
        test.expect(
            test.ftp_put_client.dstl_get_parser().dstl_get_service_state() ==
            ServiceState.DOWN.value, msg="Wrong service state")
        test.expect(
            test.ftp_put_client.dstl_get_parser().dstl_get_socket_state() ==
            SocketState.CLIENT.value, msg="Wrong socket state")
        sent_amount_of_data = \
            test.ftp_put_client.dstl_get_parser().dstl_get_service_data_counter("tx")

        test.log.step("7. Call at^sisc to close the service")
        test.expect(test.ftp_put_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("III. GET session")
        test.log.step("1. Call at^siso for the defined profile (GET session)")
        test.expect(test.ftp_get_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("2. Check the service profile (AT^SISO?)")
        test.expect(
            test.ftp_get_client.dstl_get_parser().dstl_get_service_state() ==
            ServiceState.UP.value,
            msg="Wrong service state")
        test.expect(
            test.ftp_get_client.dstl_get_parser().dstl_get_socket_state() ==
            SocketState.CLIENT.value, msg="Wrong socket state")

        test.log.step("3. Download some data")
        test.expect(test.ftp_get_client.dstl_get_service().dstl_read_return_data(len_data_part2))

        test.log.step("4. Download rest of data till no more data is available.")
        test.expect(test.ftp_get_client.dstl_get_service().dstl_read_all_data(len_data_part1))

        test.log.step("5. Check for proper URC")
        test.log.info("Checked in the previous step")

        test.log.step("6. Check Internet service state (AT^SISO?)")
        test.expect(
            test.ftp_get_client.dstl_get_parser().dstl_get_service_state() ==
            ServiceState.DOWN.value, msg="Wrong service state")
        test.expect(
            test.ftp_get_client.dstl_get_parser().dstl_get_socket_state() ==
            SocketState.CLIENT.value, msg="Wrong socket state")
        received_amount_of_data = \
            test.ftp_get_client.dstl_get_parser().dstl_get_service_data_counter("rx")

        test.log.step("7. Call at^sisc to close the service")
        test.expect(test.ftp_get_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("IV. Compare amount of transmitted and received data from "
                      "PUT and GET session")
        test.expect(sent_amount_of_data == received_amount_of_data, msg="Comparing received and "
                                                                        "sent data")


if __name__ == "__main__":
    unicorn.main()
