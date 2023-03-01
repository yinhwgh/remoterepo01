#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0010954.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """
    Test FTP when at least one optional parameter is not configured.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.file_name = "FtpMissingParamsOK.txt"

    def run(test):
        test.log.info("TC0010954.001 FtpMissingParamsOK")
        amount_of_data = 1024

        test.log.step("1. Define PDP context and activate it "
                      "(if module doesn't support PDP context, define connection profile).")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        used_cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Configure FTP service with mandatory and optional parameters but at least one optional"
                      " parameter is not configured.\r\n (in this step: ipver, ftpath are not configured)")
        test.ftp_server = FtpServer("IPv4", test, used_cid)
        test.ftp_client = FtpProfile(test.dut, 0, used_cid, command="put", alphabet=1, files=test.file_name,
                                secopt="0", tcp_mr=15)
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_set_host(test.ftp_server.dstl_get_server_FQDN())
        test.ftp_client.dstl_set_port(test.ftp_server.dstl_get_server_port())
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open the service and try to initiate a file transfer (put or get)")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(amount_of_data,eod_flag="1"))

        test.log.step("4. Close the service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("5. Repeat the test steps describes above and leave another optional parameter")

        test.log.step("2.2 Configure FTP service with mandatory and optional parameters but at least one optional"
                      " parameter is not configured.\r\n (in this step: secopt, tcp_mr is not configured)")
        test.ftp_client = FtpProfile(test.dut, 0, used_cid, command="get", alphabet=1, files=test.file_name, ip_version=4,
                                ftpath="/")
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3.2 Open the service and try to initiate a file transfer (put or get)")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(amount_of_data))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("4.2 Close the service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())


if __name__ == "__main__":
    unicorn.main()
