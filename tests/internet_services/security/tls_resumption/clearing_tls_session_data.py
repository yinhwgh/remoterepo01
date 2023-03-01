# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105108.001, TC0105108.002

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
    ClearingTlsSessionData

    Intention:
    To check if any stored TLS session data can be cleared using the AT^SIPS="tls-session",
    "reset" and AT^SISS=0,"TlsSesTypeInit","none" commands.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.log.step("1. Change Error Message Format with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Create TCP Client profile (connection to SSL server) with parameters: \n"
                      "- TlsSesTypeInit - sesid or '1', depending on product \n"
                      "- TlsSesExpInit - 600 \n"
                      "- TlsSesPers - 1 \n"
                      "- SecOpt - 0")
        dstl_remove_cipher_suites_file(test.dut)
        test.ssl_server = SslServer("IPv4", "socket_tls", 'TLS_DHE_RSA_WITH_AES_128_CBC_SHA256',
                                    extended=True, naccept=0, timeout=600)
        test.host = test.ssl_server.dstl_get_server_ip_address()
        test.port = test.ssl_server.dstl_get_server_port()
        test.connection_setup = dstl_get_connection_setup_object(test.dut)

        test.define_and_load_profile("1")

        test.log.step("3. Check defined profile AT^SISS.")
        dstl_check_siss_read_response(test.dut, [test.profile])

        test.log.step("4. Start IP traffic tracing using Wireshark on server side.")
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration=5)
        test.log.info("no need for TCPDUMP, SSL server will inform if new session ticket was "
                      "issued")

        test.open_profile_and_check([5, 6, 7])

        test.log.step("8. Change the TlsSesTypeInit parameter to 'none' to clear stored TLS "
                      "session data.")
        test.profile.dstl_set_tls_ses_type_init("none")
        test.expect(test.profile.dstl_get_service().dstl_write_tls_ses_type_init())

        test.log.step("9. Change back the TlsSesTypeInit parameter to 'sesid'.")
        test.profile.dstl_set_tls_ses_type_init("sesid")
        test.expect(test.profile.dstl_get_service().dstl_write_tls_ses_type_init())

        test.log.step("10. Repeat steps 5-7.")
        test.open_profile_and_check(["10.5", "10.6", "10.7"])

        test.log.step('11. Clear stored TLS session data again, but this time using the '
                      'AT^SIPS="tls-session","reset" command.')
        dstl_execute_sips_command(test.dut, "tls-session", "reset")

        test.log.step("12. Repeat steps 5-7.")
        test.open_profile_and_check(["12.5", "12.6", "12.7"])

        test.log.step("13. set - TlsSesPers to 0, Clear session data via resetting the module")
        test.profile.dstl_set_ses_pers("0")
        test.expect(test.profile.dstl_get_service().dstl_write_tls_ses_pers())
        test.expect(dstl_restart(test.dut))

        test.log.step("14. Repeat steps 5-7")
        test.define_and_load_profile("0")
        test.open_profile_and_check(["14.5", "14.6", "14.7"])

        test.log.step("15. Clear session data via resetting service profile, and creating it again "
                      "(e.g. with SIPS command)")
        test.expect(dstl_execute_sips_command(test.dut, "all", "reset"))
        test.define_and_load_profile("0")

        test.log.step("16. Repeat steps 5-7")
        test.open_profile_and_check(["16.5", "16.6", "16.7"])

        test.log.info("no need for TCPDUMP, SSL server will inform if session was reused")
        test.ssl_server_thread.join()
        test.expect(test.ssh_server.last_response.count("Reused session-id") == 0)
        test.log.info("Amount of resued sessions: {}".
                      format(test.ssh_server.last_response.count("NewSessionTicket")))

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

        test.log.step("{}. Close profile.".format(step_numbers[2]))
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

    def define_and_load_profile(test, ses_pers):
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.profile = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                     protocol="tcp", tls_ses_pers=ses_pers,
                                     tls_ses_type_init="sesid", host=test.host, port=test.port,
                                     secure_connection=True, tls_ses_exp_init="600", secopt="0")
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())


if __name__ == "__main__":
    unicorn.main()
