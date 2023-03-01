# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102306.002

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
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC name:
    TC0102306.002 - CheckingSupportOfDTLSv1UsingDTLS

    Intention:
    Testing if DTLSv1 protocol version connection is not possible during DTLS connection

    description:
    1. Run OpenSSL server using DTLSv1:
    s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem -key mic.pem -keyform pem -dtls1 -brief
    2. Load client certificate and server public certificate (micCert.der) on module.
    Path to certificate: \\view\\aktuell\\z_pegasus_swt\\plugins\\com.cinterion.pegasus.testprocedure\\src
    \\pegasus\\testProcedure\\network\\wm\\st\\func\\ipnet\\SSLcertFiles\\OpenSSLFiles
    3. Check if certificates are installed
    4. Set Real Time Clock to current time
    5. Define PDP context for Internet services.
    6. Activate Internet service connection.
    7. Set Tcp/TLS/Version to:
    - for "TLS_min_version" to "MIN"
    - for "TLS_max_version" to 1.2
    8. Define UDP socket client profile to openSSL server. Use sockudps connection.
    9. Enable Security Option of IP service (secopt parameter).
    10. Open socket profile.
    11. Check if server response is correct.
    12. Close socket profile.
    13. Remove certificates from module
    """


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):

        test.log.step("1. Run OpenSSL server using DTLSv1:")
        ciphersuite = "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
        test.ssl_server = SslServer("IPv4", "dtls", ciphersuite)
        if not test.ssl_server:
            test.expect(False, True, msg="ssl_server did not start correctly")
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, tls_version="1")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates:
            test.expect(False, True, msg="problem with certificates")

        test.log.step("2. Load client certificate and server public certificate (micCert.der) "
                      "on module.")
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

        test.log.step("7. Set Tcp/TLS/Version to: \n"
                      "- for \"TLS_min_version\" to \"MIN\"\n"
                      "- for \"TLS_max_version\" to \"1.2\"\")")

        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "1.2"))

        test.log.step("8. Define UDP socket client profile to openSSL server. "
                      "Use sockudps connection.")
        test.profile = SocketProfile(test.dut, "0", connection.dstl_get_used_cid(),
                                host=ip_address, port=test.ssl_server.dstl_get_server_port(),
                                protocol="udp", secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("9. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("10. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared())

        test.log.step("11. Check if server response is correct.")
        test.log.info(test.ssh_server.last_response)
        test.expect("ERROR" in test.ssh_server.last_response,
                    msg="wrong server response")

    def cleanup(test):
        test.log.step("12. Close socket profile.")
        test.ssl_server.dstl_server_close_port()
        test.ssl_server_thread.join()
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("13. Remove certificates from module.")
        test.certificates.dstl_delete_certificate("1")
        test.certificates.dstl_delete_certificate("0")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")


if "__main__" == __name__:
    unicorn.main()
