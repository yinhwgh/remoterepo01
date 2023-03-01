#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093957.001, TC0093957.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.generate_data import dstl_generate_data
from os.path import join


class Test(BaseTest):
    """ Intention: Check Socket TCP secure connection with/without client authentication check and with/without server
    authentication check using correct (matching) and incorrect certificates."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))

    def run(test):
        test.log.h2("Executing script for test case: 'TC0093957.001/002 BasicSocketServerSecureConnection'")

        test.log.step("1. Switch on server certificate notification")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"is_cert\",1", ".*OK.*"))

        test.log.step("2. Attach module to network")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("3. Define PDP context (+ internet connection profile if required) and activate it.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4. Check if any certificates are installed on module and if so, remove all")
        test.certificates = InternetServicesCertificates(test.dut)
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.log.step("5. Add client certificate and private key file at index 0")
        test.certificates.dstl_set_security_private_key("SHA1_RSA", "client", "pwdclient", join("echo_certificates", "client",
                                                                                                "client.ks"), "pwdclient")
        test.expect(test.certificates.dstl_upload_certificate_at_index_0(join("echo_certificates", "client", "client.der"),
                                                             join("echo_certificates", "client", "client_priv.der")))

        test.log.step("[TLSServer1] Connection without client authentication/with server authentication")
        test.log.step("6. Install server certificate 1 on module")
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates", "client", "ca.der")))

        test.log.step("7. Check if certificates have been installed on module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("8. Define socktcps connection [TLSServer1] with server certificate check parameter on.")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP")
        test.socket_dtls = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), protocol="tcp",
                                         secopt="1", host=test.ssl_echo_server.dstl_get_server_ip_address(),
                                         port=test.ssl_echo_server.dstl_get_server_port(), secure_connection=True)
        test.socket_dtls.dstl_generate_address()
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())

        test.log.step("9. Open socket profile")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("10. Send some data from module to server and read echoed data.")
        exchange_data_and_verify(test)

        test.log.step("11. Close connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
        test.expect(test.ssl_echo_server.dstl_server_close_port())

        test.log.step("[TLSServer2] Connection with client and server authentication")
        test.log.step("12. Define socktcps connection [TLSServer2] with server certificate check parameter on.")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP", check_client_certificate=True)
        test.socket_dtls.dstl_set_port(test.ssl_echo_server.dstl_get_server_port())
        test.socket_dtls.dstl_generate_address()
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())

        test.log.step("13. Open socket profile")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("14. Send some data from module to server and read echoed data.")
        exchange_data_and_verify(test)

        test.log.step("15. Close connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())

        test.log.step("[TLSServer2] Connection with client authentication/without server authentication")
        test.log.step("16. Set server certificate check parameter to 0 (off).")
        test.socket_dtls.dstl_set_secopt("0")
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())

        test.log.step("17. Open socket profile")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("18. Send some data from module to server and read echoed data.")
        exchange_data_and_verify(test)

        test.log.step("19. Close connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())

        test.log.step("[TLSServer2] Connection with client authentication/without server authentication and wrong "
                      "server certificate uploaded on module")
        test.log.step("20. Delete currently installed server certificate from module.")
        test.expect(test.certificates.dstl_delete_certificate(1))

        test.log.step("21. Install server certificate 2 on module")
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates", "client", "ca_4096.der")))

        test.log.step("22. Check if certificate has been installed on module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("23. Open socket profile")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=90))

        test.log.step("24. Send some data from module to server and read echoed data.")
        exchange_data_and_verify(test)

        test.log.step("25. Close connection.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())

        test.log.step("[TLSServer2] Connection with client and server authentication, and wrong server certificate "
                      "uploaded on module")
        test.log.step("26. Set server certificate check parameter to 1 (on).")
        test.socket_dtls.dstl_set_secopt("1")
        test.expect(test.socket_dtls.dstl_get_service().dstl_load_profile())

        test.log.step("27. Open socket profile")
        test.expect(test.socket_dtls.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        if test.dut.project == ('VIPER'):
            test.socket_dtls.dstl_get_urc().dstl_is_sis_urc_appeared("0", "66", '"Peer certificate is not confirmed"')
        else:
            test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sis_urc_appeared
                                                                    ("0", "77", '"The certificate does not exist"'))

        test.log.step("28. Delete all certificates")
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_delete_certificate(0))
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.log.step("29. Reset connection profile.")
        test.expect(test.socket_dtls.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dtls.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        try:
            if not test.ssl_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            if test.certificates.dstl_count_uploaded_certificates() != 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()
        except AttributeError:
            test.log.error("Certificate object was not created.")

def exchange_data_and_verify(test):
    data_to_send_from_client = dstl_generate_data(100)
    if test.expect(test.socket_dtls.dstl_get_service().dstl_send_sisw_command(100)):
        test.expect(test.socket_dtls.dstl_get_service().dstl_send_data(data_to_send_from_client))
    test.expect(test.socket_dtls.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
    data_read = test.socket_dtls.dstl_get_service().dstl_read_return_data(100)
    test.expect(data_read == data_to_send_from_client, msg="Data read from server is not equal data sent")


if "__main__" == __name__:
    unicorn.main()
