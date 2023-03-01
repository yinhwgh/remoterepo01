# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0103480.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates \
    import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from os.path import join
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Check socket secure connection with 4096 bit key and client/server authentication."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

    def run(test):
        test.log.info("Executing script for test case:"
                      "'TC0103480.001 BasicSocketSecureConnection4096'")

        test.log.step("1. Upload client certificate with private key and server certificate "
                      "with 4096 bit key.")
        test.certificates = InternetServicesCertificates(test.dut)
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.expect(test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates",
                                                                  "client.der"),
                                                             join("openssl_certificates",
                                                                  "private_client_key")))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates",
                                                                             "client",
                                                                             "ca_4096.der")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("2. Run OpenSSL server without client certificate verification.")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384")
        fqdn_server_address = test.ssl_server.dstl_get_server_FQDN()
        server_port = test.ssl_server.dstl_get_server_port()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="4WithoutClientVerificationUnicorn")
        test.sleep(3)

        test.log.step("3. Try to establish socket TLS connection with server. "
                      "Module should verify server certificate.")
        test.socket_tls = SocketProfile(test.dut, 0, test.cid, protocol="tcp", secopt="1",
                                        host=fqdn_server_address, port=server_port,
                                        secure_connection=True)
        test.socket_tls.dstl_generate_address()
        test.expect(test.socket_tls.dstl_get_service().dstl_load_profile())
        test.open_and_check_service_profile()
        test.ssl_server_thread.join()

        test.log.step("4. Run OpenSSL server with client certificate verification.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="4WithClientVerificationUnicorn")

        test.log.step("5. Try to establish socket TLS connection with server. "
                      "Module should verify server certificate, but use wrong CA file.")
        test.log.info("Different CA client file than on server was uploaded in step 1")
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates",
                                                                             "client",
                                                                             "ca.der")))
        test.expect(test.socket_tls.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(test.socket_tls.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.sleep(5)
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()

        test.log.step("6. Remove server certificate.")
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

        test.log.step("7. Run OpenSSL server without client certificate verification.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="4WithoutClientVerificationUnicorn")

        test.log.step("8. Try to establish socket TLS connection with server. "
                      "Module should NOT verify server certificate.")
        test.socket_tls.dstl_set_secopt("0")
        test.expect(test.socket_tls.dstl_get_service().dstl_write_secopt())
        test.open_and_check_service_profile()
        test.ssl_server_thread.join()

    def cleanup(test):
        try:
            test.log.step("9. Remove client certificate.")
            test.expect(test.certificates.dstl_delete_certificate(0))
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0):
                test.certificates.dstl_delete_all_uploaded_certificates()
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError:
            test.log.error("Certificate object was not created.")

        try:
            test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_tls.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")

        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

    def open_and_check_service_profile(test):
        test.expect(test.socket_tls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
