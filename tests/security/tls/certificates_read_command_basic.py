 #responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0104383.001

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
        test.delete_installed_certificates(test)

    def run(test):
        test.log.step("1. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

        test.log.step("2. Check syntax of response.")
        test.expect(test.check_sbnr_syntax(test, False))

        test.log.step("3. Load client certificate and server public certificate on module.")
        test.certificates.dstl_upload_certificate_at_index_0(join("openssl_certificates", "client.der"),
                                                             join("openssl_certificates", "private_client_key"))
        test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates", "certificate_conf_1.der"))

        test.log.step("4. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

        test.log.step("5. Check syntax of response.")
        test.expect(test.check_sbnr_syntax(test, True))

    def cleanup(test):
        test.log.step("6. Remove certificates.")
        test.certificates.dstl_delete_certificate(1)
        test.certificates.dstl_delete_certificate(0)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

    @staticmethod
    def delete_installed_certificates(test):
        installed_certificates = test.certificates.dstl_count_uploaded_certificates()
        if installed_certificates > 0:
            test.log.info("{} certificate(s) will be removed.".format(installed_certificates))
            for cert_index in range(installed_certificates-1, -1, -1):
                test.certificates.dstl_delete_certificate(cert_index)

    @staticmethod
    def check_sbnr_syntax(test, is_certificates_installed):
        sbnr_syntax_with_certificates = ".*SBNR: [0-20], size: \"\\d{2,4}\", issuer: \"\\S{1,100}\", serial number: " \
                                        "\"\\S{1,20}\", subject: \"\\S{1,100}\", signature: \"\\S{1,20}\", " \
                                        "thumbprint algorithm: \"sha1\", thumbprint: \"\\S{1,50}\", expiry date: " \
                                        "\"\\d{2}\\/\\d{2}\\/\\d{2} \\d{2}:\\d{2}:\\d{2}\""
        sbnr_syntax_without_certificates = ".*SBNR: [0-20], size: \"0\", issuer: \"\", serial number: \"\", subject: " \
                                           "\"\", signature: \"\", thumbprint algorithm: \"\", thumbprint: " \
                                           "\"\", expiry date: \"\""
        test.dut.at1.send_and_verify("AT^SBNR=\"is_cert\"")
        if is_certificates_installed:
            return re.search(sbnr_syntax_with_certificates, test.dut.at1.last_response)
        else:
            return re.search(sbnr_syntax_without_certificates, test.dut.at1.last_response)


if "__main__" == __name__:
    unicorn.main()
