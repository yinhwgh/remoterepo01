#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0103710.001, TC0103710.002

import unicorn
from os.path import join
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Validate client authentication functionality in TLS connection
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_bootloader(test.dut)
        test.log.info("Preparation before executing TS (preconditions) ")
        test.dut.at1.send("at^sbnw=\"ciphersuites\",0")
        test.expect(dstl_set_real_time_clock(test.dut))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"is_cert\",1", ".OK.", wait_for="OK"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0103710.001/002 SSLClientAuthentication'")
        test.log.step("1. Define and activate PDP context / internet connection profile.")
        connection_profile = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_profile.dstl_load_and_activate_internet_connection_profile())
        cid = connection_profile.dstl_get_used_cid()

        test.log.step("2. Add client certificate no.1 and private key file at index 0")
        test.certificates = InternetServicesCertificates(test.dut)
        test.cert_file = join(test.certificates.certificates_path, "echo_certificates", "client", "client.der")
        test.key_file = join(test.certificates.certificates_path, "echo_certificates", "client", "client_priv.pem")
        test.certificates.dstl_upload_certificate_at_index_0(test.cert_file, test.key_file)

        test.log.step("3. Check if certificate has been installed on module")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Define transparent client profile with socktcps connection to echo server and server"
                      " certificate check parameter set to off (0).")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP", check_client_certificate=True)
        test.socket_tls = SocketProfile(test.dut, 0, cid, protocol="tcp", secopt="0",
                                        host=test.ssl_echo_server.dstl_get_server_FQDN(),
                                        port=test.ssl_echo_server.dstl_get_server_port(), secure_connection=True)
        test.socket_tls.dstl_generate_address()
        test.expect(test.socket_tls.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open socket profile")
        test.expect(test.socket_tls.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_tls.dstl_get_urc().dstl_is_sisw_urc_appeared(1, timeout=60))

        test.log.step("6. Send some data from module to server and read echoed data")
        exchange_data_and_verify(test)

        test.log.step("7. Compare sent/received data")
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_data_counter("tx") == 900)
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_data_counter("rx") == 900)

        test.log.step("8. Check client srv state")
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.UP.value)
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_socket_state(at_command=Command.SISO_WRITE)
                    == SocketState.CLIENT.value)

        test.log.step("9. Close socket.")
        test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Add client certificate no.2 and private key file at index 0")
        test.expect(test.certificates.dstl_delete_certificate(0))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")
        test.cert_file2 = join(test.certificates.certificates_path, "openssl_certificates", "client.der")
        test.key_file2 = join(test.certificates.certificates_path, "openssl_certificates", "private_client_key")
        test.certificates.dstl_upload_certificate_at_index_0(test.cert_file2, test.key_file2)

        test.log.step("11. Check if certificate has been installed on module")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                    msg="Wrong amount of certificates installed")

        test.log.step("12. Open socket profile.")
        test.expect(test.socket_tls.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.socket_tls.dstl_get_urc().dstl_is_sis_urc_appeared
                    (urc_cause="0", urc_info_id=".*", urc_info_text=".*error"))
        test.sleep(5)
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.DOWN.value)

        test.log.step("13. Close socket.")
        test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())

        test.log.step("14. Remove client certificate and private key.")
        test.expect(test.certificates.dstl_delete_certificate(0))

        test.log.step("15. Check if certificate has been removed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")

        test.log.step("16. Open socket profile.")
        test.expect(test.socket_tls.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.socket_tls.dstl_get_urc().dstl_is_sis_urc_appeared
                    (urc_cause="0", urc_info_id=".*", urc_info_text=".*error"))
        test.sleep(5)
        test.expect(test.socket_tls.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.DOWN.value)

    def cleanup(test):
        try:
            if not test.ssl_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")
        test.log.step("17. Close and reset internet service profile.")
        test.expect(test.socket_tls.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_tls.dstl_get_service().dstl_reset_service_profile())


def exchange_data_and_verify(test):
    data_to_send_from_client = dstl_generate_data(900)
    if test.expect(test.socket_tls.dstl_get_service().dstl_send_sisw_command(900)):
        test.expect(test.socket_tls.dstl_get_service().dstl_send_data(data_to_send_from_client))
    test.expect(test.socket_tls.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
    data_read = test.socket_tls.dstl_get_service().dstl_read_return_data(900)
    test.expect(data_read == data_to_send_from_client, msg="Data read from server is not equal data sent")


if "__main__" == __name__:
    unicorn.main()
