# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102302.002

import unicorn

from os.path import join
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """
    TC name:
    CheckingSupportOfTLSv1_1UsingTLS

    Intention:
    Testing if  TLS1.1 protocol version is used during TLS connection

    description:
    1. Run OpenSSL server using TLSv1.1:
    s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem -key mic.pem
    -keyform pem -tls1_1 -msg
    Path to certificates: \\view\aktuell\z_pegasus_swt\plugins\com.cinterion.pegasus.testprocedure\src
    \pegasus\testProcedure\network\wm\st\func\ipnet\SSLcertFiles\OpenSSLFiles\ServerConfigCerts
    2. Load client certificate and server public certificate (micCert.der) on module.
    Path to certificate: \\view\aktuell\z_pegasus_swt\plugins\com.cinterion.pegasus.testprocedure\src
    \pegasus\testProcedure\network\wm\st\func\ipnet\SSLcertFiles\OpenSSLFiles
    3. Check if certificates are installed
    4. Set Real Time Clock to current time
    5. Define PDP context for Internet services.
    6. Activate Internet service connection.
    7. Set Tcp/TLS/Version to:
    - for "TLS_min_version" to "MIN"
    - for "TLS_max_version" to 1.2
    8. Define TCP socket client profile to openSSL server. Use socktcps connection.
    9. Enable Security Option of IP service (secopt parameter).
    10. Open socket profile.
    11. Check if server response is correct.
    12. Close socket profile.
    13. Remove certificates from module
    14. Additional for manual test - check package logs from server in Wireshark
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))

    def run(test):
        test.log.step("1. Run OpenSSL server using TLS1_1 param")
        ciphersuite = "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
        test.certificates = InternetServicesCertificates(test.dut)

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")), (join("openssl_certificates",
                                                                "private_client_key")))

        test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates",
                                                              "certificate_conf_1.der"))

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

        test.log.step("7. Set Tcp/TLS/Version to:"
                      "- for \"TLS_min_version\" to \"MIN\""
                      "- for \"TLS_max_version\" to \"1.2\"\")")

        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "1.2"))

        test.log.step("8. Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection.")
        test.ssl_server = SslServer("IPv4", "socket_tls", ciphersuite)
        test.profile = SocketProfile(test.dut, "0", connection.dstl_get_used_cid(),
                                host=test.ssl_server.dstl_get_server_ip_address(),
                                     port=test.ssl_server.dstl_get_server_port(),
                                protocol="tcp", secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, tls_version="1_1")
        test.sleep(2)

        test.log.step("9. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("10. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("11. Check if server response is correct.")
        test.profile.dstl_get_service().dstl_close_service_profile()
        test.server_response = test.ssh_server.last_response
        test.log.info(test.server_response)
        test.expect("TLS 1.1 Handshake" in test.server_response,
                    msg="wrong server response")


    def cleanup(test):
        test.log.step("12. Close socket profile.")
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.info("Object does not exist")

        try:
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.info("Object does not exist")

        try:
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
            test.expect(test.profile.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.info("Object does not exist")

        test.log.step("13. Remove certificates from module.")
        try:
            test.expect(test.certificates.dstl_delete_certificate("1"))
            test.expect(test.certificates.dstl_delete_certificate("0"))
        except AttributeError:
            test.log.info("Object does not exist")

if (__name__ == "__main__"):
    unicorn.main()
