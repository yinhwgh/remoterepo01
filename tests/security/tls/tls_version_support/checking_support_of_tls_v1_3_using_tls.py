# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0104373.002

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
        Testing if  TLS1.3 protocol version is used during TLS connection
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.step("1. Run OpenSSL server using TLSv1.3: \
       s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem -key mic.pem "
                      "-keyform pem -tls1_3 -msg")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_AES_128_GCM_SHA256")
        ip_address=test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()
        test.expect(test.certificates.dstl_upload_openssl_certificates())

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time.")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services.")
        connection = dstl_get_connection_setup_object(test.dut)
        test.expect(connection.dstl_load_internet_connection_profile())

        test.log.step("6. Activate Internet service connection.")
        test.expect(connection.dstl_activate_internet_connection(),
                    msg="Could not activate PDP context")

        test.log.step("7. Set Tcp/TLS/Version to:\
        - for \"TLS_min_version\" to \"1.3\"\
        - for \"TLS_max_version\" to \"MAX\"")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.3", "MAX"))

        test.log.step("8. Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection.")
        test.profile = SocketProfile(test.dut, 0, connection.dstl_get_used_cid(), protocol="tcp",
                                     host=ip_address,
                                     port=test.ssl_server.dstl_get_server_port(),
                                     secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("9. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("10. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("11. Check if server response is correct.")
        test.expect("TLS 1.3, Handshake" in test.ssh_server.last_response,
                    msg="Incorrect or missing \"TLS 1.3 Handshake\" in server response!")

        test.log.step("12. Close socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("13. Remove certificates from module.")
        try:
            test.expect(test.certificates.dstl_delete_openssl_certificates())
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError: test.log.error("Certificate object was not created.")
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")
        dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX")


if "__main__" == __name__:
    unicorn.main()
