# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0087881.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from os.path import join
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.internet_service.get_internet_service_error_report import dstl_get_internet_service_error_report


class Test(BaseTest):
    """ Check parameter secOpt for manage certificates """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.certificates = InternetServicesCertificates(test.dut)
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)
        test.expect(test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates",
                                "client.der"), join("openssl_certificates", "private_client_key")))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("openssl_certificates",
                                                                "certificate_conf_5.der")))
        test.expect(test.certificates.dstl_upload_server_certificate(2, join("openssl_certificates",
                                                                "certificate_conf_6.der")))
        test.expect(test.certificates.dstl_upload_server_certificate(3, join("echo_certificates",
                                                                             "client", "ca.der")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 4)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0087881.002 BasicSSLHttpsFunc'")

        test.log.step("1) Module attached to the network if not ready.")
        test.log.info("This will be done together with next step.")

        test.log.step("2) Configure bearer service.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Establish http (instead of https) connection to SSLHttpServer")
        test.ssl_server = SslServer("IPv4", "http_tls", 'TLS_DHE_RSA_WITH_AES_128_CBC_SHA256')
        server_ip_address = test.ssl_server.dstl_get_server_ip_address()
        server_port = test.ssl_server.dstl_get_server_port()
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.srv_id = '1'
        http_service = HttpProfile(test.dut, test.srv_id, connection_setup.dstl_get_used_cid(),
                                   host=server_ip_address, port=server_port, secopt='0',
                                   http_command='get')
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.expect(http_service.dstl_get_service()
                    .dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(http_service.dstl_get_urc()
                    .dstl_is_sis_urc_appeared('0', '15', '"Remote host has reset the connection"'))
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())
        ssl_server_thread.join()

        test.log.step("4) Establish https connection to SSLHttpServer; secOpt=0")
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        http_service.dstl_set_secure_connection(True)
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.expect(http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())
        ssl_server_thread.join()

        test.log.step("5) Establish https connection to SSLHttpServer; secOpt=1")
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration='5')

        http_service.dstl_set_secopt('1')
        test.expect(http_service.dstl_get_service().dstl_write_secopt())

        test.expect(http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())
        ssl_server_thread.join()

        test.log.step("6) Delete certificate at index 1 and 2.")
        test.expect(test.certificates.dstl_delete_certificate(2))
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("7) Establish https connection to SSLHttpServer; secOpt=1")
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration='5')

        test.expect(http_service.dstl_get_service()
                    .dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(http_service.dstl_get_urc()
                    .dstl_is_sis_urc_appeared('0', '76', '"Certificate format error"'))

        test.log.step("8) Check state and if error occurred check error code with at^sise")
        test.expect(http_service.dstl_get_parser().dstl_get_service_state()
                    == ServiceState.DOWN.value)
        test.expect(['76', 'Certificate format error']
                    == dstl_get_internet_service_error_report(test.dut, test.srv_id))

        test.log.step("9) Close connection")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())
        ssl_server_thread.join()
        test.expect(test.certificates.dstl_delete_certificate(3))
        test.expect(test.certificates.dstl_delete_certificate(0))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.certificates.dstl_delete_all_uploaded_certificates())
        except AttributeError:
            test.log.error("Certificate object was not created.")
        dstl_reset_internet_service_profiles(test.dut, profile_id=test.srv_id,
                                             force_reset=True)


if __name__ == "__main__":
    unicorn.main()
