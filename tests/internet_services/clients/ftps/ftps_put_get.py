#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0102379.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from os.path import join


class Test(BaseTest):
    """
    Intention: To check FTPS function on Module.

    description:
    1. Define the FTPS session
    a. Upload certificates, which allow to connect to FTPS server (on the module side).
    b. Check if certificates were correctly uploaded
    c. Define FTPS service session for PUT command.
    d. Define FTPS service session for GET command.

    2. Start the FTPS session (PUT)
    a. Open the defined service profile
    b. Check for proper URC
    c. Upload small file (~1KB) to FTPS server
    d. Check Internet service state
    e. Close the defined service profile

    3. Start the FTPS session (GET)
    a. Open the defined service profile
    b. Check for proper URC
    c. Download the small file from FTPS server
    d. Check Internet service state
    e. Close the defined service profile
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.file_name = "ftps_put_get.txt"

    def run(test):
        test.log.step("1. Define the FTPS session")
        test.log.step("1a. Upload certificates, which allow to connect to FTPS server (on the module side).")

        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates", "private_client_key")))

        test.certificates.dstl_upload_server_certificate("1", join("echo_certificates", "client",
                                                                   "ca.der"))

        test.log.step("1b. Check if certificates were correctly uploaded")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("1c. Define FTPS service session for PUT command.")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        used_cid = test.connection_setup.dstl_get_used_cid()
        test.ftps_server = FtpsServer("IPv4", test, used_cid)
        ftps_client = FtpProfile(test.dut, 0, used_cid, command="put", alphabet=1,
                                 ip_server=test.ftps_server, files=test.file_name, secopt="1", secure_connection=True)

        ftps_client.dstl_set_parameters_from_ip_server()
        ftps_client.dstl_generate_address()
        test.expect(ftps_client.dstl_get_service().dstl_load_profile())

        test.log.step("1d. Define FTPS service session for GET command.")
        ftps_client_get = FtpProfile(test.dut, 1, used_cid, command="get", alphabet=1, 
                                 ip_server=test.ftps_server, files=test.file_name, secopt="1", secure_connection=True)

        ftps_client_get.dstl_set_parameters_from_ip_server()
        ftps_client_get.dstl_generate_address()
        test.expect(ftps_client_get.dstl_get_service().dstl_load_profile())

        test.log.step("2. Start the FTPS session (PUT)")
        test.log.step("2a. Open the defined service profile")
        test.expect(ftps_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("2b. Check for proper URC")
        test.expect(ftps_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("2c. Upload small file (~1KB) to FTPS server")
        package_size = 1024
        test.expect(ftps_client.dstl_get_service().dstl_send_sisw_command_and_data(package_size, eod_flag="1"))

        test.log.step("2d. Check Internet service state")
        test.sleep(5)
        test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("2e. Close the defined service profile")
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("3. Start the FTPS session (GET)")
        test.log.step("3a. Open the defined service profile")
        test.expect(ftps_client_get.dstl_get_service().dstl_open_service_profile())

        test.log.step("3b. Check for proper URC")
        test.expect(ftps_client_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("3c. Download the small file from FTPS server")
        test.expect(ftps_client_get.dstl_get_service().dstl_read_return_data(package_size))
        test.expect(ftps_client_get.dstl_get_parser().dstl_get_service_data_counter("rx") == package_size)

        test.log.step("3d. Check Internet service state")
        test.sleep(3)
        test.expect(ftps_client_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(ftps_client_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")

        test.log.step("3e. Close the defined service profile")
        test.expect(ftps_client_get.dstl_get_service().dstl_close_service_profile())
        test.expect(ftps_client_get.dstl_get_service().dstl_reset_service_profile())
        test.expect(ftps_client.dstl_get_service().dstl_close_service_profile())
        test.expect(ftps_client.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):

        try:
            test.certificates.dstl_delete_certificate(0)
            test.certificates.dstl_delete_certificate(1)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0, msg="Certificates not removed")
        except AttributeError:
            test.log.error("certificates was not created.")

        try:
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftps_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")


if __name__ == "__main__":
    unicorn.main()
