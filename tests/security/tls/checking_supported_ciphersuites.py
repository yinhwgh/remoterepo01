# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102603.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.cipher_suites_file_read import dstl_read_cipher_suites_file
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_set_length_of_cipher_suites_file, dstl_remove_cipher_suites_file, \
    dstl_send_selected_cipher_suites_list


class Test(BaseTest):
    """
    Intention: Checking list of supported ciphersuites on module.

    Description:
    1. Check default ciphersuites using SBNR command
    2. Check current ciphersuites using SBNR command (list set by user)
    3. Delete list of ciphersuites set by user
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):

        ciphersuites_list_serval = ["DES-CBC3-SHA", "AES128-SHA", "AES256-SHA",
                                    "DHE-RSA-AES128-SHA", "DHE-RSA-AES256-SHA",
                                    "ECDHE-RSA-AES128-SHA", "ECDHE-RSA-AES256-SHA",
                                    "ECDHE-ECDSA-AES128-SHA", "ECDHE-ECDSA-AES256-SHA",
                                    "ECDHE-RSA-DES-CBC3-SHA", "ECDHE-ECDSA-DES-CBC3-SHA",
                                    "AES128-SHA256", "AES256-SHA256", "DHE-RSA-AES128-SHA256",
                                    "DHE-RSA-AES256-SHA256", "ECDH-RSA-AES128-SHA",
                                    "ECDH-RSA-AES256-SHA", "ECDH-ECDSA-AES128-SHA256",
                                    "ECDH-ECDSA-AES256-SHA384", "ECDH-RSA-DES-CBC3-SHA",
                                    "ECDH-ECDSA-DES-CBC3-SHA", "AES128-GCM-SHA256",
                                    "AES256-GCM-SHA384", "DHE-RSA-AES128-GCM-SHA256",
                                    "DHE-RSA-AES256-GCM-SHA384", "ECDHE-RSA-AES128-GCM-SHA256",
                                    "ECDHE-RSA-AES256-GCM-SHA384", "ECDHE-ECDSA-AES128-GCM-SHA256",
                                    "ECDHE-ECDSA-AES256-GCM-SHA384", "ECDH-RSA-AES128-GCM-SHA256",
                                    "ECDH-RSA-AES256-GCM-SHA384", "ECDH-ECDSA-AES128-GCM-SHA256",
                                    "ECDH-ECDSA-AES256-GCM-SHA384", "ECDHE-ECDSA-AES128-SHA256",
                                    "ECDH-RSA-AES128-SHA256", "ECDH-ECDSA-AES128-SHA256",
                                    "ECDHE-RSA-AES256-SHA384", "ECDHE-ECDSA-AES256-SHA384",
                                    "ECDH-RSA-AES256-SHA384", "ECDH-ECDSA-AES256-SHA384",
                                    "ECDHE-RSA-CHACHA20-POLY1305", "ECDHE-ECDSA-CHACHA20-POLY1305",
                                    "DHE-RSA-CHACHA20-POLY1305", "EDH-RSA-DES-CBC3-SHA",
                                    "TLS13-AES128-GCM-SHA256", "TLS13-AES256-GCM-SHA384",
                                    "TLS13-CHACHA20-POLY1305-SHA256",
                                    "TLS13-AES128-CCM-SHA256", "TLS13-AES128-CCM-8-SHA256",
                                    "AES256-CCM-8", "AES128-CCM-8"]
        ciphersuites_current = "AES256-CCM-8"

        test.log.step("1. Check default ciphersuites using SBNR command")
        cipher = dstl_read_cipher_suites_file(test.dut, "default")
        for ciphersuite in ciphersuites_list_serval:
            test.expect(ciphersuite in cipher)

        test.log.step("2. Check current ciphersuites using SBNR command (list set by user)")
        test.expect(dstl_set_length_of_cipher_suites_file(test.dut, len(ciphersuites_current)))
        test.expect(dstl_send_selected_cipher_suites_list(test.dut, ciphersuites_current))
        cipher = dstl_read_cipher_suites_file(test.dut, "current")
        test.expect(ciphersuites_current in cipher)

        test.log.step("3. Delete list of ciphersuites set by user")
        test.expect(dstl_remove_cipher_suites_file(test.dut))
        error_message = "No Cipher Suites file found or loaded"
        cipher = dstl_read_cipher_suites_file(test.dut, "current")
        test.expect(error_message in cipher)


    def cleanup(test):
        dstl_remove_cipher_suites_file(test.dut)


if "__main__" == __name__:
    unicorn.main()
