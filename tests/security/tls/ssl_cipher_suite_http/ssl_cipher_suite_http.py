# responsible grzegorz.dziublinski@globallogic.com
# Wroclaw
# TC0103724.001, TC0103725.001, TC0092529.001, TC0092530.001, TC0092531.001, TC0092532.001,
# TC0092535.001, TC0092536.001, TC0092537.001, TC0092538.001, TC0092539.001, TC0092551.001,
# TC0092552.001, TC0092553.001, TC0092556.001


import unicorn
from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock


class Test(BaseTest):
    """
       TC intention: Testing if specified cipher suite is supported and accepted by module in HTTPS
       connection.
       Test script can be used with multiple Test Cases depending on used Cipher Suite as the
       parameter value.
       Args:
           cipher (String): Cipher Suite Name (in IANA notation) to be used.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

    def run(test):
        test.log.step("1. Run OpenSSL server with one cipher suite supported by module: {}.".
                      format(test.cipher))
        test.ssl_server = SslServer("IPv4", "http_tls", test.cipher)
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() > 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.expect(test.certificates.dstl_upload_openssl_certificates())

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time.")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services and activate Internet "
                      "service connection.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("6. Define HTTP get profile to openSSL server. Use https connection.")
        http_service = HttpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                   http_command="get", host=ip_address,
                                   port=test.ssl_server.dstl_get_server_port(),
                                   secure_connection=True)
        http_service.dstl_generate_address()
        test.expect(http_service.dstl_get_service().dstl_load_profile())

        test.log.step("7. Enable Security Option of IP service (secopt parameter).")
        http_service.dstl_set_secopt("1")
        test.expect(http_service.dstl_get_service().dstl_write_secopt())

        test.log.step("8. Open HTTP profile.")
        test.expect(http_service.dstl_get_service().dstl_open_service_profile())
        test.expect(http_service.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("9. Check if server response is correct.")
        sisr_response = http_service.dstl_get_service().dstl_read_return_data(1500, repetitions=3)
        test.expect(test.ssl_server.dstl_compare_cipher_suite(sisr_response),
                    msg="Incorrect server response!")

        test.log.step("10. Close HTTP profile.")
        test.expect(http_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Problem with join thread.")
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("11. Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                        msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


if __name__ == "__main__":
    unicorn.main()
