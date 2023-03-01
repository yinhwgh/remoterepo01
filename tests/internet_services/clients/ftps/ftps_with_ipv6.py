#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0105226.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """To test FTPs support using IPv6"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.file_name = "Ftps_with_Ipv6.txt"

    def run(test):
        test.log.h2("Executing script for test case: 'TC0105226.001 Ftps_with_Ipv6'")

        test.log.step("1. Define and activate IPv6 PDP Context.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        connection_setup.dstl_load_and_activate_internet_connection_profile()
        con_id = connection_setup.dstl_get_used_cid()

        test.log.step("2. Set up an FTPs service profile (using FQDN server address).")
        test.ftps_server = FtpsServer("IPv6", test, con_id)

        ftps_client = FtpProfile(test.dut, 0, con_id, command="put", alphabet='1', files=test.file_name,
                                 ip_version="ipv6", secopt='0', secure_connection=True)
        ftps_client.dstl_set_parameters_from_ip_server(test.ftps_server)
        ftps_client.dstl_set_host(test.ftps_server.dstl_get_server_FQDN())
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined service profile.")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Upload or download some data.")
        test.expect(ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(500, eod_flag='1'))
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("5. Close the FTPs internet service.")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("6. Repeat steps 2-5 but this time use IPV6 IP server address.")

        test.log.step("6.2. Set up an FTPs service profile (using FQDN server address).")
        ftps_client.dstl_set_ftp_command("get")
        ftps_client.dstl_set_host(test.ftps_server.dstl_get_server_ip_address())
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("6.3. Open defined service profile.")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("6.4. Upload or download some data.")
        test.expect(ftps_client.dstl_get_service().dstl_read_data(500))
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(ftps_client.dstl_get_service().dstl_get_confirmed_read_length() == 500)

        test.log.step("6.5. Close the FTPs internet service.")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Server object was not created.")


if __name__ == "__main__":
    unicorn.main()
