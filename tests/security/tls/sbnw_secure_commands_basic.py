# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0102462.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from os.path import join


class Test(BaseTest):
    """
    TC name:
    TC0102462.001 - SBNWSecureCommandsBasic

    Intention:
    Uploading of client and server certificates to the module

    description:
    1. Upload client certificate using IpCertManager at index 0.
    2. Upload server certificate using IpCertManager to all available indexes.
    3. Delete server certificates.
    4. Delete client certificate.

    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.certificates = InternetServicesCertificates(test.dut)

    def run(test):
        test.log.step("1. Upload client certificate using IpCertManager at index 0.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")),
            (join("openssl_certificates", "private_client_key")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

        test.log.step("2. Upload server certificate using IpCertManager to all available indexes.")
        for i in range(1, 31):
            test.certificates.dstl_upload_server_certificate(i, join("openssl_certificates",
                                                                     "certificate_conf_1.der"))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 31)

        test.log.step("3. Delete server certificates.")
        for i in range(30, 0, -1):
            test.certificates.dstl_delete_certificate(i)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

        test.log.step("4. Delete client certificate.")
        test.certificates.dstl_delete_certificate(0)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

    def cleanup(test):
        try:
            if test.certificates.dstl_count_uploaded_certificates() is not 0:
                for i in range(30, -1, -1):
                    test.certificates.dstl_delete_certificate(i)
        except AttributeError:
            test.log.error("problem with certificate object")


if __name__ == "__main__":
    unicorn.main()
