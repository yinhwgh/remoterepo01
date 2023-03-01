# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0102358.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import \
    dstl_check_no_internet_profiles_defined
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    To check correct implementation of (D)TLS resumption parameters.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        tls_ses_type_init_correct_values = ["none", "sesid", "all"]
        tls_ses_exp_init_correct_values = ["0", "60", "3600"]
        tls_ses_pers_correct_values = ["0", "1"]
        tls_ses_pers_incorrect_values = ["-2", "2"]
        con_id = '1'
        service_profile_id = '0'
        test.log.info("Executing script for test case: 'TC0102358.001 TlsResumptionParameters'")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        test.log.step("1. Create Socket profile")
        test.socket = SocketProfile(test.dut, service_profile_id, con_id, protocol="tcp",
                                    alphabet=1, ip_version="IPv4",
                               address="195.238.92.60:666")
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.log.step("2. Change 'Error Message Format' to 2 with AT+CMEE=2 command")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("3. Try to add 'TlsSesTypeInit' parameter with the following values, "
                      "and check if value"
                      " was correctly added (at^siss?).\r\n"
                        "a) none\r\n"
                        "b) sesid\r\n"
                        "c) all\r\n"
                        "d) socket\r\n")
        for ses_type_value in tls_ses_type_init_correct_values:
            test.log.info("Checking if value can be set to " + ses_type_value)
            test.socket.dstl_set_tls_ses_type_init(ses_type_value)
            test.expect(test.socket.dstl_get_service().dstl_write_tls_ses_type_init())
            test.log.info("Checking if set value is correct, expected: " + ses_type_value)
            test.expect(dstl_get_siss_read_response(test.dut))
            test.expect('SISS: 0,"TlsSesTypeInit","{}"'.format(ses_type_value)
                        in test.dut.at1.last_response)
        test.log.info("Checking if 'socket' value can be set")
        test.socket.dstl_set_tls_ses_type_init("socket")
        test.expect(not test.socket.dstl_get_service().dstl_write_tls_ses_type_init())
        test.expect(dstl_get_siss_read_response(test.dut))
        test.expect('SISS: 0,"TlsSesTypeInit","{}"'.format(ses_type_value)
                    in test.dut.at1.last_response)

        test.log.step("4. Try to add 'TlsSesExpInit' parameter with the following values, "
                      "and check if value was correctly added (at^siss?)\r\n"
                        "a) 0\r\n"
                        "b) 60\r\n"
                        "c) 3600\r\n"
                        "d) -1 (or -2 for some products)")
        for ses_exp_value in tls_ses_exp_init_correct_values:
            test.log.info("Checking if value can be set to " + ses_exp_value)
            test.socket.dstl_set_tls_ses_exp_init(ses_exp_value)
            test.expect(test.socket.dstl_get_service().dstl_write_tls_ses_exp_init())
            test.log.info("Checking if set value is correct, expected: " + ses_exp_value)
            test.expect(dstl_get_siss_read_response(test.dut))
            test.expect('SISS: 0,"TlsSesExpInit","{}"'.format(ses_exp_value)
                        in test.dut.at1.last_response)
        test.log.info("Checking if '-2' value can be set")
        test.socket.dstl_set_tls_ses_exp_init("-2")
        test.expect(not test.socket.dstl_get_service().dstl_write_tls_ses_exp_init())
        test.expect(dstl_get_siss_read_response(test.dut))
        test.expect('SISS: 0,"TlsSesTypeInit","{}"'.format(ses_type_value)
                    in test.dut.at1.last_response)
        test.expect('SISS: 0,"TlsSesExpInit","{}"'.format(ses_exp_value)
                    in test.dut.at1.last_response)

        test.log.step("5. Try to add 'TlsSesPers' parameter with the following values, "
                      "and check if value was correctly added (at^siss?).\r\n"
                        "a) 0\r\n"
                        "b) 1\r\n"
                        "c) -1 (or -2 for some products)\r\n"
                        "d) 2\r\n")
        for tls_pers_value in tls_ses_pers_correct_values:
            test.log.info("Checking if value can be set to " + tls_pers_value)
            test.socket.dstl_set_ses_pers(tls_pers_value)
            test.expect(test.socket.dstl_get_service().dstl_write_tls_ses_pers())
            test.log.info("Checking if set value is correct, expected: " + tls_pers_value)
            test.expect(dstl_get_siss_read_response(test.dut))
            test.expect('SISS: 0,"TlsSesPers","{}"'.format(tls_pers_value)
                        in test.dut.at1.last_response)

        for tls_pers_incorrect_value in tls_ses_pers_incorrect_values:
            test.log.info("Checking if incorrect value can be set to " + tls_pers_incorrect_value)
            test.socket.dstl_set_ses_pers(tls_pers_incorrect_value)
            test.expect(not test.socket.dstl_get_service().dstl_write_tls_ses_pers())
            test.expect(dstl_get_siss_read_response(test.dut))
            test.expect('SISS: 0,"TlsSesTypeInit","{}"'.format(ses_type_value)
                        in test.dut.at1.last_response)
            test.expect('SISS: 0,"TlsSesExpInit","{}"'.format(ses_exp_value)
                        in test.dut.at1.last_response)
            test.expect('SISS: 0,"TlsSesPers","{}"'.format(tls_pers_value)
                        in test.dut.at1.last_response)

    def cleanup(test):
        test.log.step("6. Delete profile and check result with (at^siss?)")
        test.expect(test.socket.dstl_get_service().dstl_reset_service_profile())
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))


if "__main__" == __name__:
    unicorn.main()
