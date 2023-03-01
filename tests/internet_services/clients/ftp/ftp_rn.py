# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0071509.001, TC0071509.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Test FTP service in a real environment."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        srv_id_list = 0
        srv_id_put_get = 1
        test.file_name = "FtpRN.txt"
        test.second_file_name = "FileSoFolderIsNotEmpty"
        test.data_length = 1024
        test.data_packets = 100
        test.data = []

        test.log.step("1. Log in to the FTP server")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.log.info("creating a file, so folder is not empty, and list command does return SISR")
        test.expect(test.ftp_server.dstl_ftp_server_create_file(test.second_file_name, 10))

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.ftp_client_list = FtpProfile(test.dut, srv_id_list, test.connection_setup.dstl_get_used_cid(),
                                          command="list", ip_server=test.ftp_server, files=test.file_name, alphabet=1)
        test.ftp_client_list.dstl_set_parameters_from_ip_server()
        test.ftp_client_list.dstl_generate_address()
        test.expect(test.ftp_client_list.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client_list.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_list.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("2. Check the home directory on the server")
        test.expect(test.ftp_client_list.dstl_get_service().dstl_read_data(1500))
        test.expect((test.file_name not in test.dut.at1.last_response),
                    msg="{} file present, when it should not be".format(test.file_name))
        test.expect(test.ftp_client_list.dstl_get_service().dstl_close_service_profile())

        test.log.step("3. Upload a file of about 100 kBytes to the server")
        test.ftp_client_put_get_del = FtpProfile(test.dut, srv_id_put_get, test.connection_setup.dstl_get_used_cid(),
                                             command="put", ip_server=test.ftp_server, files=test.file_name, alphabet=1)
        test.ftp_client_put_get_del.dstl_set_parameters_from_ip_server()
        test.ftp_client_put_get_del.dstl_generate_address()
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_load_profile())

        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_put_get_del.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        for packet in range(test.data_packets):
            current_packet = dstl_generate_data(test.data_length)
            test.data.append(current_packet)
            test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_send_sisw_command(test.data_length))
            test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_send_data(current_packet))

        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_send_sisw_command(
            req_write_length="0", eod_flag="1"))
        test.expect(test.ftp_client_put_get_del.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client_put_get_del.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    test.data_length * test.data_packets)
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_close_service_profile())

        test.log.step("4. Check the directory on the server")
        test.expect(test.ftp_client_list.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_list.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.ftp_client_list.dstl_get_service().dstl_read_data(1500))
        test.expect((test.file_name in test.dut.at1.last_response),
                    msg="{} file not present, when it should be".format(test.file_name))
        test.expect(test.ftp_client_list.dstl_get_service().dstl_close_service_profile())

        test.log.step("5. Download the same file from the server")
        test.ftp_client_put_get_del.dstl_set_ftp_command("get")
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_write_cmd())
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_put_get_del.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        for packet in test.data:
            test.expect(packet in test.ftp_client_put_get_del.dstl_get_service().dstl_read_return_data(1024))

        test.expect(test.ftp_client_put_get_del.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                    test.data_length * test.data_packets)
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_close_service_profile())

        test.log.step("6. Delete the file on the server")
        test.ftp_client_put_get_del.dstl_set_ftp_command("del")
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_write_cmd())
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_put_get_del.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("7. Check the directory on the server")
        test.expect(test.ftp_client_list.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client_list.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.ftp_client_list.dstl_get_service().dstl_read_data(1500))
        test.expect((test.file_name not in test.dut.at1.last_response),
                    msg="{} file present, when it should not be".format(test.file_name))

        test.log.step("8. Log out from the server")
        test.log.info("Executed by closing the service profile")
        test.expect(test.ftp_client_put_get_del.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client_list.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Compare the uploaded and downloaded file")
        test.log.info("Executed in step 5")

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.info("Problem with removing {}".format(test.file_name))
            if not test.ftp_server.dstl_ftp_server_delete_file(test.second_file_name):
                test.log.info("Problem with removing {}".format(test.second_file_name))
            if not test.ftp_server.dstl_server_close_port():
                test.log.info("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)



if "__main__" == __name__:
    unicorn.main()
