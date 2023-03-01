# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102359.001, TC0102359.002

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
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_remove_cipher_suites_file


class Test(BaseTest):
    """
    TC name:
    TlsResumptionSessionId_basic

    Intention:
    	To check correct connection resumption with TLS server using Session ID parameter.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.log.step("1. Change Error Message Format with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Create TCP Client profile (connection to SSL server) with parameters:\n"
                        '- TlsSesTypeInit - sesid or "1", depending on product\n'
                        '- TlsSesExpInit - 120\n'
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
                                     protocol="tcp", tls_ses_pers="1", tls_ses_type_init="sesid",
                                     host=host, port=port, secure_connection=True,
                                     tls_ses_exp_init="120", secopt="0")
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("3. Check defined profile AT^SISS.")
        dstl_check_siss_read_response(test.dut, [test.profile])

        test.log.step("4. Start IP traffic tracing using Wireshark on server side.")
        test.ssh_server2 = test.ssh_server.clone()
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration=5)
        test.log.info("no need for TCPDUMP, SSL server will inform if new session ticket was "
                      "issued")

        test.open_profile_and_check([5, 6, 7])

        test.log.step("8 Close connection")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("9 Reopen connection before session expires.")
        test.open_profile_and_check([9, 10, 11])

        test.log.step("10 Close connection")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("11 Wait till session expires.")
        test.sleep(130)

        test.open_profile_and_check([12, 13, 14])

        test.log.step("15 Close profile.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()

        test.log.step("16 Stop Wireshark log and analyze traffic.")
        test.log.info("server response will be checked instead of wireshark log")
        test.expect(test.ssh_server.last_response.count("Reused session-id") == 1)
        test.log.info(test.ssh_server.last_response.count("Reused session-id"))

    def cleanup(test):
        try:
            test.ssl_server_thread.join()
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.info("Object ssl_server does not exist")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def open_profile_and_check(test, step_numbers):
        if step_numbers[0] != 9:
            test.log.step("{}. Open defined profile and check if connection opened correctly."
                      .format(step_numbers[0]))
        elif step_numbers[0] == 12:
            test.log.step("{}. Reopen connection".format(step_numbers[0]))
        test.sleep(3)
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)

        if step_numbers[0] != 9:
            test.log.step("{}. Send some data to server.".format(step_numbers[1]))
        elif step_numbers[0] == 12:
            test.log.step("{}. Send another data to server and check if connection was "
                          "resumed".format(step_numbers[0]))
            test.log.info("{}. amount of resumptions will be checked at the end of the "
                          "test".format(step_numbers[0]))
        test.expect(test.profile.dstl_get_service().dstl_send_sisw_command_and_data(1500))

        if step_numbers[0] != 9:
            test.log.step("{}. Check service state AT^SISI=srvProfileId,2.".format(step_numbers[2]))

        test.expect('"sessid"' in test.profile.dstl_get_parser().dstl_get_resumption_information())


if __name__ == "__main__":
    unicorn.main()
