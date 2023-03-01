# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0102301.002, TC0102301.003
import unicorn
from core.basetest import BaseTest
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Short description:
       Testing if  TLSv1 protocol version connection is not possible during TLS connection.

       Detailed description:
       1. Run OpenSSL server using TLSv1
       2. Load client certificate and server public certificate (micCert.der) on module
       3. Check if certificates are installed
       4. Set Real Time Clock to current time
       5. Define PDP context for Internet services
       6. Activate Internet service connection
       7. Set Tcp/TLS/Version to:
            - for "TLS_min_version" to "MIN"
            - for "TLS_max_version" to 1.2
       8. Define TCP socket client profile to openSSL server. Use socktcps connection
       9. Enable Security Option of IP service (secopt parameter)
       10. Open socket profile, check socket state
       11. Check if server response is correct
       12. Close socket profile
       13. Remove certificates from module
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):

        test.log.info("Starting TS for TC0102301.002,003 - CheckingSupportOfTLSv1UsingTLS")

        test.log.step("1) Run OpenSSL server using TLSv1")
        test.ssl_server = SslServer("IPv4", "socket_tls", "DHE-RSA-AES128-SHA")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        test.expect(test.certificates)

        test.log.step("2) Load client certificate and server public certificate "
                      "(micCert.der) on module")
        test.certificates.dstl_upload_openssl_certificates()

        test.log.step("3) Check if certificates are installed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("4) Set Real Time Clock to current time")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5) Define PDP context for Internet services")
        test.connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_object.
                    dstl_load_and_activate_internet_connection_profile())

        test.log.step("6) Activate Internet service connection")
        test.log.info("Performed during test step 5")

        test.log.step("7) Set Tcp/TLS/Version to: \n"
                      +"- for \"TLS_min_version\" to \"MIN\" \n"
                      +"- for \"TLS_max_version\" to 1.2")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "1.2"))

        test.log.step("8) Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection")
        test.socket_service = SocketProfile(test.dut, 0, test.connection_setup_object.dstl_get_used_cid(),
                                            secure_connection=True, secopt="1")
        test.socket_service.dstl_set_parameters_from_ip_server(test.ssl_server)
        test.socket_service.dstl_generate_address()
        test.expect(test.socket_service.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, tls_version="1")
        test.sleep(2)

        test.log.step("9) Enable Security Option of IP service (secopt parameter)")
        test.log.info("Security Option of IP service has enabled during 8 test step")

        test.log.step("10) Open socket profile, check socket state")
        test.expect(test.socket_service.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.sleep(3)
        test.expect(test.socket_service.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0",
                                                                                urc_info_id="62"))
        test.expect(test.socket_service.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("11) Check if server response is correct")
        test.sleep(20)
        test.expect("ERROR" in test.ssh_server.last_response,
                    msg="Incorrect or missing \"ERROR\" in server response!")

        test.log.step("12) Close connection")
        test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())

        test.log.step("13) Remove certificates from module")
        test.certificates.dstl_delete_openssl_certificates()

        test.log.info("Check if certificates are removed")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

    def cleanup(test):
        try:
            test.ssl_server_thread.join()
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX")

            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()

        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()