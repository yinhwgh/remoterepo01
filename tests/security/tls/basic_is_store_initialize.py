#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0103884.002

import unicorn
import time
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from core.basetest import BaseTest
from os.path import dirname, realpath, join
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.security.internet_service_signature import InternetServiceSignatures


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        dstl_get_imei(test.dut)

    def run(test):

        # key_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client_priv.der"  # path to private key file
        # cert_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client.der"  # path to client certificate
        # server_cert_file = []  # path to server certificate
        # for i in range(1, 20):
        #     server_cert_file.append(r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\{}.sec".format(str(i)))
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))  # current file path.
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client.der")
        server_cert_file = []  # path to server certificate
        for i in range(1, 20):
            server_cert_file.append(join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server", "{}.sec".format(str(i))))

        test.log.info("Empty IS store certificates.")
        is_certificate = InternetServicesCertificates(test.dut, device_interface="at1")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 30):
                test.log.info("Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)

        test.log.info("Empty preconfig store certificates.")
        preconfig_certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="preconfig_cert")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 30):
                size = preconfig_certificate.dstl_get_certificate_size(index)
                test.log.info("Size of No. " + str(index) + " certificate is: " + str(size))
                if size != '0':
                    test.log.info("Delete No. " + str(index) + " preconfig store certificates.")
                    preconfig_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Install preconfig client and server certificates.")
        preconfig_certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)
        for index in range(1, 6):
            test.log.info("Install No. " + str(index) + " preconfig store server certificate.")
            preconfig_certificate.dstl_upload_server_certificate(index, server_cert_file[index])
            test.sleep(30)

        test.log.info("Initial IS store when IS store is empty.")
        signature = InternetServiceSignatures(test.dut)
        if not signature.dstl_initialize_is_store_non_security_mode():
            test.expect(False)
            test.log.info("Initial IS store fail.")
        else:
            test.log.info("Check IS store certificates.")
            count = is_certificate.dstl_count_uploaded_certificates()
            if count == 6:
                for index in range(0, count):
                    if preconfig_certificate.dstl_get_certificate_size(index) == is_certificate.dstl_get_certificate_size(index):
                        test.log.info("No." + str(index) + " certificate update correctly.")
                    else:
                        test.expect(False)
                        test.log.info("No. " + str(index) + " certificate update failed.")
                # test.expect(True)
                # test.log.info("IS store certificates update successful.")
            else:
                test.expect(False)
                test.log.info("IS store certificates update failed.")
        test.log.info("Initial IS store when IS store is not empty.")
        test.expect(not signature.dstl_initialize_is_store_non_security_mode())
        test.sleep(10)
        test.log.info("Check if preconfig certs were removed.")
        if preconfig_certificate.dstl_count_uploaded_certificates() == 0:
            test.expect(False)
            test.log.info("Preconfig certificates should not removed.")
        else:
            test.expect(True)
            test.log.info("Preconfig certificates are present.")
        test.log.info("Delete IS store certificates.")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(count):
                test.log.info("Delete No. " + str(index) + " IS store certificate.")
                is_certificate.dstl_delete_certificate(index)
                test.sleep(30)
        test.log.info("Initialize IS store with only selected certificate")
        # signature = InternetServiceSignatures(test.dut)
        # is_certificate = InternetServicesCertificates(test.dut.at1)
        for index in range(0, 5):
            test.expect(signature.dstl_initialize_is_store_by_index_non_security_mode(index))
            test.sleep(15)
        # test.log.info("Count updated certificates numbers " + str(is_certificate.dstl_count_uploaded_certificates()))
        if is_certificate.dstl_count_uploaded_certificates() == 5:
            test.expect(True)
            test.log.info("Selected certificates have been updated.")
        else:
            test.expect(False)
            test.log.info("Selected certificates have not been updated.")
        test.log.info("Empty IS store certificates.")
        count = is_certificate.dstl_count_uploaded_certificates()
        test.log.info("Count is certificates number : " + str(count))
        if count > 0:
            for index in range(0, 30):
                test.log.info(
                    "Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Empty preconfig store certificates.")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 30):
                size = preconfig_certificate.dstl_get_certificate_size(index)
                test.log.info("Size of No. " + str(index) + " certificate is: " + str(size))
                if size != '0':
                    test.log.info("Delete No. " + str(index) + " preconfig store certificates.")
                    preconfig_certificate.dstl_delete_certificate(index)
                    test.sleep(30)

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
