#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0095173.002
import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

        test.ssl_server = SslServer("IPv4", "http_tls", "TLS_DHE_RSA_WITH_AES_128_CBC_SHA")
        test.certificates = OpenSslCertificates(test.dut, 3)
        test.certificates.dstl_upload_openssl_certificates()

    def run(test):

        test.log.info("TC0095173.002 - Ssl_CievURC_WrongCert")

        test.log.step("1) Check certificates using AT^SBNR=”is_cert” command.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 3)

        test.log.step("2) Enable URCs displaying for Internet Service commands.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("3) Activate Error result decoding using AT+CMEE=2 command")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".OK.", wait_for="OK"))

        test.log.step("4) Enable URCs for SSL connection using AT^SIND=”is_cert”,1 command.")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"is_cert\",1", ".OK.", wait_for="OK"))

        test.log.step("5) Define PDP context and activate it using SICA command.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("6) Define HTTPS GET service profile to HTTPS server (or website)"
                      "with secOpt parameter set to: secOpt,\"1\".")
        srv_profile_id = "0"
        http_service = HttpProfile(test.dut, srv_profile_id, connection_setup_object.dstl_get_used_cid(),
                                   http_command="get", host=test.ssl_server.dstl_get_server_ip_address(),
                                   port=test.ssl_server.dstl_get_server_port(), secure_connection=True,
                                   secopt="1")
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.log.step("7) Open service profile.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)
        test.expect(http_service.dstl_get_service().dstl_open_service_profile())

        test.log.step("8) Check if URCs “+CIEV: is_cert …” appears during connection handshake.")
        test.expect(test.dut.at1.wait_for(".+CIEV: \"is_cert\"," + srv_profile_id + ",.", timeout=60))

        test.log.step("9) Check if ^SIS: Error with information that certificate does not fit appears.")
        test.expect(http_service.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="66",
                                                                    urc_info_text="Peer certificate is not confirmed"))

        test.log.step("10) Check profile state using AT^SISO? Command.")
        test.expect(http_service.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("11) Close service profile.")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):

        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")

        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("GenericIpServer was not created.")

        test.dut.at1.send_and_verify("AT^SIND=\"is_cert\",0", ".OK.", wait_for="OK")

        try:
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_openssl_certificates()
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError:
            test.log.error("InternetServicesCertificates was not created.")


if "__main__" == __name__:
    unicorn.main()