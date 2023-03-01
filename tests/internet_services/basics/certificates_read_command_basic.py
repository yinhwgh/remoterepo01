# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0104383.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.openssl_certificates import InternetServicesCertificates
from dstl.network_service.register_to_network import dstl_enter_pin
from os.path import join


class Test(BaseTest):
    """
       TC intention: Checking syntax of command for reading the certificates.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.certificates = InternetServicesCertificates(test.dut)

    def run(test):
        test.log.step("1. Check if certificates are installed.")
        test.certificates.dstl_delete_all_uploaded_certificates()
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

        test.log.step("2. Check syntax of response.")
        test.expect(test.check_sbnr_syntax(test, False))

        test.log.step("3. Load client certificate and server public certificate on module.")
        test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates",
                                                                  "client.der"),
                                                             join("openssl_certificates",
                                                                  "private_client_key"))
        test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates",
                                                                   "certificate_conf_1.der"))

        test.log.step("4. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("5. Check syntax of response.")
        test.expect(test.check_sbnr_syntax(test, True))

    def cleanup(test):
        test.log.step("6. Remove certificates.")
        try:
            test.certificates.dstl_delete_certificate(1)
            test.certificates.dstl_delete_certificate(0)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)
            test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")

    @staticmethod
    def check_sbnr_syntax(test, is_certificates_installed):
        regex_one_line_no_cert = r'.*SBNR: \d{1,2}, size: "0", issuer: "", serial number: "", ' \
                                 r'subject: "", signature: "", thumbprint algorithm: "", ' \
                                 r'thumbprint: "", expiry date: ""\s'
        regex_one_line_with_cert = r'.*SBNR: (\d), size: "\d{2,4}", issuer: "\S{1,1000}", ' \
                                   r'serial number: "\S{1,30}", subject: "\S{1,100}", ' \
                                   r'signature: "\S{1,20}", thumbprint algorithm: "sha1", ' \
                                   r'thumbprint: "\S{1,50}", ' \
                                   r'expiry date: "\d{2,4},\d{1,2},\d{1,2}"\s'

        lines_with_cert = re.findall(regex_one_line_with_cert, test.dut.at1.last_response)
        lines_without_cert = re.findall(regex_one_line_no_cert, test.dut.at1.last_response)

        test.log.info('Verify also number of lines in SBNR command response')
        if is_certificates_installed:
            if len(lines_with_cert) == 2 and len(lines_without_cert) == 29:
                test.log.info('PASS -> Expected : 2 lines with certificates '
                              'and 29 lines without certificates')
                test.log.info(f'EXPECTED RESPONSE SYNTAX - check for 1 line with certificate: '
                              f'{regex_one_line_with_cert}')
                test.log.info(f'EXPECTED RESPONSE SYNTAX - check for 1 line without certificate: '
                              f'{regex_one_line_no_cert}')
                return (re.search(regex_one_line_with_cert, test.dut.at1.last_response) and
                        re.search(regex_one_line_no_cert, test.dut.at1.last_response))

            else:
                return test.expect(False, msg='Incorrect number of lines in SBNR command response\n'
                                              'Expected : 2 lines with certificates '
                                              'and 29 lines without certificates')
        else:
            if len(lines_without_cert) == 31:
                test.log.info('PASS -> Expected : 31 lines without certificates')
                test.log.info(f'EXPECTED RESPONSE SYNTAX - check for 1 line with certificate: '
                              f'{regex_one_line_no_cert}')
                return re.search(regex_one_line_no_cert, test.dut.at1.last_response)
            else:
                return test.expect(False, msg='Incorrect number of lines in SBNR command response\n'
                                              'Expected : 31 lines without certificates')


if "__main__" == __name__:
    unicorn.main()