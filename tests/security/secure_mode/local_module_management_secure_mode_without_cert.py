#responsible: jun.chen@thalesgroup.com
#location: Beijing
#TC0102364.001

import random
import string
import time
from os.path import join

import unicorn
import os

from core.basetest import BaseTest
from os.path import dirname, realpath, join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        # Uploading digital certificate for local module management and activation of secure mode.
        # "1. Display current module management certificate." +
        # "2. Try to use AT command AT^SBNW which need to be validated by certificate (e.g upload client certificate)."
        # "3. Check if client certificate is uploaded and there is no management certificate."
        # "4. Delete client certificate."

        line_for_better_readability = "-------------------------------------------------------------------------------"
        test.log.info("Step1. Display current module management certificate.")
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not.")
        test.expect(not is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is installed, but should not.")

        test.log.info(line_for_better_readability)
        test.log.info("Step2. Try to use AT command AT^SBNW which need to be validated by certificate (e.g upload client certificate).")
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        store_password = "MgntStorePwd"
        key_store_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntKeystore.ks")
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client.der")
        revoke_list_path = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server", "RevokeList.cfg")
        management_cert_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntModuleCert.der")
        certificate = InternetServicesCertificates(test.dut.at1, mode="is_cert")
        certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)

        test.log.info(line_for_better_readability)
        test.log.info("Step3. Check if client certificate is uploaded and there is no management certificate.")
        test.expect(is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is not installed.")
        test.expect(not is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is installed, but should not.")

        test.log.info(line_for_better_readability)
        test.log.info("Step4. Delete client certificate.")
        certificate.dstl_delete_certificate(0)
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not.")


        # test.log.info("Upload management certificate.")
        #
        # # management_certificate.dstl_set_security_private_key(None, key_alias, key_password, key_store_path, store_password)
        # management_certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        # test.log.info("Switch to security mode.")
        # signature = InternetServiceSignatures(test.dut,  revoke_list_path)
        # signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        # # signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        # # signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        #
        # management_certificate.dstl_get_certificate_size(0)
        # print("size after:" + management_certificate.dstl_get_certificate_size(0))
        # count = management_certificate.dstl_count_uploaded_certificates()
        # print(is_management_cert_installed(test.dut.at1))
        #
        #
        # management_certificate.dstl_delete_certificate(0)
        #
        # management_certificate.dstl_get_certificate_size(0)
        # print("size final:" + management_certificate.dstl_get_certificate_size(0))
        # count = management_certificate.dstl_count_uploaded_certificates()
        # print(is_management_cert_installed(test.dut.at1))

    def cleanup(test):
        pass

def is_management_cert_installed(com_port):
    certificate = InternetServicesCertificates(com_port, mode="management_cert")
    cert_size = int(certificate.dstl_get_certificate_size(0))
    if cert_size > 0:
        return True
    return False

def is_client_cert_installed(com_port):
    certificate = InternetServicesCertificates(com_port, mode="is_cert")
    cert_size = int(certificate.dstl_get_certificate_size(0))
    if cert_size > 0:
        return True
    return False

if(__name__ == "__main__"):
    unicorn.main()
