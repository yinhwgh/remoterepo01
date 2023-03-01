#responsible: jun.chen@thalesgroup.com
#location: Beijing
#TC0102357.002

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
        # "1. Upload local module management certificate at index 0.
        # "2. Display current module management certificate.
        # "3. Try to upload client certificate not validated (signed) by management cert.
        # "4. Display installed certificates.
        # "5. Try to upload client certificate validated (signed) by management cert.
        # "6. Display installed certificates.
        # "7. Delete all certificates.

        line_for_better_readability = "===================================================================================="
        test.log.info("Step1. Upload local module management certificate at index 0")
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not.")
        test.expect(not is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is installed, but should not.")
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        key_password_invalid = "pwd_incorrect"
        store_password = "MgntStorePwd"
        sig_type_none = "NONE"
        sig_type_sha256_rsa = "SHA256_RSA"
        key_store_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntKeystore.ks")
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client.der")
        revoke_list_path = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server", "RevokeList.cfg")
        management_cert_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntModuleCert.der")
        certificate = InternetServicesCertificates(test.dut.at1, mode="management_cert")
        certificate.dstl_upload_certificate_at_index_0(management_cert_path)

        test.log.info(line_for_better_readability)
        test.log.info("Step2. Display current module management certificate.")
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not.")
        test.expect(is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is not installed.")
        test.log.info("Switch to security mode 1.")
        signature = InternetServiceSignatures(test.dut, revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        # signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)

        test.log.info(line_for_better_readability)
        test.log.info("Step3. Try to upload client certificate not validated (not signed) by management cert.")
        certificate = InternetServicesCertificates(test.dut.at1, mode="is_cert")
        # sigType=NONE will ignore all signature related parameters.
        certificate.dstl_set_security_private_key(sig_type_none, key_alias, key_password_invalid, key_store_path, store_password)
        certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)

        test.log.info(line_for_better_readability)
        test.log.info("Step4. Display installed certificates.")
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not")
        test.expect(is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is not installed.")

        test.log.info(line_for_better_readability)
        test.log.info("Step5. Try to upload client certificate validated (signed) by management cert.")
        certificate.dstl_set_security_private_key(sig_type_sha256_rsa, key_alias, key_password, key_store_path, store_password)
        certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)

        test.log.info(line_for_better_readability)
        test.log.info("Step6. Display installed certificates.")
        test.expect(is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is not installed.")
        test.expect(is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is not installed.")

        test.log.info(line_for_better_readability)
        test.log.info("Step7. Delete all certificates.")
        signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        certificate = InternetServicesCertificates(test.dut.at1, mode="is_cert")
        certificate.dstl_delete_certificate(0)
        certificate = InternetServicesCertificates(test.dut.at1, mode="management_cert")
        certificate.dstl_delete_certificate(0)
        test.expect(not is_client_cert_installed(test.dut.at1), critical=True, msg="Client certificate is installed, but should not.")
        test.expect(not is_management_cert_installed(test.dut.at1), critical=True, msg="Management certificate is installed, but should not.")

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
