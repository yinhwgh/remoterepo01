#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0092768.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from os.path import join


class Test(BaseTest):
    """ Check socket secure connection with 2048 bit key and client/server authentication.
        Checking client authentication with and without private key."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.h2("Executing script for test case: 'TC0092768.001 BasicSocketSecureConnection'")

        test.log.step("1. Upload different than expected on server client certificate without private key"
                      " and correct server certificate with 2048 bit key.")
        test.certificates = InternetServicesCertificates(test.dut)
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates", "client.der"),
                                                             join("openssl_certificates", "private_client_key"))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates", "client", "ca.der")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("2. Try to establish socket TLS connection with server. Module should verify server certificate..")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP", check_client_certificate=True)
        test.socket_dtls = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), protocol="tcp",
                                         secopt="1", host=test.ssl_echo_server.dstl_get_server_FQDN(),
                                         port=test.ssl_echo_server.dstl_get_server_port(), secure_connection=True)
        test.socket_dtls.dstl_generate_address()
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.sleep(5)
        test.expect(test.socket_dtls.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())

        test.log.step("3. Upload correct client certificate with private key.")
        test.expect(test.certificates.dstl_delete_certificate(0))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)
        test.certificates.dstl_set_security_private_key("SHA1_RSA", "client", "pwdclient",
                                                        join("echo_certificates", "client", "client.ks"), "pwdclient")
        test.expect(test.certificates.dstl_upload_certificate_at_index_0(
                                                        join("echo_certificates", "client", "client.der"),
                                                        join("echo_certificates", "client", "client_priv.der")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("4. Try to establish socket TLS connection with server. Module should verify server certificate.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))
        test.expect(test.socket_dtls.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.log.step("5. Remove installed certificates.")
            test.expect(test.certificates.dstl_delete_certificate(1))
            test.expect(test.certificates.dstl_delete_certificate(0))
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")

        try:
            test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dtls.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")

        try:
            if not test.ssl_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
