#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0105121.001, TC0105121.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: To test FTP with IPv6 (using IP server address).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_size = 1024
        test.file_name = "FTPWithIpv6_using_IP_address.txt"

    def run(test):
        test.log.step("1. Define PDP context with PDP_type = IPv6 and activate it.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftp_server = FtpServer("IPv6", test, connection_setup.dstl_get_used_cid())
        test.ftp_server.dstl_ftp_server_create_file(file_name=test.file_name, file_size=test.file_size)

        test.log.step("2. Set up an FTP get service profile (using IP server address).")
        test.ftp_client = FtpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), command="get",
                                     alphabet="1", files=test.file_name)
        test.ftp_client.dstl_set_parameters_from_ip_server(ip_server=test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined service profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("4. Read some data from the FTP server.")
        test.expect(len(test.ftp_client.dstl_get_service().dstl_read_return_data(test.file_size)) == test.file_size)

        test.log.step("5. Close the FTP internet service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.ftp_server.dstl_server_close_port()
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
