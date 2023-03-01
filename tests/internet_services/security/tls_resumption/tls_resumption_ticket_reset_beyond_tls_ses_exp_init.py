# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105117.001, TC0105117.002

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_remove_cipher_suites_file


class Test(BaseTest):
    """
    TC name:
    TlsResumptionTicket_reset_beyond_TlsSesExpInit

    Intention:
    To check correct connection resumption with TLS server using Ticket resumption option.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.log.step("1. Change Error Message Format with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Create TCP Client profile (connection to SSL server) with parameters:\n"
                        '- TlsSesTypeInit - all or "2", depending on product\n'
                        '- TlsSesExpInit - 40\n'
                        '- TlsSesPers - 1\n'
                        '- SecOpt - 0")\n')
        dstl_remove_cipher_suites_file(test.dut)
        test.ssl_server = SslServer("IPv4", "socket_tls", 'TLS_DHE_RSA_WITH_AES_128_CBC_SHA256',
                                    extended=True, naccept=0, timeout=360)
        host = test.ssl_server.dstl_get_server_ip_address()
        port = test.ssl_server.dstl_get_server_port()

        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.profile = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                     protocol="tcp", tls_ses_pers="1", tls_ses_type_init="all",
                                     host=host, port=port, secure_connection=True,
                                     tls_ses_exp_init="40", secopt="0")
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("3. Check defined profile AT^SISS.")
        dstl_check_siss_read_response(test.dut, [test.profile])
        dstl_execute_sips_command(test.dut, "all", "save")

        test.log.step("4. Start IP traffic tracing using Wireshark on server side.")
        test.ssh_server2 = test.ssh_server.clone()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration=5)
        test.log.info("no need for TCPDUMP, SSL server will inform if new session ticket was "
                      "issued")

        test.open_profile_and_check([5, 6, 7])

        test.log.step("8. Close service profile and reset module after a longer time than defined "
                      "in the parameter: TlsSesExpInit.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.sleep(45)
        dstl_restart(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("9. Restore defined profile.")
        dstl_execute_sips_command(test.dut, "all", "load")

        test.log.step("10. Check defined profile AT^SISS.")
        dstl_check_siss_read_response(test.dut, [test.profile])

        test.open_profile_and_check([11, 12, 13])

        test.log.step("14. Close profile.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("15. Stop Wireshark log and analyze traffic.")
        test.log.info("no need for TCPDUMP, SSL server will inform if new session ticket was "
                      "issued")
        test.ssl_server_thread.join()
        test.expect(test.ssh_server.last_response.count("NewSessionTicket") == 2)
        test.log.info(test.ssh_server.last_response.count("NewSessionTicket"))

    def cleanup(test):
        try:
            """test.tcp_dump_thread.join()"""
            test.ssl_server_thread.join()
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.info("Object ssl_server does not exist")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def open_profile_and_check(test, step_numbers):
        test.log.step("{}. Open defined profile and check if connection opened correctly."
                      .format(step_numbers[0]))
        test.sleep(3)
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("{}. Check service and socket state AT^SISO.".format(step_numbers[1]))
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)

        test.log.step("{}. Check service state AT^SISI=srvProfileId,2.".format(step_numbers[2]))
        test.expect('"ticket"' in test.profile.dstl_get_parser().dstl_get_resumption_information())


if __name__ == "__main__":
    unicorn.main()
