# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0011639.001, TC TC0011639.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """ Check behavior if read command is called before receiving a read URC."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        data_50 = 50

        test.log.step("1. Define and activate PDP context / Define connection profile")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        dut_ip_address = connection_setup.dstl_get_pdp_address()[0]

        test.log.step("2. Enable IP services URCs using AT^SCFG command.")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.log.step("3. Configure FTP GET service profile")
        srv_id = "0"
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.ftp_server.dstl_ftp_server_create_file("test.txt", data_50, "")
        test.ftp_client = FtpProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(),
                                     command="get", alphabet=1, ip_server=test.ftp_server,
                                     files="test.txt")
        test.ftp_client.dstl_set_parameters_from_ip_server()
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Open the service profile and call AT^SISR before service is ready")
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_address))

        test.log.step("4.1. Wait for \"OK\"")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("4.2. Call AT^SISR.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_50, expected=".*ERROR.*"))
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

        test.log.step("4.3. Wait for ^SISR URC indicates the service is ready")
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("4.4. Check the service state with AT^SISO")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("5. Read rest data.")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(data_50))
        test.expect(test.ftp_client.dstl_get_service().dstl_get_confirmed_read_length() == data_50)

        test.log.step("6. Check the service state.")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("7. Close the FTP GET profile..")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.ftp_client.dstl_get_service().dstl_close_service_profile()
        test.ftp_client.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
