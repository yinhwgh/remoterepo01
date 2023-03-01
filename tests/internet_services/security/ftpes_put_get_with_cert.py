#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0102313.001, TC0102313.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.network_service.register_to_network import dstl_register_to_network
from os.path import join


class Test(BaseTest):
    """
    Intention: To check FTPES function on Module.
    Correct communication starts out as plain FTP (over e.g. port 21), but is upgraded to TLS/SSL encryption.

    Description:
    1. Upload certificates, which allow to connect to FTPES server, to Module.
    2. Check if certificates were correctly uploaded to Module.
    3. Attach Module to Network.
    4. Define FTPES "put" service profile to FTP server (secopt parameter = 1).
    5. Open defined profile. Check in URCs if encryption is used while connection.
    6. Check service and socket state using SISO command.
    7. Upload file to FTP server (size 1KB).
    8. Check service and socket state using SISO command.
    9. Close FTP put profile.
    10. Define FTPES "get" service profile to FTP server (same file that was uploaded in step 7)
    11. Open defined profile. Check in URCs if encryption is used while connection.
    12. Check service and socket state using SISO command.
    13. Download whole file from FTP server (wait for proper URC after downloading file).
    14. Check service and socket state using SISO command.
    15. Close FTP get profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.file_name = "FTPES_PutGet_WithCert.txt"

    def run(test):
        test.log.info("TC0102313.001 / TC0102313.002 - FTPES_PutGet_WithCert")
        amount_of_data = 1024

        test.log.step("1. Upload certificates, which allow to connect to FTPES server, to Module).")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates", "private_client_key")))
        test.certificates.dstl_upload_server_certificate("1", join("echo_certificates", "client","ca.der"))

        test.log.step("2. Check if certificates were correctly uploaded to Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step(" 3. Attach Module to Network.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        used_cid = connection_setup.dstl_get_used_cid()

        test.log.step("4. Define FTPES 'put' service profile to FTP server (secopt parameter = 1).")
        ftpes_client_put_get = FtpProfile(test.dut, 0, used_cid, command="put", alphabet=1, ftpes=True,
                                                files=test.file_name, secopt="1", secure_connection=True)
        test.ftpes_server = FtpServer("IPv4", test, used_cid)
        ftpes_client_put_get.dstl_set_parameters_from_ip_server(test.ftpes_server)
        ftpes_client_put_get.dstl_generate_address()
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open defined profile. Check in URCs if encryption is used while connection. ")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_open_service_profile())
        test.expect(ftpes_client_put_get.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="200",
                                                            urc_info_text=".*openFtpData with TLS DATA.*"))
        test.expect(ftpes_client_put_get.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6. Check service and socket state using SISO command.")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value,
                    msg="Wrong service state")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("7. Upload file to FTP server (size 1KB) ")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_send_sisw_command_and_data(amount_of_data,
                                                                                eod_flag="1"))

        test.log.step("8. Check service and socket state using SISO command.")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("9) Close FTP put profile.")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Define FTPES \"get\" service profile to FTP server (same file that was uploaded in step 7).")
        ftpes_client_put_get.dstl_set_ftp_command("get")
        ftpes_client_put_get.dstl_generate_address()
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_load_profile())

        test.log.step("11) Open defined profile. Check in URCs if encryption is used while connection.")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_open_service_profile())
        test.expect(ftpes_client_put_get.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="200",
                                                                        urc_info_text=".*openFtpData with TLS DATA.*"))
        test.expect(ftpes_client_put_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("12) Check service and socket state using SISO command.")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("13) Download whole file from FTP server (wait for proper URC after downloading file).")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_read_data(amount_of_data))
        test.expect(ftpes_client_put_get.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("14) Check service and socket state using SISO command.")
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(ftpes_client_put_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("15) Close FTP get profile.")
        test.expect(ftpes_client_put_get.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.certificates.dstl_delete_all_certificates_using_ssecua()
            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.certificates.dstl_delete_certificate(0)
                test.certificates.dstl_delete_certificate(1)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0, msg="Certificates not removed")
        except AttributeError:
            test.log.error("certificates was not created.")

        try:
            if not test.ftpes_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftpes_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")


if __name__ == "__main__":
    unicorn.main()
