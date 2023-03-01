#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0103862.002

import unicorn
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from core.basetest import BaseTest
from os.path import dirname, realpath, join
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        dstl_get_imei(test.dut)

    def run(test):
        # key_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client_priv.der"  # path to private key file
        # cert_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client.der"  # path to client certificate
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))  # current file path.
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client",
                        "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client",
                         "client.der")
        server_cert_file = []  # path to server certificate
        for i in range(1, 25):
            # server_cert_file.append(r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\{}.sec".format(str(i)))
            server_cert_file.append(
                join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server",
                     "{}.sec".format(str(i))))

        test.log.info("Empty preconfig store certificates.")
        preconfig_certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="preconfig_cert")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 23):
                size = preconfig_certificate.dstl_get_certificate_size(index)
                test.log.info("Size of No. " + str(index) + " certificate is: " + str(size))
                if size != '0':
                    test.log.info("Delete No. " + str(index) + " preconfig store certificates.")
                    preconfig_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Upload client preconfig certificate.")
        preconfig_certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)
        test.sleep(30)
        test.log.info("Upload 20 server preconfig certificates.")
        for index in range(1, 21):
            test.log.info("Install No. " + str(index) + " preconfig store server certificate.")
            preconfig_certificate.dstl_upload_server_certificate(index, server_cert_file[index -1])
            test.sleep(30)
        test.log.info("View preconfig certificate list.")
        if preconfig_certificate.dstl_count_uploaded_certificates() == 21:
            test.expect(True)
            test.log.info("Upload preconfig certificates successful.")
        else:
            test.expect(False)
            test.log.info("Upload preconfig certificates failed.")
        test.log.info("Upload one more server preconfig certificare with index 10.")
        preconfig_certificate.dstl_upload_server_certificate(10, server_cert_file[15])
        test.sleep(30)
        test.log.info("View preconfig certificate list.")
        if preconfig_certificate.dstl_count_uploaded_certificates() == 21:
            if preconfig_certificate.dstl_get_certificate_size(10) == preconfig_certificate.dstl_get_certificate_size(16):
                test.expect(True)
                test.log.info("Replace preconfig certificate successful.")
            else:
                test.expect(False)
                test.log.info("Replace preconfig certificate failed.")
        # test.dut.at1.send_and_verify("at^sbnr=\"preconfig_cert\"")
        # if cert_file in test.dut.at1.last_response:
        #     test.expect(True)
        #     test.log.info("Index 10 certificate replaced.")
        # test.log.info("Upload one more server preconfig certificare with index 21.")
        # test.expect(not preconfig_certificate.dstl_upload_server_certificate(21, server_cert_file[21]))
        test.log.info("Remove preconfig certificates.")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 23):
                size = preconfig_certificate.dstl_get_certificate_size(index)
                test.log.info("Size of No. " + str(index) + " certificate is: " + str(size))
                if size != '0':
                    test.log.info("Delete No. " + str(index) + " preconfig store certificates.")
                    preconfig_certificate.dstl_delete_certificate(index)
                    test.sleep(30)

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
