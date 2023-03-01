#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0103885.002

import random
import string
import time
from os.path import join

import unicorn
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from core.basetest import BaseTest
from os.path import dirname, realpath, join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        dstl_get_imei(test.dut)

    def run(test):
        # server_cert_file = []  # path to server certificate
        # for i in range(1, 20):
        #     server_cert_file.append(r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\{}.sec".format(str(i)))
        # revoke_bin_path = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\RevokePrecfgServerCert.bin"  # path to RevokePrecfgServerCert.bin
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))  # current file path.
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        # key_store_path = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\MgntKeystore.ks"  # path to key store
        key_store_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate",
                              "MgntKeystore.ks")
        store_password = "MgntStorePwd"
        # key_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client_priv.der"  # path to private key file
        # cert_file = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\client.der"  # path to client certificate
        # management_cert_path = r"C:\work\Serval\certificate\tools\tools\SecurityCertMgr\MgntModuleCert.der"  # path to managment cetificate file
        test.project_root = dirname(dirname(dirname(dirname(realpath(__file__)))))  # current file path.
        key_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client",
                        "client_priv.der")
        cert_file = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client",
                         "client.der")
        revoke_list_path = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server",
                                "RevokeList.cfg")
        # key_store_path = join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "client", "client.ks")
        management_cert_path = join(test.project_root, "tests", "test_files", "certificates", "management_certificate", "MgntModuleCert.der")
        server_cert_file = []  # path to server certificate
        for i in range(1, 20):
            server_cert_file.append(
                join(test.project_root, "tests", "test_files", "certificates", "echo_certificates", "server",
                     "{}.sec".format(str(i))))

        test.log.info("Empty IS store certificates.")
        is_certificate = InternetServicesCertificates(test.dut, device_interface="at1")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 25):
                test.log.info("Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Empty preconfig store certificates.")
        preconfig_certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="preconfig_cert")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 25):
                size = preconfig_certificate.dstl_get_certificate_size(index)
                test.log.info("Size of No. " + str(index) + " certificate is: " + str(size))
                if size != '0':
                    test.log.info("Delete No. " + str(index) + " preconfig store certificates.")
                    preconfig_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Install preconfig client and server certificates.")
        preconfig_certificate.dstl_upload_certificate_at_index_0(cert_file, key_file)
        test.sleep(30)
        for index in range(1, 4):
            test.log.info("Install No. " + str(index) + " preconfig store server certificate.")
            preconfig_certificate.dstl_upload_server_certificate(index, server_cert_file[index])
            test.sleep(30)
        # test.log.info("Set client private key parameters.")
        # certificate.dstl_set_security_private_key(key_alias, key_password, key_store_path, store_password)
        # test.log.info("Upload client certificate to module.")
        # certificate.dstl_upload_client_certificate(key_file, cert_file, is_cert)
        test.log.info("Upload management certificate.")
        management_certificate = InternetServicesCertificates(test.dut, device_interface="at1", mode="management_cert")
        # management_certificate.dstl_set_security_private_key(None, key_alias, key_password, key_store_path, store_password)
        management_certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.sleep(30)
        test.log.info("Switch to security mode.")
        signature = InternetServiceSignatures(test.dut,  revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.log.info("Initial IS store in security mode with correct signature.")
        test.expect(signature.dstl_initialize_is_store_security_mode(False))
        test.log.info("Check IS store certificates.")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count == 4:
            for index in range(count):
                # index = index + 1
                if preconfig_certificate.dstl_get_certificate_size(index) == is_certificate.dstl_get_certificate_size(index):
                    test.log.info("No." + str(index) + " certificate initial correctly.")
                else:
                    test.expect(False)
                    test.log.info("No. " + str(index) + " certificate initial failed.")
            # test.expect(True)
            # test.log.info("IS store certificates update successful.")
        else:
            test.expect(False)
            test.log.info("IS store certificates initial failed.")
        test.log.info("Delete all certificates in IS store.")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            test.log.info("Switch to non security mode.")
            test.sleep(10)
            signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
            for index in range(0, 25):
                size = is_certificate.dstl_get_certificate_size(index)
                test.log.info(
                    "Size of No. " + str(index) + " certificate is: " + size)
                if not size == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Switch to security mode.")
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.log.info("Initialize IS store in security mode with only selected certificates.")
        for index in range(0, 4):
            test.expect(signature.dstl_initialize_is_store_by_index_security_mode(index, False))
        test.log.info("Count updated certificates numbers")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count == 4:
            for index in range(count):
                index = index + 1
                if preconfig_certificate.dstl_get_certificate_size(index) == is_certificate.dstl_get_certificate_size(index):
                    test.log.info("No." + str(index) + " certificate initial correctly.")
                else:
                    test.expect(False)
                    test.log.info("No. " + str(index) + " certificate initial failed.")
        else:
            test.expect(False)
            test.log.info("Initialize IS store in security mode with only selected certificates failed.")
        test.log.info("Delete server certificates in IS store.")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            test.log.info("Switch to non security mode.")
            signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
            test.sleep(30)
            for index in range(0, 25):
                test.log.info(
                    "Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Switch to security mode.")
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.sleep(30)
        test.log.info("Initialize IS store with wrong signature.")
        incorrect_signature = ''.join(random.sample(string.ascii_letters + string.digits, 20))
        test.dut.at1.send_and_verify("at^ssecua=\"CertStore/TLS/PreconfigureCerts\","
                                     + str(incorrect_signature) + "\"", ".*ERROR.*")

        test.log.info("Switch to non security mode.")
        signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.sleep(30)
        test.log.info("Delete management certificate.")
        management_certificate.dstl_delete_certificate(0)
        test.sleep(30)
        test.log.info("Empty IS store certificates.")
        count = is_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 25):
                test.log.info(
                    "Size of No. " + str(index) + " certificate is: " + is_certificate.dstl_get_certificate_size(index))
                if not is_certificate.dstl_get_certificate_size(index) == '0':
                    test.log.info("Delete No. " + str(index) + " IS store certificates.")
                    is_certificate.dstl_delete_certificate(index)
                    test.sleep(30)
        test.log.info("Empty preconfig store certificates.")
        count = preconfig_certificate.dstl_count_uploaded_certificates()
        if count > 0:
            for index in range(0, 25):
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
