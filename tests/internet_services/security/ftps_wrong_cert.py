#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0103543.001

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
from os.path import join


class Test(BaseTest):
    """
    Intention: To check FTPS function on Module.

    description:
    1. Upload wrong certificates to Module.
    2. Check if certificates were correctly uploaded to Module.
    3. Attach Module to Network.
    4. Define FTPS "put" service profile to FTP server.
    5. Open defined profile.
    6. Check service and socket state using SISO command.
    7. Try to upload any file to FTP server (100 bytes).
    8. Check service and socket state using SISO command.
    9. Close FTP profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.file_name = "FtpFileName.txt"

    def run(test):
        test.log.step("1. Upload wrong certificates to Module.")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            for index in range(0, 11):
                test.certificates.dstl_delete_certificate(index)

        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates", "private_client_key")))

        test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates",
                                                                   "certificate_conf_1.der"))

        test.log.step("2. Check if certificates were correctly uploaded to Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Attach Module to Network.")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftps_server = FtpsServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.ftps_port = test.ftps_server.dstl_get_server_port()

        test.log.step("4. Define FTPS \"put\" service profile to FTP server.")
        ftps_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), command="put",
                                 ip_server=test.ftps_server, files=test.file_name, secopt="1", secure_connection=True)

        ftps_client.dstl_set_parameters_from_ip_server()
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open defined profile.")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.wait_for("The certificate does not exist"))

        test.log.step("6. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("7. Try to upload any file to FTP server (100 bytes).")
        test.expect(not ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(100, eod_flag="1"))

        test.log.step("8. Check service and socket state using SISO command.")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("9. Close FTP profile.")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):

        try:
            test.certificates.dstl_delete_certificate(0)
            test.certificates.dstl_delete_certificate(1)
        except AttributeError:
            test.log.error("certificates was not created.")

        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("server was not created.")

if __name__ == "__main__":
    unicorn.main()
