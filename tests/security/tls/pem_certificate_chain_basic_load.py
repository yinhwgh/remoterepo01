# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105915.001

import unicorn

from os.path import realpath, dirname, join
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC name:
    TC0105915.001 - PEM_certificate_chain_basic_load

    Intention:
    to check possibility of installing PEM certificate chains on module
    """

    def setup(test):

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

        test.test_files_path = join(dirname(dirname(dirname(dirname(realpath(__file__))))),
                                    "tests", "test_files", "certificates")
        test.certificates = InternetServicesCertificates(test.dut)

    def run(test):

        if not (test.certificates.dstl_count_uploaded_certificates() == 0):
            test.certificates.dstl_delete_all_uploaded_certificates()

        test.log.step("0. Execute for certificates pas expiration date")
        for not_expired in range(2):
            if not_expired == 0:
                certificate = "clientChainExp.pem"
            else:
                certificate = "clientChain.pem"

            test.log.step(
                "1. Try to upload client certificate in PEM at index different from zero "
                "e.g. at index 1.")

            arguments = ["-serialPort", test.certificates.port_name, "-serialSpd",
                         test.certificates.serial_speed,
                         "-cmd",
                         "writecert",
                         "-certfile",
                         join(test.test_files_path, "certificate_chain", certificate),
                         "-certIndex",
                         "1", "-mode", test.certificates.mode, "-sigType", "SHA256_RSA",
                         "-alias", "client", "-keypass",
                         "pwdclient", "-keystore",
                         join(test.test_files_path, "certificate_chain", "client.ks"),
                         "-storepass", "pwdclient", "-keyfile",
                         join(test.test_files_path, "certificate_chain",
                              "client.key")]
            test.expect(not test.certificates.dstl_execute_ip_cert_mgr_jar(arguments))

            if not test.expect((test.certificates.dstl_count_uploaded_certificates() == 0)):
                for index in range(10, 0, -1):
                    test.certificates.dstl_delete_certificate(index)

            test.log.step("2. Upload client certificate chain in PEM format at index 0.")
            test.certificates.dstl_set_security_private_key \
                ("SHA256_RSA", "client", "pwdclient", join("certificate_chain", "client.ks"),
                 "pwdclient")
            test.expect(test.certificates.dstl_upload_certificate_at_index_0(
                (join("certificate_chain", certificate)),
                (join("certificate_chain", "client.key"))))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                        msg="Wrong amount of certificates installed")

            test.log.step("3. Upload server certificate chain in PEM format to all available "
                          "indexes. If PEM server certificates not supported, install only "
                          "two in DER format")

            for index in range(1, 3):
                test.expect(test.certificates.dstl_upload_server_certificate
                            (index, join("openssl_certificates", "certificate_conf_1.der")))

            test.expect(test.certificates.dstl_count_uploaded_certificates() == 3,
                        msg="Wrong amount of certificates installed")

            test.log.step("4. Delete client certificate.")
            test.expect(test.certificates.dstl_delete_certificate(0))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 2,
                        msg="Wrong amount of certificates installed")

            test.log.step("5. Delete server certificate.")
            test.certificates.dstl_delete_certificate(2)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                        msg="Wrong amount of certificates installed")

            test.log.step("6. Upload new client certificate which has different password.")
            test.certificates.dstl_set_security_private_key("SHA256_RSA", "management_cert",
                                                            "pwd_management01",
                                                            join("management_certificate",
                                                                 "management_cert.ks"),
                                                            "pwd_management02")
            test.expect(test.certificates.dstl_upload_certificate_at_index_0(
                (join("management_certificate", "MgntModuleCert.der")),
                (join("management_certificate", "MgntModuleKey.der"))))

            test.log.step("7. Try to delete server certificate with old password.")
            test.certificates.dstl_set_security_private_key \
                ("SHA256_RSA", "client", "pwdclient", join("certificate_chain", "client.ks"),
                 "pwdclient")
            test.expect(test.certificates.dstl_delete_certificate(1))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                        msg="Wrong amount of certificates installed")

            test.log.step("8. Delete all certificates with new password.")
            test.certificates.dstl_delete_certificate(0)
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0):
                test.log.info("Removing certificate here, as it should not be installed")
                test.certificates.dstl_delete_certificate(0)

        test.log.step("9. Repeat test with certificates before expiration date")

    def cleanup(test):
        try:
            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.certificates.dstl_delete_all_uploaded_certificates()

            if not (test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)):
                for index in range(10, 0, -1):
                    test.certificates.dstl_delete_certificate(index)

        except AttributeError:
            test.log.error("problem with certificates.")

    if __name__ == "__main__":
        unicorn.main()
