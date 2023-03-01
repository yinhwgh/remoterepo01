# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0094353.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
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
    """To check FTP service profile (APPEND)"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.info("Starting TS for TC0094353.001 ftpAPPEND")
        srv_id_1 = 1
        srv_id_2 = 2
        test.file_name = "TestFile"
        test.folder_name = "TestFolder"
        test.file_size = 666
        test.data_packet_size = 1000
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.log.info("creating a folders and files")
        location_amount = 5

        test.ftp_client_append = FtpProfile(test.dut, srv_id_1,
                                            test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                            command="append", ip_server=test.ftp_server)
        test.ftp_client_append.dstl_set_parameters_from_ip_server()
        test.ftp_client_append.dstl_generate_address()

        test.ftp_client_size = FtpProfile(test.dut, srv_id_2,
                                            test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                            command="size", ip_server=test.ftp_server)
        test.ftp_client_size.dstl_set_parameters_from_ip_server()
        test.ftp_client_size.dstl_generate_address()

        for location_number in range(location_amount):
            test.expect(test.ftp_server.dstl_ftp_server_create_directory(test.folder_name +
                                                                         str(location_number)))
            test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name +
                                                                    str(location_number),
                                                                    test.file_size,
                                                                    path="/{}".
                                                                    format(test.folder_name +
                                                                           str(location_number))))
            test.log.info("iteration {} out of 5".format(location_number + 1))
            test.log.step("I. Session define /r/n"
                          "1. Define FTP APPEND service profile session using new FTP syntax"
                          '("user", "passwd", "FtpPath" and "files" in separate fields)')
            test.ftp_client_append.dstl_set_ftpath("{}".format(test.folder_name +
                                                                str(location_number)))
            test.ftp_client_append.dstl_set_files("{}".format(test.file_name +
                                                                str(location_number)))
            test.expect(test.ftp_client_append.dstl_get_service().dstl_load_profile())

            test.log.step("I. Session define /r/n"
                          '2. Define FTP SIZE service session for same file that in APPEND session')
            test.ftp_client_size.dstl_set_ftpath("{}".format(test.folder_name +
                                                                str(location_number)))
            test.ftp_client_size.dstl_set_files("{}".format(test.file_name +
                                                              str(location_number)))
            test.expect(test.ftp_client_size.dstl_get_service().dstl_load_profile())
            dstl_check_siss_read_response(test.dut, [test.ftp_client_size, test.ftp_client_append])

            test.log.step("II. APPEND session")
            test.open_profile_read_check_for_file(test.ftp_client_size, False)
            test.open_profile_write_data(test.ftp_client_append)
            test.log.step('10. Check if file was correctly append using SIZE session '
                          '(check file size)')
            test.open_profile_read_check_for_file(test.ftp_client_size, after_append=True)

            test.log.step('III. Repeat APPEND session 5 times with different FtpPath and files/r/n')

        test.log.step('IV. Repeat step II-III for "old" FTP syntax ("user", "passwd", "FtpPath" '
                      'and "files" in address field) in FTP APPEND session')
        test.ftp_client_append = FtpProfile(test.dut, srv_id_1,
                                            test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                            command="append", ip_server=test.ftp_server,
                                            are_concatenated=True, path_in_address=True,
                                            files_in_address=True)
        test.ftp_client_append.dstl_set_parameters_from_ip_server()

        test.ftp_client_size = FtpProfile(test.dut, srv_id_2,
                                          test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                          command="size", ip_server=test.ftp_server,
                                          are_concatenated=True, path_in_address=True,
                                          files_in_address=True)
        test.ftp_client_size.dstl_set_parameters_from_ip_server()
        test.ftp_server.dstl_ftp_server_clean_up_directories()

        for location_number in range(location_amount):
            test.log.info("iteration {} out of 5".format(location_number + 1))
            test.expect(test.ftp_server.dstl_ftp_server_create_directory(test.folder_name +
                                                                         str(location_number)))
            test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name +
                                                                    str(location_number),
                                                                    test.file_size,
                                                                    path="/{}".
                                                                    format(test.folder_name +
                                                                           str(location_number))))

            test.ftp_client_append.dstl_set_ftpath("{}".format(test.folder_name +
                                                                str(location_number)))
            test.ftp_client_append.dstl_set_files("{}".format(test.file_name +
                                                              str(location_number)))
            test.ftp_client_append.dstl_generate_address()
            test.expect(test.ftp_client_append.dstl_get_service().dstl_load_profile())

            test.ftp_client_size.dstl_set_ftpath("{}".format(test.folder_name +
                                                             str(location_number)))
            test.ftp_client_size.dstl_set_files("{}".format(test.file_name + str(location_number)))
            test.ftp_client_size.dstl_generate_address()
            test.expect(test.ftp_client_size.dstl_get_service().dstl_load_profile())
            test.expect(dstl_get_siss_read_response(test.dut))

            test.log.step("II. APPEND session")
            test.open_profile_read_check_for_file(test.ftp_client_size, after_append=False)
            test.open_profile_write_data(test.ftp_client_append)
            test.log.step('10. Check if file was correctly append using SIZE session '
                          '(check file size)')
            test.open_profile_read_check_for_file(test.ftp_client_size, after_append=True)

            test.log.step('III. Repeat APPEND session 5 times with different FtpPath and files')

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_clean_up_directories():
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def open_profile_read_check_for_file(test, profile, after_append):
        test.log.step('1. Call at^siso for the defined profile (SIZE session) and check file size')
        test.expect(profile.dstl_get_service().dstl_open_service_profile())
        test.expect(profile.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect((test.file_name in test.dut.at1.last_response),
                    msg="{} file not present".format(test.file_name))
        if after_append:
            test.expect((str(test.file_size+3*test.data_packet_size) in test.dut.at1.last_response),
                        msg="{} incorrect file size".format(test.file_name))
        else:
            test.expect((str(test.file_size) in test.dut.at1.last_response),
                        msg="{} incorrect file size".format(test.file_name))

        test.log.step('2. Call at^sisc to close SIZE session service')
        test.expect(profile.dstl_get_service().dstl_close_service_profile())

    def open_profile_write_data(test, profile):
        test.log.step('3. Call at^siso for the defined profile (APPEND session)')
        test.expect(profile.dstl_get_service().dstl_open_service_profile())
        test.expect(profile.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step('4. Check the service profile (AT^SISO?)')
        test.expect(profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(profile.dstl_get_parser().dstl_get_socket_state() ==
                    ServiceState.ALLOCATED.value)

        test.log.step('5. Send some data')
        generated_packet = dstl_generate_data(test.data_packet_size)
        test.expect(profile.dstl_get_service().dstl_send_sisw_command_and_data(
                                                        test.data_packet_size, repetitions=2))
        test.log.step("6. Send some data with eodFlag")
        test.expect(profile.dstl_get_service().dstl_send_sisw_command(test.data_packet_size,
                                                                      eod_flag='1'))
        test.expect(profile.dstl_get_service().dstl_send_data(generated_packet))

        test.log.step("7. Check for proper URC")
        test.expect(profile.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step('8. Check the service profile (AT^SISO?)')
        test.expect(profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(profile.dstl_get_parser().dstl_get_socket_state() ==
                    ServiceState.ALLOCATED.value)

        test.log.step('9. Call at^sisc to close the service')
        test.expect(profile.dstl_get_service().dstl_close_service_profile())
        test.sleep(5)


if "__main__" == __name__:
    unicorn.main()
