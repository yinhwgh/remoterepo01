#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0107180.001

import unicorn
import time
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
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))  # current file path.
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client.der")
        server_cert_file = []  # path to server certificate
        for i in range(1, 10):
            server_cert_file.append(join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server", "{}.sec".format(str(i))))

        test.log.info("Empty IS store certificates.")
        is_certificate = InternetServicesCertificates(test.dut, device_interface="at1")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 23):
                test.log.info("Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)

        loop = 1
        while loop < 51:
            test.log.info("*************************************")
            test.log.info("Install certificates Loop {} starts...".format(loop))
            test.log.info("*************************************")
            test.log.info("Install is_cert client and server certificates.")
            test.expect(is_certificate.dstl_upload_certificate_at_index_0(cert_file, key_file))
            test.sleep(30)
            for index in range(1, 5):
                test.log.info("Install No. " + str(index) + " is_cert server certificate.")
                test.expect(is_certificate.dstl_upload_server_certificate(index, server_cert_file[index]))
                test.sleep(30)
            test.log.info("Delete client and server certificates.")
            # count = is_certificate.dstl_count_uploaded_certificates()
            if is_certificate.dstl_count_uploaded_certificates() > 0:
                test.expect(test.dut.at1.send_and_verify("at^ssecua=\"CertStore/TLS/DeleteAllClient\"", ".*OK.*"))
                test.expect(test.dut.at1.send_and_verify("at^ssecua=\"CertStore/TLS/DeleteAllServer\"", ".*OK.*"))
                # test.log.info("The number of certificate in is_cert is: " + str(is_certificate.dstl_count_uploaded_certificates()))
                test.sleep(10)
            else:
                test.log.info("No certificate in is_cert.")
            loop += 1

    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
