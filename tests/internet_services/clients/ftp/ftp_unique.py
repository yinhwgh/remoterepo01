#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0105126.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network


class Test(BaseTest):
    """
    TC intention: To check if unique parameter is supported during FTP session.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))


    def run(test):
        test.log.step("1. Define the FTP profile using unique parameter in cmd")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        file_name = "ftp_unique.txt"
        file_content = "12345qwert"
        test.ftp_server = FtpServer("IPv4", test, connection_setup.dstl_get_used_cid())
        ftp_client_unique = FtpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), command="unique",
                                     ip_server=test.ftp_server, alphabet="1", files=file_name)
        ftp_client_unique.dstl_set_parameters_from_ip_server()
        ftp_client_unique.dstl_generate_address()
        test.expect(ftp_client_unique.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open the defined profile.")
        test.expect(ftp_client_unique.dstl_get_service().dstl_open_service_profile())

        test.log.step("3. Check for proper URC, filename.")
        test.expect(ftp_client_unique.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="2100",
                                                                            urc_info_text=".*150 FILE: ftp.*",))

        ftp_unique_line = test.dut.at1.last_response.split("^SIS: 0,0,2100,\"150 FILE: ")
        unique_file_name = ftp_unique_line[1].replace('"', '').split("\r\n")[0]
        test.expect(ftp_client_unique.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("4. Write some data to file.")
        test.expect(ftp_client_unique.dstl_get_service().dstl_send_sisw_command(10))
        test.expect(ftp_client_unique.dstl_get_service().dstl_send_data(file_content))

        test.log.step("5. Close the defined service profile")
        test.expect(ftp_client_unique.dstl_get_service().dstl_close_service_profile())

        test.log.step("6. Define the FTP get profile using file name generated in step 4")
        ftp_client_get = FtpProfile(test.dut, 1, connection_setup.dstl_get_used_cid(), command="get",
                                     ip_server=test.ftp_server, alphabet="1", files=unique_file_name)
        ftp_client_get.dstl_set_parameters_from_ip_server()
        ftp_client_get.dstl_generate_address()
        test.expect(ftp_client_get.dstl_get_service().dstl_load_profile())

        test.log.step("7. Open the defined profile")
        test.expect(ftp_client_get.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("8. Read and compare all data")
        test.expect(ftp_client_get.dstl_get_service().dstl_read_return_data(10) == file_content)

        test.log.step("9. Close the defined service profile")
        test.expect(ftp_client_get.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Remove created file from FTP server")
        test.expect(test.ftp_server.dstl_ftp_server_delete_file(unique_file_name))

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()