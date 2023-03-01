#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0093726.001, TC0093726.002

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
    TC intention: To test FTP with IPv6 (using FQDN server address).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.file_size = 1500
        test.file_name = "FTPWithIpv6.txt"

    def run(test):
        test.log.step("1. Define PDP context with PDP_type = IPv6 and activate it.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Set up an FTP service profile (using FQDN server address).")
        test.ftp_server = FtpServer("IPv6", test, connection_setup.dstl_get_used_cid())
        ftp_fqdn_address = test.ftp_server.dstl_get_server_FQDN()
        test.ftp_client = FtpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), command="put",
                            alphabet="1", files=test.file_name, port=test.ftp_server.dstl_get_server_port(),
                            host=ftp_fqdn_address, user=test.ftp_server.dstl_get_ftp_server_user(),
                            passwd=test.ftp_server.dstl_get_ftp_server_passwd(), are_concatenated=True,
                            ip_version="IPv6")
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined service profile.")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Upload some data to the FTP server.")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.file_size , eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("5. Close the FTP internet service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(len(test.ftp_server.dstl_ftp_server_get_file(test.file_name)) == test.file_size)

    def cleanup(test):
        try:
            test.ftp_server.dstl_server_close_port()
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
