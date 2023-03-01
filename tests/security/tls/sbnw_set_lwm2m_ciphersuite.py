# responsible dominik.tanderys@globallogic.com
# Wroclaw
# TC0105105.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.dstl_set_cipher_suites_user_file import \
    dstl_set_length_of_cipher_suites_file, dstl_send_selected_cipher_suites_list, \
    dstl_remove_cipher_suites_file
from dstl.internet_service.configuration.cipher_suites_file_read import dstl_read_cipher_suites_file
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """Short description:
       to check possibility of choosing lwM2M ciphersuites with sbnw AT command

       Detailed description:
        1. Use AT^SBNW="ciphersuites", command to set current ciphersuite to
        TLS_PSK_WITH_AES_128_CBC_SHA256,
         and check if it was set.
        2. Use AT^SBNW="ciphersuites", command to set current ciphersuite to
        TLS_PSK_WITH_AES_128_CCM_8,
         and check if it was set.
        3. Use AT^SBNW="ciphersuites", command to set current ciphersuite to
        TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256,
         and check if it was set.
        4. Use AT^SBNW="ciphersuites", command to set current ciphersuite to
        TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8,
         and check if it was set."""

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_get_imei(test.dut)

    def run(test):

        test.log.info("TC0105105.001 - SBNW_set_lwM2M_ciphersuite")
        test.log.step("1) Use AT^SBNW=\"ciphersuites\", command to"
                      " set current ciphersuite to TLS_PSK_WITH_AES_128_CBC_SHA256")
        test.set_ciphersuite("PSK-AES128-CBC-SHA256")

        test.log.step("2) Use AT^SBNW=\"ciphersuites\", command to"
                      " set current ciphersuite to TLS_PSK_WITH_AES_128_CCM_8")
        test.set_ciphersuite("PSK-AES128-CCM8")

        test.log.step("3) Use AT^SBNW=\"ciphersuites\", command to"
                      " set current ciphersuite to TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256")
        test.set_ciphersuite("ECDHE-PSK-AES128-CBC-SHA256")

        test.log.step("4) Use AT^SBNW=\"ciphersuites\", command to"
                      " set current ciphersuite to TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8")
        test.set_ciphersuite("ECDHE-ECDSA-AES128-CCM8")

    def cleanup(test):
        dstl_remove_cipher_suites_file(test.dut)

    def set_ciphersuite(test, ciphersuite):
        dstl_set_length_of_cipher_suites_file(test.dut, len(ciphersuite))
        test.expect(dstl_send_selected_cipher_suites_list(test.dut, ciphersuite))
        test.expect(ciphersuite in dstl_read_cipher_suites_file(test.dut))


if "__main__" == __name__:
    unicorn.main()