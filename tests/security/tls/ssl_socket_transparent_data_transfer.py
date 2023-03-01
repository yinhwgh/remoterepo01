# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0087861.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_echo_server import SslEchoServer
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from os.path import join
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Check loadtest of datatransfer via SSL socket transparent connection."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(dstl_set_real_time_clock(test.dut))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        test.log.h2("Executing script for test case: 'TC0087861.001 "
                    "SSlSocketTransparentDataTransfer'")

        test.log.step("1. Define and activate PDP context / internet connection profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile(),
                    critical=True)

        test.log.step("2. Add client certificate and private key file at index 0")
        test.certificates = InternetServicesCertificates(test.dut)
        if test.certificates.dstl_count_uploaded_certificates() != 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates",
                                                                  "client.der"), join(
                                                    "openssl_certificates", "private_client_key"))

        test.log.step("3. Add server certificate on module")
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("echo_certificates",
                                                                             "client", "ca.der")))

        test.log.step("4. Check if certificates have been installed on module")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("5. Define transparent client profile with socktcps connection and server "
                      "certificate check parameter on.")
        test.ssl_echo_server = SslEchoServer("IPv4", "TCP", test_duration=10)
        test.socket_ssl = SocketProfile(test.dut, 2, connection_setup.dstl_get_used_cid(),
                                        protocol="tcp", secopt="1",  secure_connection=True,
                                        etx_char=26)
        test.socket_ssl.dstl_set_parameters_from_ip_server(test.ssl_echo_server)
        test.socket_ssl.dstl_generate_address()
        test.expect(test.socket_ssl.dstl_get_service().dstl_load_profile())

        iterations = 150
        for iteration in range(1, iterations + 1):
            test.log.step("6. Open socket profile and enter transparent mode "
                          "\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(test.socket_ssl.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_ssl.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
            test.sleep(2)
            test.expect(test.socket_ssl.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("7. Upload 50KB to server "
                          "\nIteration: {} of {}.".format(iteration, iterations))
            data = dstl_generate_data(1000)
            amount_of_sent_data = len(data) * 50
            test.expect(test.socket_ssl.dstl_get_service().dstl_send_data(data, expected="",
                                                                          repetitions=50,
                                                                          delay_in_ms=800))
            test.sleep(5)

            test.log.step("8. Compare sent/received data "
                          "\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26, time_out=60))

            test.sleep(10)
            test.expect(test.socket_ssl.dstl_get_parser().dstl_get_service_data_counter(
                "RX") == amount_of_sent_data)
            test.expect(test.socket_ssl.dstl_get_parser().dstl_get_service_data_counter(
                "TX") == amount_of_sent_data)

            test.log.step("9. Check client srv state "
                          "\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(test.socket_ssl.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.UP.value)
            test.expect(test.socket_ssl.dstl_get_parser().dstl_get_socket_state() ==
                        SocketState.CLIENT.value)

            test.log.step("10. Close the connection "
                          "\nIteration: {} of {}.".format(iteration, iterations))
            test.expect(test.socket_ssl.dstl_get_service().dstl_close_service_profile())

            test.log.step("11. Repeat steps 6-10 {} times.".format(iterations - iteration))

    def cleanup(test):
        try:
            test.log.step("12. Reset internet service profiles and remove certificates.")
            test.expect(test.socket_ssl.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_ssl.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")

        try:
            test.expect(test.certificates.dstl_delete_certificate(1))
            test.expect(test.certificates.dstl_delete_certificate(0))
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")

        try:
            if not test.ssl_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
