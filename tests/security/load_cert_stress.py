# responsible dan.liu@thalesgroup.com
# location Dalian
# TC0107870.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from os.path import join
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates

class Test(BaseTest):
    """
    TC0107870.001 - load_cert_stress
    0. Delete all certificates.

   1. Load three different server certificatesÂ  and 1 client certificate to module.

   2. Repeat step 1 1000 times.Â

   3. Repeat step 0 and 2 on Five modules.
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        key_file = join("echo_certificates", "client", "client_priv.der")
        cert_file = join("echo_certificates", "client", "client.der")
        server_cert_file = []
        for i in range(1, 4):
            server_cert_file.append(
                join("echo_certificates", "server", "{}.sec".format(str(i))))
        test.is_certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="is_cert")
        test.log.step("0.  Delete all certificates. ")
        test.expect(test.is_certificate.dstl_delete_all_uploaded_certificates())
        for i in range(1, 1001):
            test.log.info('this is  {} loop '.format(i))
            test.log.step('1. Load three different server certificatesÂ  and 1 client certificate to module.')
            test.log.info('load client cert to index 0')
            test.expect(test.is_certificate.dstl_upload_certificate_at_index_0(cert_file=cert_file, key_file=key_file))
            for j in range(1, 4):
                test.log.info('load server cert {} to index{}'.format(j, j))
                test.expect(
                    test.is_certificate.dstl_upload_server_certificate(index=j, cert_file=server_cert_file[(j - 1)]))
            test.log.info('check cert amount')
            test.expect(test.is_certificate.dstl_count_uploaded_certificates() == 4)

    def cleanup(test):
        test.expect(test.is_certificate.dstl_delete_all_uploaded_certificates())

if __name__ == "__main__":
    unicorn.main()
