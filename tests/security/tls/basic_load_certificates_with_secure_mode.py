#responsible: dominik.tanderys@globallogic.com
#Wroclaw
#TC TC0104875.001

import unicorn

from os.path import realpath, dirname, join
from core.basetest import BaseTest
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
import subprocess


class Test(BaseTest):
    """
    TC name:
    TC0104875.001 - BasicLoadCertificatesWithSecureMode

    Intention:
    Uploading of client,server and management certificates to the module and to test basic functionalities like read,
    overwrite and deleting.
    Test case for products with management certificate and additional Secure Mode (AT^SSECUC="SEC/MODE") functionality.

    description:
    1. Upload client certificate at index different from zero e.g. at index 1.
    2. Upload client certificate at index 0.
    3. Upload server certificate on indexes 1-10.
    4. Delete client certificate.
    5. Delete server certificate.
    6. Install management certificate
    7. Activate legacy Secure mode (certificate and IMEI).
    8. Try to upload new client certificate which has different password.
    9. Try to delete server certificate with old password.
    10. Try to install server certificate with old password.
    11. Delete all client and server certificates with new password.
    12. Try to upload client certificate with wrong IMEI.
    13. Deactivate Secure mode.
    14. Delete management certificate.

    location:
    Wroclaw

    author:
    Dominik Tanderys dominik.tanderys@globallogic.com
    """

    def setup(test):

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

        test.test_files_path = join(dirname(dirname(dirname(dirname(realpath(__file__))))),
                                    "tests", "test_files", "certificates")
        test.certificates = InternetServicesCertificates(test.dut)

    def run(test):

        test.log.step("1. Upload client certificate at index different from zero e.g. at index 1.")
        test.certificates.dstl_set_security_private_key\
            ("NONE", "client", "pwdclient", join("openssl_certificates", "client.ks"), "pwdclient")

        test.upload_client_certificate_at_any_index((join(test.test_files_path, "openssl_certificates", "client.der")),
                                                    (join(test.test_files_path, "openssl_certificates", "private_client_key"))
                                                    , managament=False, index=1)

        if test.certificates.dstl_count_uploaded_certificates() is not 0:
            test.expect(False, msg="Wrong amount of certificates installed")
            for i in range(10, 0, -1):
                test.certificates.dstl_delete_certificate(i)

        test.log.step("2. Upload client certificate at index 0.")

        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")),
            (join("openssl_certificates", "private_client_key")))

        test.expect(test.certificates.dstl_count_uploaded_certificates() == 1,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Upload server certificate on indexes 1-10.")

        for i in range(1, 11):
            test.certificates.dstl_upload_server_certificate(i, join("openssl_certificates",
                                                                     "certificate_conf_1.der"))

        test.expect(test.certificates.dstl_count_uploaded_certificates() == 11,
                    msg="Wrong amount of certificates installed")

        test.log.step("4. Delete client certificate.")
        test.certificates.dstl_delete_certificate(0)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 10,
                    msg="Wrong amount of certificates installed")

        test.log.step("5. Delete server certificate.")
        test.certificates.dstl_delete_certificate(7)
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 9,
                    msg="Wrong amount of certificates installed")

        test.log.step("6. Install management certificate")
        test.upload_cert_secure_mode((join(test.test_files_path, "management_certificate", "management_cert_pub.der")),
                                     keystore=(join(test.test_files_path, "management_certificate",
                                                    "management_cert.ks")))

        test.log.step("7. Activate legacy Secure mode (certificate and IMEI).")

        test.sec_mode_command = test.generate_signed_command(keystore=join(test.test_files_path,
                                                                           "management_certificate",
                                                                           "management_cert.ks"))
        test.expect(test.dut.at1.send_and_verify(test.sec_mode_command, wait_for="OK"))

        test.sec_mode_command = test.generate_signed_command(
            keystore=join(test.test_files_path, "management_certificate", "management_cert.ks"),
            command_string="AT^SSECUC=\"SEC/MODE\",0")

        test.log.step("8. Try to upload new client certificate which has different password.")
        test.certificates.dstl_set_security_private_key("SHA256_RSA", "client", "pwdclient",
                                                        join("openssl_certificates", "client.ks"), "wrongpass")
        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")),
            (join("openssl_certificates", "private_client_key")))

        if not test.certificates.dstl_count_uploaded_certificates() == 9:
            test.expect(False, msg="Wrong amount of certificates installed")
            test.log.info("Removing certificate here, as it should not be installed")
            test.certificates.dstl_delete_certificate(0)

        test.log.step("9. Try to delete server certificate with old password.")
        test.certificates.dstl_set_security_private_key("SHA256_RSA", "client", "pwdclient",
                                                        join("openssl_certificates", "client.ks"), "pwdclient")
        test.certificates.dstl_delete_certificate(6)

        test.expect(test.certificates.dstl_count_uploaded_certificates() == 9,
                    msg="Wrong amount of certificates installed")

        test.log.step("10. Try to install server certificate with old password.")
        test.certificates.dstl_upload_server_certificate(7, join("openssl_certificates",
                                                                 "certificate_conf_1.der"))

        test.expect(test.certificates.dstl_count_uploaded_certificates() == 9,
                    msg="Wrong amount of certificates installed")

        test.log.step("11. Delete all client and server certificates with new password.")
        test.certificates.dstl_set_security_private_key("SHA256_RSA", "management_cert", "pwd_management01",
                                                        join("management_certificate",
                                                             "management_cert.ks"),
                                                        "pwd_management02")

        for i in range(0, 11):
            test.certificates.dstl_delete_certificate(i)

        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                msg="Wrong amount of certificates installed")

        test.log.step("12. Try to upload client certificate with wrong IMEI.")
        correct_imei = test.certificates.imei
        test.certificates.imei = "000000000000006"

        test.certificates.dstl_upload_certificate_at_index_0(
            (join("openssl_certificates", "client.der")),
            (join("openssl_certificates", "private_client_key")))

        test.certificates.imei = correct_imei
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.expect(False, msg="Wrong amount of certificates installed")
            test.log.info("Removing certificate here, as it should not be installed")
            test.certificates.dstl_delete_certificate(0)


    def cleanup(test):
        test.log.step("13. Deactivate Secure mode.")
        try:
            test.expect(test.dut.at1.send_and_verify(test.sec_mode_command, wait_for="OK"))
        except AttributeError:
            test.log.error("problem with sending commands.")

        test.log.step("14. Delete management certificate.")
        test.upload_cert_secure_mode((join(test.test_files_path, "management_certificate", "management_cert_pub.der")),
                                     keystore=(join(test.test_files_path, "management_certificate",
                                                   "management_cert.ks")),
                                     cmd="delcert")
        try:
            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.expect(False, msg="Wrong amount of certificates installed")

                test.dut.at1.send("AT^SSECUA=\"CertStore/TLS/DeleteAllServer\"")
                test.dut.at1.wait_for(".*O.*")
                test.dut.at1.send("AT^SSECUA=\"CertStore/TLS/DeleteAllClient\"")
                test.dut.at1.wait_for(".*O.*")

            if not test.certificates.dstl_count_uploaded_certificates() == 0:
                test.expect(False, msg="still wrong amount of certificates installed")

                for i in range(10, 0, -1):
                    test.certificates.dstl_delete_certificate(i)

        except AttributeError:
            test.log.error("problem with certificates.")

    def upload_client_certificate_at_any_index(test, cert_file, key_file=None, managament=None, index=0):
        # author: mariusz.piekarski1@globallogic.com, modified: dominik.tanderys@globallogic.com
        """Method is loading client certificate at wrong index
        """
        test.dut.at1.close()
        if key_file:
            key_file_command = " -keyfile \"{}\"".format(key_file)
        else:
            key_file_command = ""

        if managament:
            managament_command = " -mode management_cert"
        else:
            managament_command = ""

        subprocess.run("\"{}\" -jar \"{}\" -serialPort {} -serialSpd {} -cmd writecert -certfile \"{}\" -certIndex {} "
                       "-imei {} {} -mode {} {} {}".format(test.certificates.java_exe,
                                                           test.certificates.ip_cert_manager,
                                                           test.certificates.port_name,
                                                           test.certificates.serial_speed,
                                                           cert_file,
                                                           index,
                                                           test.certificates.imei,
                                                           key_file_command,
                                                           test.certificates.mode,
                                                           test.certificates.security_private_key,
                                                           managament_command))
        test.dut.at1.open()

    def upload_cert_secure_mode(test, cert_file, managament=True, index=0, alias="management_cert",
                                keypass="pwd_management01", cmd="writecert",keystore=None, storepass="pwd_management02",
                                keyfile=""):
        test.dut.at1.close()

        if managament:
            managament_command = " -mode management_cert"
        else:
            managament_command = ""

        subprocess.run("\"{}\" -jar \"{}\" -serialPort {} -serialSpd {} -cmd {} -certfile \"{}\" -certIndex {} "
                       "-imei {} -alias {} -keypass {} -keystore {} -storepass {} {} {}".
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

    def generate_signed_command(test, command_string="AT^SSECUC=\"SEC/MODE\",2", alias="management_cert",
                                keypass="pwd_management01", keystore="", keystorepass="pwd_management02"):
        test.dut.at1.close()
        hash_gen = join(dirname(dirname(dirname(dirname(realpath(__file__))))), "tests", "test_files", "hash_gen",
                        "hash_gen.jar")
        response = subprocess.run("\"{}\" -jar \"{}\" -cmd {} -alias \"{}\" -keypass {} -keystore {} "
                                  "-keystorepass {} -imei {}".format(test.certificates.java_exe,
                                                           hash_gen,
                                                           command_string,
                                                           alias,
                                                           keypass, keystore, keystorepass,
                                                           test.certificates.imei), stdout=subprocess.PIPE)

        try:
            signed_command = response.stdout.decode('utf-8').split('\n')
            signed_command = signed_command[5].split(" ")
        except IndexError:
            test.expect(False, True, "Problem with generating signed command")
            return None
        else:
            return signed_command[3]


if __name__ == "__main__":
    unicorn.main()
