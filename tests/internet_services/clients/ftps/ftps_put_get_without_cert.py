#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0103542.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState


class Test(BaseTest):
    """
    Intention: To check FTPS function on Module.

    description:
    1. Delete all certificates, from Module.
    2. Check that no certificates are present on Module.
    3. Attach Module to Network.
    4. Define FTPS "put" service profile to FTP server (secopt parameter = 0).
    5. Open defined profile.
    6. Check service and socket state using SISO command.
    7. Upload file to FTP server (size 1KB).
    8. Check service and socket state using SISO command.
    9. Close FTP put profile.
    10. Define FTPS "get" service profile to FTP server (same file that was uploaded in step 7)
    11. Open defined profile.
    12. Check service and socket state using SISO command.
    13. Download whole file from FTP server (wait for proper URC after downloading file).
    14. Check service and socket state using SISO command.
    15. Close FTP get profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)


    def run(test):
        test.log.step("1. Delete all certificates, from Module.")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            for index in range(0, 11):
                test.certificates.dstl_delete_certificate(index)

        test.log.step("2. Check that no certificates are present on Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Attach Module to Network.")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftps_server = FtpsServer(test = test, con_id=test.connection_setup.dstl_get_used_cid(), ip_version="IPv4")
        test.ftps_port = test.ftps_server.dstl_get_server_port()
        test.file_name = "FtpsPutGetWithoutCert.txt"

        test.log.step("4. Define FTPS \"put\" service profile to FTP server "
                      "(secopt parameter = 0).")
        ftps_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                 command="put", ip_server=test.ftps_server, files=test.file_name,
                                 secopt="0", secure_connection=True, alphabet="1")

        ftps_client.dstl_set_parameters_from_ip_server()
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open defined profile.")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("7. Upload file to FTP server (size 1KB).")
        test.expect(ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(1024, eod_flag="1"))
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("8. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("9. Close FTP put profile.")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Define FTPS \"get\" service profile to FTP server (same file that was uploaded in step 7)")
        ftps_client.dstl_set_ftp_command("get")
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("11. Open defined profile")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("12. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("13. Download whole file from FTP server (wait for proper URC after downloading file).")
        test.expect(ftps_client.dstl_get_service().dstl_read_return_data(1024))
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("14. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("15. Close FTP get profile.")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")

if __name__ == "__main__":
    unicorn.main()
