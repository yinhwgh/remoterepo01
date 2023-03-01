# responsible dominik.tanderys@globallogic.com
# Wroclaw
# TC0102316.002

import unicorn

from os.path import join
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version


class Test(BaseTest):
    """
    TC name:
    CheckingDifferentTLS_VerUsingTLS

    Intention:
    Testing if TLS connection can be established when on module and on server different
    TLS versions can be accepted.

    description:
    1. Run OpenSSL server using TLS1_2 param:
    s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem -key mic.pem
    -keyform pem -msg -tls1_2
    Path to certificates: \\view\aktuell\z_pegasus_swt\plugins\com.cinterion.pegasus.
    testprocedure\src\
    pegasus\testProcedure\network\wm\st\func\ipnet\SSLcertFiles\OpenSSLFiles\ServerConfigCerts
    2. Load client certificate and server public certificate (micCert.der) on module.
    Path to certificate: \\view\aktuell\z_pegasus_swt\plugins\com.cinterion.pegasus.
    testprocedure\src\
    pegasus\testProcedure\network\wm\st\func\ipnet\SSLcertFiles\OpenSSLFiles
    3. Check if certificates are installed
    4. Set Real Time Clock to current time
    5. Define PDP context for Internet services.
    6. Activate Internet service connection.
    7. Set Tcp/TLS/Version to:
    - for "TLS_min_version" to "MIN"
    - for "TLS_max_version" to "1.1"
    8. Define TCP socket client profile to openSSL server. Use socktcps connection.
    9. Enable Security Option of IP service (secopt parameter).
    10. Open socket profile.
    11. Check if server response is correct.
    12. Close socket profile.
    13. Remove certificates from module.
    """


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))

    def run(test):

        test.log.step("1. Run OpenSSL server using TLS1_3 param")

        test.log.info("Openssl is run in later step")

        ciphersuite = "TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8"

        test.log.step("2. Load client certificate and server public certificate (micCert.der) "
                      "on module.")
        test.certificates = InternetServicesCertificates(test.dut)

        if test.certificates.dstl_count_uploaded_certificates() is not 0:
            test.certificates.dstl_delete_all_uploaded_certificates()

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
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, tls_version="1_3")

        test.profile = SocketProfile(test.dut, "0", connection.dstl_get_used_cid(),
                                host=ip_address, port=test.ssl_server.dstl_get_server_port(),
                                protocol="tcp", secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("9. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("10. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.sleep(5)

        test.log.step("11. Check if server response is correct.")
        test.server_response = test.ssh_server.last_response
        test.log.info(test.server_response)
        test.expect(("TLS 1.3" in test.server_response) and ("fatal protocol_version" in
                                                             test.server_response),
                    msg="wrong server response")

    def cleanup(test):
        test.log.step("12. Close socket profile.")
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Server object was not created.")

        try:
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

        try:
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Profile object was not created.")

        test.log.step("13. Remove certificates from module.")
        try:
            test.expect(test.certificates.dstl_delete_certificate("1"))
            test.expect(test.certificates.dstl_delete_certificate("0"))
        except AttributeError:
            test.log.error("Certificates object was not created.")



if (__name__ == "__main__"):
    unicorn.main()