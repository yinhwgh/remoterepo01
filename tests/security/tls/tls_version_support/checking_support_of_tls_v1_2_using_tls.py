#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0102303.001
import unicorn
from core.basetest import BaseTest
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Intention: Testing if  TLS1.2 protocol version is used during TLS connection"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.info("TC0102303.001 - CheckingSupportOfTLSv1_2UsingTLS")

        test.log.step("1) Run OpenSSL server using TLSv1.2")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_RSA_WITH_AES_128_CBC_SHA256")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.dstl_get_openssl_configuration_number())

        test.log.step("2) Load client certificate and server public certificate (micCert.der) on module")
        test.expect(test.certificates.dstl_upload_openssl_certificates())

        test.log.step("3) Check if certificates are installed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("4) Set Real Time Clock to current time")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5) Define PDP context for Internet services")
        test.connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_object.dstl_load_internet_connection_profile())

        test.log.step("6) Activate Internet service connection")
        test.expect(test.connection_setup_object.dstl_activate_internet_connection())

        test.log.step("7) Set Tcp/TLS/Version to: \n"
                      +"- for \"TLS_min_version\" to \"1.2\" \n"
                      +"- for \"TLS_max_version\" to MAX")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.2", "MAX"))

        test.log.step("8) Define TCP socket client profile to openSSL server. Use socktcps connection")
        test.socket_service = SocketProfile(test.dut, 0, test.connection_setup_object.dstl_get_used_cid(),
                                            secure_connection=True)
        test.socket_service.dstl_set_parameters_from_ip_server(test.ssl_server)
        test.socket_service.dstl_generate_address()
        test.expect(test.socket_service.dstl_get_service().dstl_load_profile())

        test.log.step("9) Enable Security Option of IP service (secopt parameter)")
        test.socket_service.dstl_set_secopt(1)
        test.expect(test.socket_service.dstl_get_service().dstl_write_secopt())

        test.log.step("10) Open socket profile")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)
        test.expect(test.socket_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("11) Check if server response is correct")
        test.expect("TLS 1.2 Handshake" in test.ssh_server.last_response,
                    msg="Incorrect or missing \"TLS 1.2 Handshake\" in server response!")

        test.log.step("12) Close connection")
        test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("13) Remove certificates from module")
        test.certificates.dstl_delete_openssl_certificates()

        test.log.info("Check if certificates are removed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

    def cleanup(test):
        dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX")

        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")

        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("GenericIpServer was not created.")

        try:
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_openssl_certificates()
        except AttributeError:
            test.log.error("InternetServicesCertificates was not created.")


if "__main__" == __name__:
    unicorn.main()