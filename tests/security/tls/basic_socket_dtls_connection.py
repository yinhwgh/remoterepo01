# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0102308.001

import unicorn
from re import search
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """ Intention: Check support of DTLS socket connection, and SIND: is_cert URC. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.h2("Executing script for test case: 'TC0102308.001 BasicSocketDTLSConnection'")
        test.log.step("1. Run OpenSSL server with cipher that module supports")
        test.ssl_server = SslServer("IPv4", "dtls", "DHE-RSA-AES128-SHA")
        ip_address=test.ssl_server.dstl_get_server_ip_address()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(3)

        test.log.step("2. Upload client and server public certificate.")
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
                                         host=ip_address,
                                         port=test.ssl_server.dstl_get_server_port(),
                                         secure_connection=True)
        test.socket_dtls.dstl_generate_address()
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())

        test.log.step("4. Enable Security Option of IP service (secopt parameter).")
        test.socket_dtls.dstl_set_secopt("1")
        test.expect(test.socket_dtls.dstl_get_service().dstl_write_secopt())

        test.log.step("5. Enable SIND: is_cert URC.")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"is_cert\",1", ".*OK.*"))

        test.log.step("6. Open connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("7. Check if SIND URC is correct.")
        test.expect(search("CIEV: (\")?is_cert(\")?,0,", test.dut.at1.last_response))

        test.log.step("8. Exchange data.")
        exchange_data_and_verify(test)

        test.log.step("9. Close connection.")
        test.log.info("Closing connection was done in previous step.")
        test.ssl_server_thread.join()
        test.sleep(5)

        test.log.step("10. Disable Security Option of IP service (secopt parameter).")
        test.socket_dtls.dstl_set_secopt("0")
        test.expect(test.socket_dtls.dstl_get_service().dstl_write_secopt())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("11. Open connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("12. Check if SIND URC is correct .")
        test.expect(search("CIEV: (\")?is_cert(\")?,0,", test.dut.at1.last_response))

        test.log.step("13. Exchange data.")
        exchange_data_and_verify(test)

        test.log.step("14. Close connection.")
        test.log.info("Closing connection was done in previous step.")
        test.ssl_server_thread.join()

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


def exchange_data_and_verify(test):
    data_to_send_from_client = dstl_generate_data(100)
    test.expect(test.socket_dtls.dstl_get_service().dstl_send_sisw_command(100))
    test.expect(test.socket_dtls.dstl_get_service().dstl_send_data(data_to_send_from_client))
    test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
    test.expect(data_to_send_from_client in test.ssh_server.last_response)


if "__main__" == __name__:
    unicorn.main()
