#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0105009.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """
    Intention: To check if available by default cipher suites list is correct and comparable to the documentation.

    Description: 1. Display default ciphersuite list.
        2. Use command for Cipher suites user file removal
        3. Check again default ciphersuites list
        4. Display current list of ciphersuites
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):

        ciphersuites_list_cougar = ["TLS13-AES128-GCM-SHA256", "TLS13-AES256-GCM-SHA384",
                                    "TLS13-CHACHA20-POLY1305-SHA256", "TLS13-AES128-CCM-SHA256",
                                    "TLS13-AES128-CCM-8-SHA256", "TLS13-SHA256-SHA256", "TLS13-SHA384-SHA384",
                                    "DES-CBC3-SHA", "AES128-SHA", "AES256-SHA", "DHE-RSA-AES128-SHA",
                                    "DHE-RSA-AES256-SHA", "AES128-B2B256", "AES256-B2B256", "AES128-CCM-8",
                                    "AES256-CCM-8", "ECDHE-ECDSA-AES128-CCM", "ECDHE-ECDSA-AES128-CCM-8",
                                    "ECDHE-ECDSA-AES256-CCM-8", "ECDHE-RSA-AES128-SHA", "ECDHE-RSA-AES256-SHA",
                                    "ECDHE-ECDSA-AES128-SHA", "ECDHE-ECDSA-AES256-SHA", "ECDHE-RSA-DES-CBC3-SHA",
                                    "ECDHE-ECDSA-DES-CBC3-SHA", "AES128-SHA256", "AES256-SHA256",
                                    "DHE-RSA-AES128-SHA256", "DHE-RSA-AES256-SHA256", "AES128-GCM-SHA256",
                                    "AES256-GCM-SHA384", "DHE-RSA-AES128-GCM-SHA256", "DHE-RSA-AES256-GCM-SHA384",
                                    "ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-RSA-AES256-GCM-SHA384",
                                    "ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-ECDSA-AES256-GCM-SHA384", "CAMELLIA128-SHA",
                                    "DHE-RSA-CAMELLIA128-SHA", "CAMELLIA256-SHA", "DHE-RSA-CAMELLIA256-SHA",
                                    "CAMELLIA128-SHA256", "DHE-RSA-CAMELLIA128-SHA256", "CAMELLIA256-SHA256",
                                    "DHE-RSA-CAMELLIA256-SHA256", "ECDHE-RSA-AES128-SHA256",
                                    "ECDHE-ECDSA-AES128-SHA256", "ECDHE-RSA-AES256-SHA384", "ECDHE-ECDSA-AES256-SHA384",
                                    "ECDHE-RSA-CHACHA20-POLY1305", "ECDHE-ECDSA-CHACHA20-POLY1305",
                                    "DHE-RSA-CHACHA20-POLY1305", "EDH-RSA-DES-CBC3-SHA"]

        test.log.step("1. Display default ciphersuite list.")
        test.expect(test.dut.at1.send_and_verify('AT^sbnr=\"ciphersuites\", \"default\"'))
        for ciphersuite in ciphersuites_list_cougar:
            test.expect(ciphersuite in test.dut.at1.last_response)

        test.log.step("2. Use command for Cipher suites user file removal")
        test.expect(test.dut.at1.send_and_verify('AT^sbnw=\"ciphersuites\", \"0\"'))

        test.log.step("3. Check again default ciphersuites list")
        test.expect(test.dut.at1.send_and_verify('AT^sbnr=\"ciphersuites\", \"default\"'))
        for ciphersuite in ciphersuites_list_cougar:
            test.expect(ciphersuite in test.dut.at1.last_response)

        test.log.step("4. Display current list of ciphersuites")
        error_message = "No Cipher Suites file found or loaded"
        test.expect(test.dut.at1.send_and_verify('AT^sbnr=\"ciphersuites\", \"current\"', expect=error_message))

    def cleanup(test):

        pass


if "__main__" == __name__:
    unicorn.main()
