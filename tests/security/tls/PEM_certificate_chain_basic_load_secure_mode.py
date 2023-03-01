# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105916.001

import unicorn

from os.path import realpath, dirname, join
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
import subprocess
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans


class Test(BaseTest):
    """
    TC name:
    TC0105916.001 - PEM_certificate_chain_basic_load_secure_mode

    Intention:
    to check possibility of installing PEM certificate chains on module with secure mode
    """

    def setup(test):

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

        test.test_files_path = join(dirname(dirname(dirname(dirname(realpath(__file__))))),
                                    "tests", "test_files", "certificates")
        test.certificates = InternetServicesCertificates(test.dut)
        test.signatures = InternetServiceSignatures(test.dut)

    def run(test):

        test.log.step("0. Execute for certificates pas expiration date")
        for not_expired in range(2):
            if test.certificates.dstl_count_uploaded_certificates() is not 0:
                test.certificates.dstl_delete_all_uploaded_certificates()
            if not_expired == 0:
                certificate = "clientChainExp.pem"
            else:
                certificate = "clientChain.pem"

            test.log.step("1. Try to upload client certificate in PEM at index different from zero "
                          "e.g. at index 1.")
            test.certificates.dstl_set_security_private_key\
                ("SHA256_RSA", "client", "pwdclient", join(test.certificates.certificates_path,
                                                           "certificate_chain", "client.ks"),
                 "pwdclient")

            test.upload_client_certificate_at_any_index((join(test.test_files_path,
                                                              "certificate_chain", certificate)),
                                                        (join(test.test_files_path,
                                                              "certificate_chain", "client.key"))
                                                        , index=1)

            if test.certificates.dstl_count_uploaded_certificates() is not 0:
                test.expect(False, msg="Wrong amount of certificates installed")
                for index in range(10, 0, -1):
                    test.certificates.dstl_delete_certificate(index)

            test.log.step("2. Upload client certificate chain in PEM format at index 0.")
            test.certificates.dstl_upload_certificate_at_index_0(
                (join(test.certificates.certificates_path, "certificate_chain", certificate)),
                (join(test.certificates.certificates_path, "certificate_chain", "client.key")))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

            test.log.step("3. Upload server certificate chain in PEM format to all available "
                          "indexes. If PEM server certificates not supported, install only "
                          "one in DER format")
            test.certificates.dstl_upload_server_certificate(1, join("openssl_certificates",
                                                                     "certificate_conf_1.der"))
            test.certificates.dstl_upload_server_certificate(2, join("openssl_certificates",
                                                                     "certificate_conf_1.der"))

            test.expect(test.certificates.dstl_count_uploaded_certificates() == 3)

            test.log.step("4. Delete client certificate.")
            test.certificates.dstl_delete_certificate(0)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

            test.log.step("5. Delete server certificate.")
            test.certificates.dstl_delete_certificate(1)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

            test.log.step("6. Install management certificate")
            test.upload_cert_secure_mode(
                (join(test.test_files_path, "management_certificate", "management_cert_pub.der")),
                keystore=(join(test.test_files_path, "management_certificate",
                               "management_cert.ks")))

            test.log.step("7. Activate legacy Secure mode (certificate and IMEI).")
            test.signatures.dstl_set_security_parameters("management_cert", "pwd_management01",
                                                         join(test.test_files_path,
                                                              "management_certificate",
                                                              "management_cert.ks"),
                                                         "pwd_management02")
            test.signatures.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)

            test.log.step("8. Try to upload new client certificate in PEM format which has "
                          "different password.")
            test.certificates.dstl_set_security_private_key\
                ("SHA256_RSA", "client", "pwdclient", join(test.certificates.certificates_path,
                                                           "certificate_chain", "client.ks"),
                 "pwdclient")
            test.certificates.dstl_upload_certificate_at_index_0(
                (join(test.certificates.certificates_path, "certificate_chain", certificate)),
                (join(test.certificates.certificates_path, "certificate_chain", "client.key")))

            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

            test.log.step("9. Try to delete server certificate with old password.")
            test.certificates.dstl_delete_certificate(2)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

            test.log.step("10. Try to install server certificate chain in PEM format with old "
                          "password.(if supported)")
            test.log.info("PEM server certificates are not supported")

            test.log.step("11. Delete all client and server certificates with new password.")
            test.certificates.dstl_set_security_private_key("SHA256_RSA", "management_cert",
                                                            "pwd_management01",
                                                            join(test.test_files_path,
                                                                 "management_certificate",
                                                                 "management_cert.ks"),
                                                            "pwd_management02")

            test.certificates.dstl_delete_certificate(2)
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 1)

            test.log.step("12. Try to upload client certificate with wrong IMEI.")
            correct_imei = test.certificates.imei
            test.certificates.imei = "000000000000006"

            test.certificates.dstl_upload_certificate_at_index_0(
                (join(test.certificates.certificates_path, "certificate_chain", certificate)),
                (join(test.certificates.certificates_path, "certificate_chain", "client.key")))

            test.certificates.imei = correct_imei
            if not test.certificates.dstl_count_uploaded_certificates() == 1:
                test.expect(False, msg="Wrong amount of certificates installed")
                test.log.info("Removing certificate here, as it should not be installed")
                test.certificates.dstl_delete_certificate(0)

            test.log.step("13. Upload client certificate in PEM format")
            test.certificates.dstl_upload_certificate_at_index_0(
                (join(test.certificates.certificates_path, "certificate_chain", certificate)),
                (join(test.certificates.certificates_path, "certificate_chain", "client.key")))

            test.log.step("14. Deactivate Secure mode.")
            test.signatures.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)

            test.log.step("15. Delete management certificate.")
            test.upload_cert_secure_mode(
                (join(test.test_files_path, "management_certificate", "management_cert_pub.der")),
                keystore=(join(test.test_files_path, "management_certificate",
                               "management_cert.ks")),
                cmd="delcert")

            test.log.step("16. delete all installed certificates")
            test.certificates.dstl_delete_all_uploaded_certificates()
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

            if not_expired == 0:
                test.log.step("17. Repeat test with certificates before expiration date")

    def cleanup(test):
        try:
            test.signatures.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)
        except AttributeError:
            test.log.error("problem with certificates.")

        try:
            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.certificates.dstl_delete_all_uploaded_certificates()

            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.expect(False, msg="still wrong amount of certificates installed")

                test.certificates.dstl_delete_all_certificates_using_ssecua()

        except AttributeError:
            test.log.error("problem with certificates.")

    def upload_client_certificate_at_any_index(test, cert_file, key_file=None, index=0):
        """Method is loading client certificate at wrong index
        """
        test.dut.at1.close()
        key_file_command = " -keyfile \"{}\"".format(key_file)
        command_string ="\"{}\" -jar \"{}\" -serialPort {} -serialSpd {} -cmd writecert " \
                        "-certfile \"{}\" -certIndex {} " \
                        "-imei {} {} -mode {} {}".format(test.certificates.java_exe,
                                                           test.certificates.ip_cert_manager,
                                                           test.certificates.port_name,
                                                           test.certificates.serial_speed,
                                                           cert_file,
                                                           index,
                                                           test.certificates.imei,
                                                           key_file_command,
                                                           test.certificates.mode,
                                                           " ".join(test.certificates.
                                                                    security_private_key))
        test.log.info(command_string)
        subprocess.run(command_string)
        test.dut.at1.open()

    def upload_cert_secure_mode(test, cert_file, managament=True, index=0, alias="management_cert",
                                keypass="pwd_management01", cmd="writecert",
                                keystore=None, storepass="pwd_management02",
                                keyfile=""):
        test.dut.at1.close()

        if managament:
            managament_command = " -mode management_cert"
        else:
            managament_command = ""

        test.log.info("\"{}\" -jar \"{}\" -serialPort {} -serialSpd {} -cmd {} -certfile \"{}\" "
                       "-certIndex {} -imei {} -alias {} -keypass {} -keystore {} -storepass "
                       "{} {} {}".
                       format(test.certificates.java_exe,
                              test.certificates.ip_cert_manager,
                              test.certificates.port_name,
                              test.certificates.serial_speed,
                              cmd,
                              cert_file,
                              index,
                              test.certificates.imei,
                              alias,
                              keypass,
                              keystore,
                              storepass,
                              managament_command,
                              keyfile))
        subprocess.run("\"{}\" -jar \"{}\" -serialPort {} -serialSpd {} -cmd {} -certfile \"{}\" "
                       "-certIndex {} -imei {} -alias {} -keypass {} -keystore {} -storepass "
                       "{} {} {}".
                       format(test.certificates.java_exe,
                              test.certificates.ip_cert_manager,
                              test.certificates.port_name,
                              test.certificates.serial_speed,
                              cmd,
                              cert_file,
                              index,
                              test.certificates.imei,
                              alias,
                              keypass,
                              keystore,
                              storepass,
                              managament_command,
                              keyfile))
        test.dut.at1.open()


if __name__ == "__main__":
    unicorn.main()
