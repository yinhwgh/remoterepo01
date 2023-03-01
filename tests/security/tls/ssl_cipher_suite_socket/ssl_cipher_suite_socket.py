# responsible grzegorz.dziublinski@globallogic.com
# location Wroclaw
# TC0092570.002, TC0092559.002, TC0095925.001, TC0095901.001, TC0095897.001, TC0095926.001,
# TC0095904.001, TC0095898.001, TC0095905.001, TC0095899.001, TC0095906.001, TC0095900.001,
# TC0095929.001, TC0095927.001, TC0095896.001, TC0095895.001, TC0092514.003, TC0092522.003,
# TC0092523.003, TC0092524.003, TC0092528.003, TC0092529.003, TC0092530.003, TC0092531.003,
# TC0092532.003, TC0092535.003, TC0092536.003, TC0092537.003, TC0092538.003, TC0092539.003,
# TC0092551.003, TC0092552.003, TC0092553.003, TC0092556.003, TC0092557.003, TC0092558.003,
# TC0092559.003, TC0092560.003, TC0092561.003, TC0092562.003, TC0092563.003, TC0092565.003,
# TC0092566.003, TC0092567.003, TC0092568.003, TC0092569.003, TC0092570.003, TC0095895.002,
# TC0095896.002, TC0095897.002, TC0095898.002, TC0095899.002, TC0095900.002, TC0095901.002,
# TC0095904.002, TC0095905.002, TC0095906.002, TC0095925.002, TC0095926.002, TC0095927.002,
# TC0104384.002, TC0104385.002, TC0104386.002, TC0104387.002, TC0104388.002


import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock

class Test(BaseTest):
    """
       TC intention: Testing if specified cipher suite is supported and accepted by module in
       TLS connection.
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
        test.ssl_server = SslServer("IPv4", "socket_tls", test.cipher)
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() > 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_openssl_certificates()

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time.")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("6. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection(),
                    msg="Could not activate PDP context")

        test.log.step("7. Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection.")
        socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                       host=ip_address,
                                       port=test.ssl_server.dstl_get_server_port(),
                                       protocol="tcp", secure_connection=True)
        socket_service.dstl_generate_address()
        test.expect(socket_service.dstl_get_service().dstl_load_profile())

        test.log.step("8. Enable Security Option of IP service (secopt parameter).")
        socket_service.dstl_set_secopt("1")
        test.expect(socket_service.dstl_get_service().dstl_write_secopt())

        test.log.step("9. Open socket profile.")
        test.expect(socket_service.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
        ssl_server_thread.join()

        test.log.step("10. Check if server response is correct.")
        test.expect(test.ssl_server.dstl_compare_cipher_suite(), msg="Incorrect server response!")

        test.log.step("11. Close socket profile.")
        test.expect(socket_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("12. Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


if __name__ == "__main__":
    unicorn.main()
