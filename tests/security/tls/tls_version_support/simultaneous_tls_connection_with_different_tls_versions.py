# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0104225.001, TC0104225.002

import unicorn

from os.path import join
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_remove_cipher_suites_file
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC name:
    TC0104225.002/001 SimultaneousTLSConnectionWithDifferentTLSVersions

    Intention:
    Check if TLS connection can be simultaneously established between 4 secure TCP/UDP clients
    on module, and remote instances of OpenSSL server with specific versions of TLS/DTLS set
    (DTLS 1.0/DTLS1.2TLS 1.1/TLS 1.2/TLS1.3) - depends on supported by product.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_remove_cipher_suites_file(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

        test.log.step("	1. Define and activate PDP context / internet connection profile.")
        test.connection = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection.dstl_load_internet_connection_profile())
        test.expect(test.connection.dstl_activate_internet_connection())

        test.log.step("2. Add client certificate with private key file at index 0 and server "
                      "certificate")
        test.certificates = InternetServicesCertificates(test.dut)
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates",
                                                                "private_client_key")))
        test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates",
                                                                   "certificate_conf_1.der"))

        test.log.step("3. Check if certificates have been installed on module")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Run several separate instances of OpenSSL servers, each with different "
                      "specific TLS version supported by module e.g.: DTLS1.2, TLS1.1, TLS 1.2, "
                      "TLS1.3")
        test.dtls_1_2 = SslServer("IPv4", "dtls", "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA")
        test.dtls_1_2_thread = test.thread(test.dtls_1_2.dstl_run_ssl_server, tls_version="1_2",
                                           ssh_server_property='ssh_server_5')

        test.tls_1_1 = SslServer("IPv4", "socket_tls", "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA")
        test.tls_1_1_thread = test.thread(test.tls_1_1.dstl_run_ssl_server, tls_version="1_1",
                                          ssh_server_property='ssh_server_2')

        test.tls_1_2 = SslServer("IPv4", "socket_tls", "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA")
        test.tls_1_2_thread = test.thread(test.tls_1_2.dstl_run_ssl_server, tls_version="1_2",
                                          ssh_server_property='ssh_server_3')

        test.tls_1_3 = SslServer("IPv4", "socket_tls", "TLS_AES_128_CCM_SHA256")
        test.tls_1_3_thread = test.thread(test.tls_1_3.dstl_run_ssl_server, tls_version="1_3",
                                          ssh_server_property='ssh_server_4')

        test.log.step("5. Define secure tcp client profiles and udp clients with server "
                      "certificate check parameter set to on (e.g. secopt 1) for every instance of "
                      "OpenSSL server that is running.")
        test.dtls_1_2_profile = create_profile(test, "0", test.dtls_1_2, "udp")
        test.tls_1_1_profile = create_profile(test, "1", test.tls_1_1, "tcp")
        test.tls_1_2_profile = create_profile(test, "2", test.tls_1_2, "tcp")
        test.tls_1_3_profile = create_profile(test, "3", test.tls_1_3, "tcp")

        test.log.step("6. Open socket profile")
        test.expect(test.dtls_1_2_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.tls_1_1_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.tls_1_2_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.tls_1_3_profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("7. Check client srv states")
        test.expect(
            test.dtls_1_2_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(
            test.tls_1_1_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(
            test.tls_1_2_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(
            test.tls_1_3_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("8. Check handshake responses from servers (if tested manually)")
        test.log.info("not tested manually")

        test.log.step("9. Close socket.")
        test.dtls_1_2_profile.dstl_get_service().dstl_close_service_profile()
        test.tls_1_1_profile.dstl_get_service().dstl_close_service_profile()
        test.tls_1_2_profile.dstl_get_service().dstl_close_service_profile()
        test.tls_1_3_profile.dstl_get_service().dstl_close_service_profile()

        test.dtls_1_2_thread.join()
        test.tls_1_1_thread.join()
        test.tls_1_2_thread.join()
        test.tls_1_3_thread.join()


    def cleanup(test):
        test.log.step("10. Remove client and server certificate.")
        try:
            test.certificates.dstl_delete_all_uploaded_certificates()
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_certificate("1")
                test.certificates.dstl_delete_certificate("0")

                test.log.step("11. Check if certificates have been removed.")
                test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                            msg="Wrong amount of certificates installed")
        except AttributeError:
            test.log.error("Certificate object was not created.")

        test.log.step("12. Close and reset internet service profiles.")
        try:
            test.dtls_1_2_profile.dstl_get_service().dstl_close_service_profile()
            test.expect(test.dtls_1_2_profile.dstl_get_service().dstl_reset_service_profile())
            test.tls_1_1_profile.dstl_get_service().dstl_close_service_profile()
            test.expect(test.tls_1_1_profile.dstl_get_service().dstl_reset_service_profile())
            test.tls_1_2_profile.dstl_get_service().dstl_close_service_profile()
            test.expect(test.tls_1_2_profile.dstl_get_service().dstl_reset_service_profile())
            test.tls_1_3_profile.dstl_get_service().dstl_close_service_profile()
            test.expect(test.tls_1_3_profile.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Problem with service profiles")

        try:
            test.dtls_1_2_thread.join()
            test.tls_1_1_thread.join()
            test.tls_1_2_thread.join()
            test.tls_1_3_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")


def create_profile(test, srv_id, ssl_server, protocol):
    profile = SocketProfile(test.dut, srv_id, test.connection.dstl_get_used_cid(), secopt="1",
                            host=ssl_server.dstl_get_server_ip_address(),
                            port=ssl_server.dstl_get_server_port(),
                            protocol=protocol, secure_connection=True)
    profile.dstl_generate_address()
    test.expect(profile.dstl_get_service().dstl_load_profile())
    return profile


if (__name__ == "__main__"):
    unicorn.main()
