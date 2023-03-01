# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0102422.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       TC intention: This test case should verify if connection to the SSL server is still possible
       after deletion of certificates using SBNW command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

    def run(test):
        test.log.step("1. Run OpenSSL server with one cipher suite supported by module.")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA")
        ip_address=test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("2. Load client certificate and server public certificate (micCert.der) "
                      "on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.expect(test.certificates.dstl_upload_openssl_certificates())

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time.")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services.")
        test.log.step("6. Activate Internet service connection.")
        test.log.info("Steps 5 and 6 will be performed in parallel")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("7. Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection.")
        test.profile = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                     protocol="tcp",
                                     host=ip_address,
                                     port=test.ssl_server.dstl_get_server_port(),
                                     secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("8. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("9. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("10. Check if server response is correct.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.expect(test.ssl_server.dstl_compare_cipher_suite(), msg="Incorrect server response!")

        test.log.step("11. Close socket profile.")
        test.log.info("Done in Step 10 to read server response.")

        test.log.step("12. Remove certificates from module using SBNW command.")
        test.certificates.dstl_delete_openssl_certificates()

        test.log.step("13. Open socket profile.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))

        test.log.step("14. Check if connection to the server is possible.")
        test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.expect(not test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.log.info("Deleting certificates if they are already installed.")
        try:
            test.certificates.dstl_delete_all_uploaded_certificates()
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError:
            test.log.error("Certificates object was not created.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()
