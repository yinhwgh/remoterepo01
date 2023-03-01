#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0104381.001

import unicorn

from os.path import join
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    """
    TC0104381.001 - TLSClientCertPreloading

    Intention:
    The intention of this test case is to check pre-loading of TLS certificate for Client authentication.

    description:
    1. Create the TLS certificate for client authentication with the provided cert tool;
    2. Inject the certificates into each module together with the IMEI (or serial number for modules
       with customer IMEI) by AT command ^SBNW.
    3. List the installed certificate with AT command.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

        test.certificates = InternetServicesCertificates(
        test.dut, test_files_certificates_path=f'{test.test_files_path}\\certificates\\tls_certificates',
        mode='preconfig_cert')
        test.cert_bin_file = "preconfig_bin"
        test.cert_size = "2816"
        test.cert_serial_number = "16967B01A665E6E5"
        test.cert_issuer = "Thales IoT ECC CA"
        test.is_cert_add = False


    def run(test):
        test.log.step("1. Upload preconfigured client certificate at index 0.")
        expect_cert_info = f'^SBNR: 0, size: "{test.cert_size}", issuer: "/CN={test.cert_issuer}", ' \
            f'serial number: "{test.cert_serial_number}", ' \
            f'subject: "/CN=BYD_MODSTEST_00001_2f06b38b-81f3-4799-ad7f-709a212e3829_11", ' \
            f'signature: "sha256ECDSA", thumbprint algorithm: "sha1", ' \
            f'thumbprint: "5804670F237E5D04AA72CF4FB7D9016B01C90661", expiry date: "2035,10,29"'
        certs_count_before_test = test.certificates.dstl_count_uploaded_certificates()
        test.expect(expect_cert_info not in test.dut.at1.last_response)
        test.expect(test.certificates.dstl_upload_certificate_in_bin_format(test.cert_bin_file),
                    msg="Upload preconfigured client certificate failed.")

        test.log.step("2. Expected preconfigured client certificate is displayed by AT command.")
        certs_count_after_test = test.certificates.dstl_count_uploaded_certificates()
        test.log.info(f"Certificates count before uploading is {certs_count_before_test}.")
        test.log.info(f"Certificates count after uploading is {certs_count_after_test}.")
        test.is_cert_add = test.expect(certs_count_after_test == certs_count_before_test + 1)
        test.log.info("Checking expected certificate is displayed:")
        test.log.info(expect_cert_info)
        test.expect(expect_cert_info in test.dut.at1.last_response)

    def cleanup(test):
        test.log.info("Checking if module exiting sending file mode.")
        atc_mode = test.dut.at1.send_and_verify("AT", "OK")
        if not atc_mode:
            test.dut.wait_for("ERROR", timeout=60)
        if test.is_cert_add:
            deleted = test.expect(test.dut.at1.send_and_verify(
                                  'AT^SSECUA="CertStore/Preconfigured/DeleteAll"', "OK"))
            if deleted:
                test.log.info("Added preconfigured client certificate was deleted successfully.")
            else:
                test.log.error("Fail to delete added preconfigured client certificate after tests.")


if __name__ == "__main__":
    unicorn.main()
