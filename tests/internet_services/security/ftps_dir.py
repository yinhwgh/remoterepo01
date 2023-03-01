#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0102377.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from os.path import join


class Test(BaseTest):
    """
    Basic test of support the FTPS feature

    description:
    1. Define the FTPS session
    a. Upload certificates, which allow to connect to FTPS server (on the module side).
    b. Check if certificates were correctly uploaded
    c. Define FTPS service session for DIR command.

    2. Start the FTPS session (DIR)
    a. Open the defined service profile
    b. Check for proper URC
    c. Check for presence of the already stored files
    d. Check Internet service state
    e. Close the defined service profile
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.connection_setup.dstl_load_and_activate_internet_connection_profile()
        test.ftps_server = FtpsServer("IPv4", test, test.connection_setup.dstl_get_used_cid())

    def run(test):
        test.log.step("1. Define the FTPS session")

        test.log.step("1a. Upload certificates, which allow to connect to FTPS server (on the module side)")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            for index in range(0, 11):
                test.certificates.dstl_delete_certificate(index)

        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates", "private_client_key")))

        test.certificates.dstl_upload_server_certificate("1", join("echo_certificates", "client",
                                                                   "ca.der"))

        test.log.step("1b. Check if certificates were correctly uploaded")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.ftps_server.dstl_ftp_server_create_file("test1", 50, "")
        test.ftps_server.dstl_ftp_server_create_file("test2", 50, "")

        test.log.step("1c. Define FTPS service session for DIR command.")

        ftps_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), command="dir", alphabet="1",
                                 ip_server=test.ftps_server, files="test1", secopt="1", secure_connection=True)

        ftps_client.dstl_set_parameters_from_ip_server()
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("2. Start the FTPS session")

        test.log.step("2a. Open the defined service profile")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("2b. Check for proper URC")
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("2c. Check for presence of the already stored files")
        test.expect(ftps_client.dstl_get_service().dstl_read_data(1500))
        test.expect(("test1" in test.dut.at1.last_response) and ("test2" in test.dut.at1.last_response),
                    msg="wrong server response")

        test.log.step("2d. Check Internet service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("2e. Close the defined service profile")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file("test1")
            test.ftps_server.dstl_ftp_server_delete_file("test2")
        except AttributeError:
            test.log.error("Object was not created.")

        try:
            test.certificates.dstl_delete_certificate(0)
            test.certificates.dstl_delete_certificate(1)
        except AttributeError:
            test.log.error("certificates was not created.")

if __name__ == "__main__":
    unicorn.main()
