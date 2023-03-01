# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0103728.001, TC0103729.001, TC0103296.001, TC0103295.001, TC0103294.001, TC0103293.001,
# TC0103292.001,TC0103291.001, TC0095922.001, TC0095921.001, TC0095920.001, TC0095919.001,
# TC0095918.001, TC0095917.001, TC0095916.001, TC0095915.001, TC0095914.001, TC0095913.001,
# TC0095912.001, TC0095911.001, TC0095910.001, TC0095909.001, TC0095908.001, TC0095177.001,
# TC0095004.001, TC0095003.001, TC0095002.001, TC0095000.001,TC0094999.001, TC0094998.001,
# TC0094997.001, TC0094996.001, TC0094994.001, TC0094993.001, TC0094992.001, TC0094991.001,
# TC0094990.001, TC0094988.001, TC0094987.001, TC0094986.001, TC0094985.001, TC0094983.001,
# TC0094981.001, TC0094979.001, TC0094977.001, TC0094976.001, TC0094974.001, TC0094973.001,
# TC0094971.001, TC0094970.001, TC0094968.001, TC0094967.001, TC0094966.001, TC0094962.001,
# TC0094961.001, TC0094960.001, TC0094959.001, TC0094958.001, TC0094957.001, TC0094956.001,
# TC0094955.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       TC intention: Testing if specified cipher suite is supported and accepted by module in
       DTLS connection.
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
        test.ssl_server = SslServer("IPv4", "dtls", test.cipher)
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("2. Load client certificate and server public certificate on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_openssl_certificates()

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Set Real Time Clock to current time.")
        test.expect(dstl_set_real_time_clock(test.dut))

        test.log.step("5. Define PDP context for Internet services and activate Internet "
                      "service connection.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("6. Define UDP socket client profile to openSSL server. "
                      "Use sockudps connection.")
        test.profile = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                     protocol="udp", host=ip_address,
                                     port=test.ssl_server.dstl_get_server_port(),
                                     secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("7. Enable Security Option of IP service (secopt parameter).")
        test.profile.dstl_set_secopt("1")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())

        test.log.step("8. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("9. Check if server response is correct.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.expect(test.ssl_server.dstl_compare_cipher_suite(), msg="Incorrect server response!")

    def cleanup(test):
        test.log.step("10. Close socket profile.")
        try:
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")
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
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError:
            test.log.error("Certificate object was not created.")


if "__main__" == __name__:
    unicorn.main()
