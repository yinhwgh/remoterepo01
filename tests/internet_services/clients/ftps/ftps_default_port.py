#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0104328.001

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
from dstl.internet_service.parser.internet_service_parser import ServiceState
from os.path import join
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response


class Test(BaseTest):
    """
    Intention: To check if Ftps profile uses default port (990).

    description:
    1. Define the FTPS session
    a. Upload certificates, which allow to connect to FTPS server (on the module side)
    b. Check if certificates were correctly uploaded
    c. Define FTPS service session for PUT command without customized port

    2. Start the FTPS session
    a. Open the defined service profile
    b. Check for proper URC
    c. Upload small file (~1KB) to FTPS server
    d. Check Internet service state
    e. Check used port.
    f. Close the defined service profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.ftps_server = FtpsServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.ftps_port = test.ftps_server.dstl_get_server_port()
        test.file_name = "FtpFileName.txt"
        test.expect(dstl_enter_pin(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

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

        test.log.step("1c. Define FTPS service session for PUT command without customized port")

        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.ftps_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), command="put",
                                      alphabet="1", ip_server=test.ftps_server, files=test.file_name, secopt="1",
                                      secure_connection=True)

        test.ftps_client.dstl_set_parameters_from_ip_server()
        test.ftps_client.dstl_set_port("")
        test.ftps_client.dstl_generate_address()
        test.expect(test.ftps_client.dstl_get_service().dstl_load_profile())
        test.dut.at1.send_and_verify("AT^SISS?")
        test.expect('{}"'.format(test.ftps_server.dstl_get_server_ip_address()) in test.dut.at1.last_response,
                    msg="incorrect address parameter in module")

        test.log.step("2. Start the FTPS session")

        test.log.step("2a. Open the defined service profile")
        test.expect(test.ftps_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("2b. Check for proper URC")
        test.expect(test.ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("2c. Upload small file (~1KB) to FTPS server")
        test.expect(test.ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(1024, eod_flag="1"))
        test.expect(test.ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("d. Check Internet service state")
        test.expect(test.ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")

        test.log.step("2e. Check used port.")
        rem_address = test.ftps_client.dstl_get_parser().dstl_get_service_remote_address_and_port("IPv4")
        test.expect("990" in rem_address)

    def cleanup(test):

        test.log.step("2f. Close the defined service profile.")
        try:
            test.expect(test.ftps_client.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Problem with connection to module")

        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("server was not created.")

        try:
            test.certificates.dstl_delete_certificate(0)
            test.certificates.dstl_delete_certificate(1)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0, msg="Certificates not removed")
        except AttributeError:
            test.log.error("certificates was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

if __name__ == "__main__":
    unicorn.main()
