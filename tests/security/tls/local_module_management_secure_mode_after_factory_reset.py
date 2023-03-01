#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0104418.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.network_service.register_to_network import dstl_enter_pin
from os.path import join


class Test(BaseTest):
    """
       TC intention: Check if certificate in local module management is persistence after factory reset.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True, msg="PIN code must be successfully entered as the "
                                                                 "factory reset command is PIN protected!")
        test.management_cert_path = join("management_certificate", "management_cert_pub.der")
        test.management_cert = InternetServicesCertificates(test.dut, mode="management_cert")
        if test.management_cert.dstl_count_uploaded_certificates() != 0:
            test.log.info("Trying to remove management certificate as there is already installed")
            test.expect(test.management_cert.dstl_delete_certificate("0"))
            test.expect(test.management_cert.dstl_count_uploaded_certificates() == 0, critical=True)

    def run(test):
        test.log.step("1. Upload local module management certificate at index 0.")
        test.expect(test.management_cert.dstl_upload_certificate_at_index_0(cert_file=test.management_cert_path))

        test.log.step("2. Display current module management certificate.")
        test.expect(test.management_cert.dstl_count_uploaded_certificates() == 1)

        test.log.step("3. Perform factory reset procedure on the module")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"all\"", ".*OK.*"))
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*"))

        test.log.step("4. Display current module management certificate.")
        test.expect(test.management_cert.dstl_count_uploaded_certificates() == 1)

        test.log.step("5. Delete the management certificate. ")
        test.expect(test.management_cert.dstl_delete_certificate("0"))

    def cleanup(test):
        try:
            if test.expect(test.management_cert.dstl_count_uploaded_certificates() == 0):
                test.log.info("The management certificate is deleted correctly")
            else:
                test.management_cert.dstl_delete_certificate("0")
        except AttributeError:
            test.log.error("Certificate object was not created.")


if "__main__" == __name__:
    unicorn.main()
