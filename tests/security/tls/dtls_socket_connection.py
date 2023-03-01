# responsible: lukasz.lidzba@globallogic.com
# location: Wroclaw
# TC0094328.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.generate_data import dstl_generate_data
from os.path import join


class Test(BaseTest):
    """ Testing the support of DTLS socket connections with different keysizes. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_real_time_clock(test.dut))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.secopt_disabled = "0"
        test.secopt_enabled = "1"

    def run(test):
        test.log.step("1. Run OpenSSL server with certificate -2048 bit key, e.g: openssl s_server "
                      "-accept 50457 -state -naccept 1 -cipher DHE-RSA-AES128-SHA -cert "
                      "/opt/openssl/CertificatesConfig1/micCert.pem -certform pem -key "
                      "/opt/openssl/CertificatesConfig1/mic.pem -keyform pem -dtls1_2")
        test.ssl_server = SslServer("IPv4", "dtls", "DHE-RSA-AES128-SHA")
        test.ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.sleep(3)

        test.log.step("2. Load client certificate and server public certificate on module "
                      "(2048 bit key).")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()
        test.expect(test.certificates.dstl_upload_openssl_certificates())
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed.")

        test.log.step("3. Define UDP socket client socket_dtls to openSSL server. Use sockudps "
                      "connection.")
        test.socket_dtls = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                         protocol="udp",
                                         host=test.ip_address,
                                         port=test.ssl_server.dstl_get_server_port(),
                                         secure_connection=True)
        test.socket_dtls.dstl_generate_address()
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.steps_3_to_7(test.secopt_enabled)

        test.log.step("8. Run OpenSSL server with certificate -4096 bit key, e.g: openssl s_server "
                      "-accept 50456 -state -naccept 1 -cipher NULL-SHA -cert "
                      "/opt/openssl/CertificatesConfig1_4096/micCert.pem -certform pem -key "
                      "/opt/openssl/CertificatesConfig1_4096/mic.pem -keyform pem -dtls1_2")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="5")

        test.log.step("9. Install new server certificate (4096 bit key).")
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates",
                                                                             "client",
                                                                             "ca_4096.der")))
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                    msg="Wrong amount of certificates installed.")

        test.log.step("10. Repeat steps 3-7.")
        test.steps_3_to_7(test.secopt_enabled)

        test.log.step("11. Repeat steps 3-7 but disable secopt parameter.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="5")
        test.steps_3_to_7(test.secopt_disabled)

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)
        except AttributeError:
            test.log.error("Certificate object was not created.")
        try:
            test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dtls.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Service profile could not be closed.")

    def exchange_data_and_verify(test):
        data_to_send_from_client = dstl_generate_data(100)
        test.expect(test.socket_dtls.dstl_get_service().dstl_send_sisw_command(100))
        test.expect(test.socket_dtls.dstl_get_service().dstl_send_data(data_to_send_from_client))
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
        test.expect(data_to_send_from_client in test.ssh_server.last_response)

    def steps_3_to_7(test, secopt):
        test.log.step("3. Define UDP socket client socket_dtls to openSSL server. Use sockudps "
                      "connection.")
        test.log.info("Executed in first iteration.")

        test.log.step("4. Enable Security Option of IP service (secopt parameter).")
        test.socket_dtls.dstl_set_secopt(secopt)
        test.expect(test.socket_dtls.dstl_get_service().dstl_write_secopt())

        test.log.step("5. Open connection")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("6. Exchange data with server")
        test.exchange_data_and_verify()

        test.log.step("7. Close connection.")
        test.log.info("Closing connection was done in previous step.")
        test.ssl_server_thread.join()
        test.sleep(5)


if "__main__" == __name__:
    unicorn.main()
