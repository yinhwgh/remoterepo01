#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0010952.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    TC intention: Check if the FTP port number parameter is handled correctly.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.file = "test"
        test.data_length=1500

    def run(test):
        test.log.step("1. Configure the FTP port address")

        test.log.step("1.1. Configure no FTP port.")
        test.ftp_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                     command="get", host="ftp.wcss.pl", alphabet="1",
                                     user="anonymous", passwd="anonymous",
                                     files="pub/doc/Sieciowy_Savoir-vivre.txt")
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("2.1 Try to get/put a file via FTP")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_read_all_data(1500))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("1.2. Configure a valid and available FTP port that is not equal to the "
                      "default port number 21")
        test.ftp_client.dstl_set_files(test.file)
        test.ftp_client.dstl_set_ftp_command("put")
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("2.2. Try to get/put a file via FTP")
        test.put_file("{}".format(test.ftp_server.dstl_get_server_port()),
                      data_length=test.data_length)
        test.expect(len(test.ftp_server.dstl_ftp_server_get_file(test.file)) ==
                    test.data_length)

        test.log.step("1.3. Configure a port that is not equal to the default port number 21 "
                      "and it's not available on FTP server")
        ftp_not_reachable_port = "8888"
        test.ftp_client.dstl_set_port(ftp_not_reachable_port)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("2.3. Try to get/put a file via FTP")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile(expected=
                                                                                 ".*Connection "
                                                                                 "timed out.*",
                                                                                 timeout=120))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except Exception:
                test.log.error("Object was not created.")
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file):
                test.log.info("Problem with deleting file.")
        except Exception:
            test.log.error("Object was not created.")

    def put_file(test, port, data_length):
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_remote_address_and_port
                    (ip_version='IPv4').split(":")[1] == '{}\r'.format(port))
        test.expect(test.ftp_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


if __name__ == "__main__":
    unicorn.main()
