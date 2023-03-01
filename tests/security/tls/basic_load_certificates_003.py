#responsible: michal.habrych@globallogic.com
#location: Wroclaw
#TC0087975.003, TC0087975.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from os.path import join
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    """
    Intention:
    Uploading of client and server certificates to the module and to test basic functionalities like read, overwrite
    and deleting.
    Test case for products with Secure Mode functionality (using AT^SSECUC="SEC/MODE" command)

    Description:
    1. Try to upload client certificate at index different from zero e.g. at index 1.
    2. Upload client certificate at index 0.
    3. Upload server certificate to all available indexes.
    4. Delete client certificate.
    5. Delete server's certificate's.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

        test.certificates = InternetServicesCertificates(test.dut)
        test.cert_file = join(test.certificates.certificates_path, "openssl_certificates", "client.der")
        test.key_file = join(test.certificates.certificates_path, "openssl_certificates", "private_client_key")

    def run(test):
        cert_max_index = 30
        test.cert_number = cert_max_index + 1

        test.log.step("Preconfig: checking if any certificate is already installed and deleting if necessary")
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.log.step("1. Try to upload client certificate at index different from zero e.g. at index 1.")
        jar_arguments = ["-serialPort", test.certificates.port_name, "-serialSpd", test.certificates.serial_speed,
                         "-cmd", "writecert","-certfile",  test.cert_file, "-certIndex", "1", "-mode",
                         test.certificates.mode, "-keyfile", test.key_file, "-sigType", "NONE"]
        test.certificates.dstl_execute_ip_cert_mgr_jar(jar_arguments)
        if test.certificates.dstl_count_uploaded_certificates() is not 0:
            test.expect(False, msg="ERROR: Client Cert installed on index different than 0")
            test.certificates.dstl_delete_certificate(1)

        test.log.step("2. Upload client certificate at index 0.")
        test.certificates.dstl_upload_certificate_at_index_0(test.cert_file, test.key_file)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Upload server certificate to all available indexes.")
        for i in range(1, test.cert_number):
            test.certificates.dstl_upload_server_certificate(i, join("openssl_certificates", "certificate_conf_1.der"))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == test.cert_number,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Delete client certificate.")
        test.certificates.dstl_delete_certificate(0)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == cert_max_index,
                     msg="Wrong amount of certificates installed")

    def cleanup(test):
        test.log.step("5. Delete server's certificate's")
        for i in range(1, test.cert_number):
            test.certificates.dstl_delete_certificate(i)
        if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                msg="Problem with deleting certificates from module"):
            test.certificates.dstl_delete_all_certificates_using_ssecua()

if __name__ == "__main__":
    unicorn.main()