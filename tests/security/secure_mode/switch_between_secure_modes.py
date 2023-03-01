#responsible: jun.chen@thalesgroup.com
#location: Beijing
#TC0104332.001

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
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.certificates = InternetServicesCertificates(test.dut)

    def run(test):
        # Intension: Check switch function between different secure modes.
        # 1. Switch <secmode> from 0 to 1.  Check secure mode is 1.
        # 2. Switch <secmode> from 1 to 0.  Check secure mode is 0.
        # 3. Switch <secmode> from 0 to 2.  Check secure mode is 2.
        # 4. Switch <secmode> from 2 to 1.  Check secure mode is 1.
        # 5. Switch <secmode> from 1 to 2.  Check secure mode is 2.
        # 6. Switch <secmode> from 2 to 0.  Check secure mode is 0.
        # 7. Delete management certificate.

        line_for_better_readability = "===================================================================================="

        test.log.step("Step0_1 Precondition. Upload client certificate at index 0.")
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")),
            (join("openssl_certificates", "private_client_key")))
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1, msg="Wrong amount of certificates installed")

        test.log.info("Step0_2 Precondition. Upload management certificate.")
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        store_password = "MgntStorePwd"
        key_store_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntKeystore.ks")
        revoke_list_path = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server", "RevokeList.cfg")
        management_cert_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntModuleCert.der")
        certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="management_cert")

        certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.expect(is_management_cert_installed(test.dut), critical=True, msg="Management certificate is not installed.")

        test.log.info(line_for_better_readability)
        test.log.info("Step1-2. Switch <secmode> from 0 to 1.")
        signature = InternetServiceSignatures(test.dut, revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.SECURITY_WITHOUT_IMEI) + ".*"), critical=True)

        test.log.info(line_for_better_readability)
        test.log.info("Step3-4. Switch <secmode> from 1 to 0.")
        signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.NON_SECURITY_MODE) + ".*"), critical=True)

        test.log.info(line_for_better_readability)
        test.log.info("Step5-6. Switch <secmode> from 0 to 2.")
        signature = InternetServiceSignatures(test.dut, revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.SECURITY_WITH_IMEI) + ".*"), critical=True)

        test.log.info(line_for_better_readability)
        test.log.info("Step7-8. Switch <secmode> from 2 to 1.")
        signature.dstl_mode_switch_with_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.SECURITY_WITHOUT_IMEI) + ".*"), critical=True)

        test.log.info(line_for_better_readability)
        test.log.info("Step9-10. Switch <secmode> from 1 to 2.")
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.SECURITY_WITH_IMEI) + ".*"), critical=True)

        test.log.info(line_for_better_readability)
        test.log.info("Step11-12. Switch <secmode> from 2 to 0.")
        signature.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(sec_constans.NON_SECURITY_MODE) + ".*"), critical=True)

        # new add part by chenxiaoyu
        test.log.info('13. Try to switch <secmode> from 0 to 1 with valid <signature> corresponding to secure mode 2.')
        signature.dstl_mode_switch_with_imei(sec_constans.SECURITY_WITHOUT_IMEI, expect_result='ERROR')
        test.log.info('14. Check error message says "wrong signature" and secure mode still is 0.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"",
                                                 ".*" + str(sec_constans.NON_SECURITY_MODE) + ".*"),
                    critical=True)
        test.log.info('15. Try to switch <secmode> from 0 to 1 with an invalid <signature>.')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC=\"SEC/MODE\","sssssssssssssssssssss",1','ERROR'))

        test.log.info('16. Check error message says "wrong signature" and secure mode still is 0.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"",
                                                 ".*" + str(sec_constans.NON_SECURITY_MODE) + ".*"),
                    critical=True)
        test.log.info('17. Try to switch <secmode> from 1 to 2 with valid <signature> corresponding to secure mode 2.')
        # 0 to 1
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(
            sec_constans.SECURITY_WITHOUT_IMEI) + ".*"), critical=True)
        # 1 to 2 fail
        signature.dstl_mode_switch_with_imei(sec_constans.SECURITY_WITH_IMEI, expect_result='ERROR')
        test.log.info('18. Check error message says "wrong signature" and secure mode still is 1.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"",
                            ".*" + str(sec_constans.SECURITY_WITHOUT_IMEI) + ".*"),critical=True)
        test.log.info('19. Try to switch <secmode> from 1 to 2 with an invalid <signature>.')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC=\"SEC/MODE\","sssssssssssssssssssss",2',
                                                 'ERROR'))
        test.log.info('20. Check error message says "wrong signature" and secure mode still is 1.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"",
                            ".*" + str(sec_constans.SECURITY_WITHOUT_IMEI) + ".*"),critical=True)
        test.log.info('21. Try to switch <secmode> from 2 to 0 with valid <signature> corresponding to secure mode 1.')
        # 1 to 2
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(
            sec_constans.SECURITY_WITH_IMEI) + ".*"), critical=True)
        # 2 to 0 fail
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI, expect_result='ERROR')

        test.log.info('22. Check error message says "wrong signature" and secure mode still is 2.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(
            sec_constans.SECURITY_WITH_IMEI) + ".*"), critical=True)
        test.log.info('23. Try to switch <secmode> from 2 to 0 with an invalid <signature>.')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC=\"SEC/MODE\","sssssssssssssssssssss",0',
                                                 'ERROR'))

        test.log.info('24. Check error message says "wrong signature" and secure mode still is 2.')
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"", ".*" + str(
            sec_constans.SECURITY_WITH_IMEI) + ".*"), critical=True)

        test.log.info("Step25. Delete management certificate.")
        signature.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify("AT^SSECUC=\"SEC/MODE\"",
                                                 ".*" + str(sec_constans.NON_SECURITY_MODE) + ".*"),
                    critical=True)
        certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                   mode="management_cert")
        certificate.dstl_delete_certificate(0)
        test.expect(not is_management_cert_installed(test.dut), critical=True,
                    msg="Management certificate is installed, but should not.")

    def cleanup(test):
        pass

def is_management_cert_installed(device):
    certificate = InternetServicesCertificates(device, device_interface="at1", mode="management_cert")
    cert_size = int(certificate.dstl_get_certificate_size(0))
    if cert_size > 0:
        return True
    return False

def is_client_cert_installed(device):
    certificate = InternetServicesCertificates(device, device_interface="at1", mode="management_cert")
    cert_size = int(certificate.dstl_get_certificate_size(0))
    if cert_size > 0:
        return True
    return False

if(__name__ == "__main__"):
    unicorn.main()
