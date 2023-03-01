# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102394.001, TC0102394.002


import unicorn

from core.basetest import BaseTest

from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.internet_service.configuration.cipher_suites_file_read import dstl_read_cipher_suites_file
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_remove_cipher_suites_file, dstl_set_length_of_cipher_suites_file,\
    dstl_send_selected_cipher_suites_list

import random as rand


class Test(BaseTest):
    """
    TC name:
    TlsResumptionTicketRandomCipher

    Intention:

    To check correct connection resumption with TLS server using Ticket resumption option.
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        for i in range(3):

            test.log.step('1 Select one of supported Ciphers and set it using AT^SBNW="ciphersuites",'
                          'length command.')
            test.choose_cipher()

            test.log.step('2 Check current set of Ciphers using AT^SBNR="ciphersuites","current" '
                          'command')
            test.expect(test.chosen_cipher in dstl_read_cipher_suites_file(test.dut))

            test.log.step('3 Change Error Message Format with AT+CMEE=2 command.')
            test.expect(dstl_set_error_message_format(test.dut))

            test.log.step("4. Create TCP Client profile (connection to SSL server) with parameters:\n"
                            '- TlsSesTypeInit - all or "2", depending on product\n'
                            '- TlsSesExpInit - 120\n'
                            '- TlsSesPers - 1\n'
                            '- SecOpt - 0")\n')
            test.ssl_server = SslServer("IPv4", "socket_tls", test.chosen_cipher,
                                        extended=True, naccept=0, timeout=360, tls_ver="tls1_2")
            test.chosen_cipher_iana = test.ssl_server.cipher_suite_info[1]
            host = test.ssl_server.dstl_get_server_ip_address()
            port = test.ssl_server.dstl_get_server_port()

            test.profile = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                         protocol="tcp", tls_ses_pers="1", tls_ses_type_init="all",
                                         host=host, port=port, secure_connection=True,
                                         tls_ses_exp_init="120", secopt="0")
            test.profile.dstl_generate_address()
            test.expect(test.profile.dstl_get_service().dstl_load_profile())

            test.log.step("5 Check defined profile using AT^SISS command.")
            dstl_check_siss_read_response(test.dut, [test.profile])

            test.log.step("6 Start IP traffic tracing using Wireshark on server side.")
            test.ssh_server2 = test.ssh_server.clone()
            test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                                 configuration=5)
            test.log.info("no need for TCPDUMP, SSL server will inform if new session ticket was "
                          "issued")

            test.open_profile_and_check([7, 8])
            test.open_profile_and_check([9, 10])

            test.log.step("11 Wait till session expires.")
            test.sleep(130)

            test.log.step("12 Reopen connection")
            test.expect(test.profile.dstl_get_service().dstl_open_service_profile())

            test.log.step("13 Send another data to server and check if connection was resume "
                          "correctly.")
            test.expect(test.profile.dstl_get_service().dstl_send_sisw_command_and_data(1500))

            test.log.step("14 Check service state using AT^SISI=srvProfileId,2.")
            test.expect(test.chosen_cipher_iana in test.profile.dstl_get_parser().
                        dstl_get_resumption_information())

            test.log.step("15 Close profile.")
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

            test.log.step("16 Stop Wireshark log and analyze traffic.")
            test.log.info("wiresahrk was not used")
            """Depending on opnessl version"""
            test.expect(test.ssh_server.last_response.count("NewSessionTicket") == 2 or
                        test.ssh_server.last_response.count("write session ticket A") == 2)

            test.ssl_server_thread.join()
            test.ssl_server.dstl_server_close_port()

            if i != 3:
                test.log.step("17 Repeat all steps for two more supported Ciphers")

    def cleanup(test):
        try:
            test.ssl_server_thread.join()
            test.ssl_server.dstl_server_close_port()
        except AttributeError:
            test.log.info("Object ssl_server does not exist")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_remove_cipher_suites_file(test.dut)

    def open_profile_and_check(test, step_numbers):
        if step_numbers[0] != 9:
            test.log.step("{}. Open defined profile and check if connection was opened correctly."
                      .format(step_numbers[0]))
        else:
            test.log.step("{}. Reopen connection before session expires."
                          .format(step_numbers[0]))
        test.sleep(3)
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)
        test.expect(test.chosen_cipher_iana in test.profile.dstl_get_parser().
                    dstl_get_resumption_information())

        test.log.step("{}. Close connection".format(step_numbers[1]))
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

    def choose_cipher(test):
        """Ciphers that are not present in cipher_suite_mapping.txt"""
        unsupported_ciphers = "DHE-PSK-CHACHA20-POLY1305 DHE-PSK-AES256-CBC-SHA384 " \
                              "PSK-AES256-GCM-SHA384 PSK-AES128-CBC-SHA256 " \
                              "DHE-PSK-AES256-GCM-SHA384"
        dstl_remove_cipher_suites_file(test.dut)
        dstl_read_cipher_suites_file(test.dut)
        amount_of_ciphers = test.dut.at1.last_response.count(":")
        supported_ciphers = test.dut.at1.last_response.split(":")
        test.chosen_cipher = "DHE-PSK-AES256-CBC-SHA384"
        while test.chosen_cipher in unsupported_ciphers:
            test.chosen_cipher = supported_ciphers[rand.randint(3, amount_of_ciphers - 1)]
        dstl_set_length_of_cipher_suites_file(test.dut, len(test.chosen_cipher))
        dstl_send_selected_cipher_suites_list(test.dut, test.chosen_cipher)


if __name__ == "__main__":
    unicorn.main()
