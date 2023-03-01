# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0087880.002

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from os.path import join
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles



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
        test.expect(test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates",
                                "client.der"), join("openssl_certificates", "private_client_key")))
        test.expect(test.certificates.dstl_upload_server_certificate(1, join("openssl_certificates",
                                                                "certificate_conf_5.der")))
        test.expect(test.certificates.dstl_upload_server_certificate(2, join("openssl_certificates",
                                                                "certificate_conf_6.der")))
        test.expect(test.certificates.dstl_upload_server_certificate(3, join("echo_certificates",
                                                                             "client", "ca.der")))

    def run(test):
        test.log.h2("Executing script for test case: 'TC0087880.002 BasicSSLSocketFunc'")

        test.log.step("1) Module attached to the network if not ready.")
        test.log.info("This will be done together with next step.")

        test.log.step("2) Configure bearer service.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Establish normal (non-secure socktcp) connection to SSL Server "
                      "(secOpt=0).")
        test.ssl_server_1 = SslServer("IPv4", "socket_tls", 'TLS_DHE_RSA_WITH_AES_128_CBC_SHA256')
        server_ip_address = test.ssl_server_1.dstl_get_server_ip_address()
        server_port = test.ssl_server_1.dstl_get_server_port()
        ssl_server_1_thread = test.thread(test.ssl_server_1.dstl_run_ssl_server)

        socket_service_1 = SocketProfile(test.dut, "1", connection_setup.dstl_get_used_cid(),
                                         host=server_ip_address, port=server_port,
                                         protocol="tcp", secopt='0')
        socket_service_1.dstl_generate_address()
        test.expect(socket_service_1.dstl_get_service().dstl_load_profile())

        test.expect(socket_service_1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_service_1.dstl_get_service().dstl_send_sisw_command_and_data(500))
        test.expect(socket_service_1.dstl_get_urc().dstl_is_sis_urc_appeared('0'))
        test.expect(socket_service_1.dstl_get_parser().dstl_get_service_state()
                    == ServiceState.DOWN.value)
        test.expect(socket_service_1.dstl_get_service().dstl_close_service_profile())
        ssl_server_1_thread.join()

        test.log.step("4) Establish SSL connection without certificate check (secOpt=0).")
        ssl_server_1_thread = test.thread(test.ssl_server_1.dstl_run_ssl_server)
        socket_service_1.dstl_set_secure_connection(True)
        socket_service_1.dstl_generate_address()
        test.expect(socket_service_1.dstl_get_service().dstl_load_profile())

        test.expect(socket_service_1.dstl_get_service().dstl_open_service_profile())
        test.check_data_transfer(socket_service_1, test.ssl_server_1, 'ssh_server')
        test.expect(socket_service_1.dstl_get_service().dstl_close_service_profile())
        ssl_server_1_thread.join()

        test.log.step("5) Establish SSL connection to server1 with ciphering SHA256 (secOpt=1).")
        ssl_server_1_thread = test.thread(test.ssl_server_1.dstl_run_ssl_server, configuration='5')

        socket_service_1.dstl_set_secopt('1')
        test.expect(socket_service_1.dstl_get_service().dstl_write_secopt())

        test.expect(socket_service_1.dstl_get_service().dstl_open_service_profile())
        test.check_data_transfer(socket_service_1, test.ssl_server_1, 'ssh_server')
        test.expect(socket_service_1.dstl_get_service().dstl_close_service_profile())
        ssl_server_1_thread.join()

        test.log.step("6) Establish SSL connection to Server2 with ciphering SHA1 (secOpt=1).")
        test.ssl_server_2 = SslServer("IPv4", "socket_tls", 'TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256')
        server_port = test.ssl_server_2.dstl_get_server_port()
        ssl_server_2_thread = test.thread(test.ssl_server_2.dstl_run_ssl_server, configuration='6')

        socket_service_2 = SocketProfile(test.dut, "2", connection_setup.dstl_get_used_cid(),
                                         host=server_ip_address, port=server_port,
                                         protocol="tcp", secure_connection=True, secopt='1')
        socket_service_2.dstl_generate_address()
        test.expect(socket_service_2.dstl_get_service().dstl_load_profile())

        test.expect(socket_service_2.dstl_get_service().dstl_open_service_profile())
        test.check_data_transfer(socket_service_2, test.ssl_server_2, 'ssh_server')
        test.expect(socket_service_2.dstl_get_service().dstl_close_service_profile())
        ssl_server_2_thread.join()

        test.log.step("7) Establish 2 SSL connection to both SSL server simultaneously.")
        ssl_server_1_thread = test.thread(test.ssl_server_1.dstl_run_ssl_server, configuration='5')
        ssl_server_2_thread = test.thread(test.ssl_server_2.dstl_run_ssl_server, configuration='6',
                                          ssh_server_property='ssh_server_2')

        test.expect(socket_service_1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_service_2.dstl_get_service().dstl_open_service_profile())
        test.check_data_transfer(socket_service_1, test.ssl_server_1, 'ssh_server')
        test.check_data_transfer(socket_service_2, test.ssl_server_2, 'ssh_server_2')

        test.log.step("8) Close connections")
        test.expect(socket_service_1.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_service_2.dstl_get_service().dstl_close_service_profile())
        ssl_server_1_thread.join()
        ssl_server_2_thread.join()
        test.expect(test.certificates.dstl_delete_certificate(3))
        test.expect(test.certificates.dstl_delete_certificate(2))
        test.expect(test.certificates.dstl_delete_certificate(1))
        test.expect(test.certificates.dstl_delete_certificate(0))

    def cleanup(test):
        try:
            if not test.ssl_server_1.dstl_server_close_port() \
                    or not test.ssl_server_2.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.certificates.dstl_delete_all_uploaded_certificates())
        except AttributeError:
            test.log.error("Certificate object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def check_data_transfer(test, socket_service, ssl_server, ssh_server):
        amount_of_data = 500
        data_to_send = dstl_generate_data(amount_of_data)
        test.expect(socket_service.dstl_get_service().dstl_send_sisw_command(amount_of_data))
        test.expect(socket_service.dstl_get_service().dstl_send_data(data_to_send))
        test.expect(data_to_send in
                    ssl_server.dstl_read_data_on_ssh_server(ssh_server_property=ssh_server))
        test.expect(socket_service.dstl_get_parser().dstl_get_service_state()
                    == ServiceState.UP.value)


if __name__ == "__main__":
    unicorn.main()
