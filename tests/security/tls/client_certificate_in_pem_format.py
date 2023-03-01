# responsible: dominik.tanderys@globallogic.com
# Wroclaw
# TC0104319.001

import unicorn

from os.path import join
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC name:
    TC0104319.001 - ClientCertificateInPemFormat

    Intention:
    To check if client certificate in PEM format can be uploaded on the module.
    """

    def setup(test):

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

        test.certificates = InternetServicesCertificates(test.dut)

        test.log.step("Preparation: remove all certificates from module")
        if test.certificates.dstl_count_uploaded_certificates() is not 0:
            test.certificates.dstl_delete_all_uploaded_certificates()

    def run(test):
        test.log.step("1. Check if certificate store is empty.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

        test.log.step("2. Upload client certificate in PEM format on module.")
        test.certificates.dstl_set_security_private_key("NONE", "client", "pwdclient",
                                                        join("echo_certificates", "client",
                                                             "client.ks"), "pwdclient")
        test.certificates.dstl_upload_certificate_at_index_0(
            (join(test.certificates.certificates_path, "echo_certificates", "client",
                  "client.pem")),
            (join(test.certificates.certificates_path, "echo_certificates", "client",
                  "client_priv.der")))

        test.log.step("3. Check certificate store.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Delete client certificate.")
        test.certificates.dstl_delete_certificate(0)

        test.log.step("5. Check certificate store.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")

    def cleanup(test):
        try:
            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.certificates.dstl_delete_all_certificates_using_ssecua()
                test.certificates.dstl_delete_all_uploaded_certificates()

        except AttributeError:
            test.log.error("problem with certificates.")


if __name__ == "__main__":
    unicorn.main()
