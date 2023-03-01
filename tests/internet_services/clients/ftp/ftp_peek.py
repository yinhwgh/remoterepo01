#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0012065.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Verify the peek functionality for FTP (AT^SISR=<srvProfileId>,0)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.file_name = "100bytes.txt"
        test.file_size = 100

    def run(test):
        test.log.step("1. Configure connection profile or PDP context.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.ftp_server.dstl_ftp_server_create_file(test.file_name, test.file_size)

        test.log.step("2. Configure a FTP get service profile.")
        test.ftp_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), command="get",
                                ip_server=test.ftp_server, alphabet="1", files=test.file_name)
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open the FTP service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("4. Read some data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(10))

        test.log.step("5. Call the peek command (AT^SISR=<srvProfileId>,0).")
        ftp_parser = InternetServiceParser(test.dut.at1, 0)
        test.expect(ftp_parser.dstl_get_peek_value_of_data_to_read() == 90)

        test.log.step("6. Read some data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(20))

        test.log.step("7. Call the peek command (AT^SISR=<srvProfileId>,0).")
        test.expect(ftp_parser.dstl_get_peek_value_of_data_to_read() == 70)

        test.log.step("8. Read all data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_all_data(1500, 500))

        test.log.step("9. Call the peek command (AT^SISR=<srvProfileId>,0).")
        test.expect(ftp_parser.dstl_get_peek_value_of_data_to_read() == -2)

        test.log.step("10. Close profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.warn("Problem with deleting created test file.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if (__name__ == "__main__"):
    unicorn.main()
