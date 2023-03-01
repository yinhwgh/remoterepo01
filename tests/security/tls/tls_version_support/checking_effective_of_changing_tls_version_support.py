# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0107586.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import SocketState, ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
        To check if changing TLS versions on module is effective immediately.
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_reset_internet_service_profiles(test.dut))

    def run(test):
        test.log.step("1. Run OpenSSL server using TLS1_3 param. "
                      "s_server -accept 50303 -state -naccept 1 -cert micCert.pem -certform pem "
                      "-key mic.pem -keyform pem -msg -tls1_3")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_AES_128_GCM_SHA256")

        test.log.step("2. Define and activate PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Set TCP/IP URC in scfg.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("4. Set Tcp/TLS/Version to:\
        - for \"TLS_min_version\" to \"MIN\"\
        - for \"TLS_max_version\" to \"MAX\"")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))

        test.log.step("5. Define TCP socket client profile to openSSL server. Use socktcps "
                      "connection (secopt 0).")
        test.profile = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                     protocol="tcp",
                                     host=test.ssl_server.dstl_get_server_ip_address(),
                                     port=test.ssl_server.dstl_get_server_port(),
                                     secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())
        test.profile.dstl_set_secopt("0")
        test.expect(test.profile.dstl_get_service().dstl_write_secopt())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)

        test.log.step("6. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.sleep(10)

        test.log.step("7. Send some data to server.")
        test.exchange_data_and_verify()

        test.log.step("8. Check if data on server were received")
        test.log.info("Will bo done in step 10")

        test.log.step("9. Check socket and service states")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)

        test.log.step("10. Close socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.expect(test.data_to_send_from_client in test.ssh_server.last_response)

        test.ssl_server_thread.join()

        test.log.step("11. Set Tcp/TLS/Version to:\
        - for \"TLS_min_version\" to \"MIN\"\
        - for \"TLS_max_version\" to \"1.2\"")
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "1.2"))

        test.log.step("12. Run OpenSSL server using TLS1_3 param.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)

        test.log.step("13. Open socket profile.")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))
        test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.sleep(5)

        test.log.step("14. Check socket and service states")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.
                    value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.
                    value)

    def cleanup(test):
        try:
            test.log.step("15. Close socket profile and delete profile.")
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
            test.expect(test.profile.dstl_get_service().dstl_reset_service_profile())
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Object was not created.")
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX")

    def exchange_data_and_verify(test):
        test.data_to_send_from_client = dstl_generate_data(100)
        if test.expect(test.profile.dstl_get_service().dstl_send_sisw_command(100)):
            test.expect(test.profile.dstl_get_service().dstl_send_data(
                test.data_to_send_from_client))
            test.sleep(10)

if "__main__" == __name__:
    unicorn.main()
