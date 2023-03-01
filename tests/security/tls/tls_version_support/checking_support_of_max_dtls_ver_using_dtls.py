# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0102314.002, TC0102314.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC name:
    TC0102314.001/002 CheckingSupportOfMaxDTLS_VerUsingDTLS

    Intention:
    Testing if DTLSv1_2 protocol version is used during DTLS connection when on module and on server
    all DTLS versions can be accepted.

    description:
    1. Run OpenSSL server using DTLS:
    s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem -key mic.pem -
    keyform pem -dtls -brief
    2. Load client certificate and server public certificate (micCert.der) on module.
    3. Check if certificates are installed
    4. Set Real Time Clock to current time
    5. Define PDP context for Internet services.
    6. Activate Internet service connection.
    7. Set Tcp/TLS/Version to:
    - for "TLS_min_version" to "MIN"
    - for "TLS_max_version" to "MAX"
    8. Define UDP socket client profile to openSSL server. Use sockudps connection.
    9. Enable Security Option of IP service (secopt parameter).
    10. Open socket profile.
    11. Check if server response is correct.
    12. Close socket profile.
    13. Remove certificates from module.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        test.log.info("Starting TC0102314.001/002 CheckingSupportOfMaxDTLS_VerUsingDTLS")
        test.log.step("1. Run OpenSSL server using DTLS:")
        test.ssl_server = SslServer("IPv4", "dtls", "TLS_RSA_WITH_AES_128_CBC_SHA256")

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_openssl_certificates()
        test.expect(test.certificates.dstl_upload_openssl_certificates())

        test.log.step("3. Check if certificates are installed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                   msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services.")
        connection = dstl_get_connection_setup_object(test.dut)
        test.expect(connection.dstl_load_internet_connection_profile())

        test.log.step("6. Activate Internet service connection.")
        test.expect(connection.dstl_activate_internet_connection(),
                    msg="Could not activate PDP context")

        test.log.step("7. Set Tcp/TLS/Version to: \n"
                      "- for \"TLS_min_version\" to \"MIN\"\n"
                      "- for \"TLS_max_version\" to \"MAX\"\")")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

        test.log.step("8. Define UDP socket client profile to openSSL server. "
                      "Use sockudps connection.")
        test.profile = SocketProfile(test.dut, "0", connection.dstl_get_used_cid(),
                       host=test.ssl_server.dstl_get_server_ip_address(), port=test.ssl_server.
                                     dstl_get_server_port(),
                       protocol="udp", secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, tls_version="")

        test.log.step("9. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("10. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)

        test.log.step("11. Check if server response is correct.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.log.info(test.ssh_server.last_response)
        test.expect("DTLSv1.2" in test.ssh_server.last_response,
                    msg="Incorrect or missing \"DTLSv1.2\" in server response!")

    def cleanup(test):
        test.log.step("12. Close socket profile.")
        try:
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("13. Remove certificates from module.")
        try:
            test.certificates.dstl_delete_all_certificates_using_ssecua()
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_certificate("1")
                test.certificates.dstl_delete_certificate("0")
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                        msg="Wrong amount of certificates installed")
        except AttributeError:
            test.log.error("Certificate object was not created.")
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")
        dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX")


if "__main__" == __name__:
    unicorn.main()