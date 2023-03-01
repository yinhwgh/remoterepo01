#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0104493.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_identification import dstl_get_bootloader
from os.path import join
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):

        test.log.step("1. Set command value of AT^SCFG=\"MEopMode/Factory\",\"none\" and restart the module.")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"none\"", ".*OK.*"))
        test.expect(dstl_restart(test.dut))

        if test.dut.project == 'VIPER':
            test.step2to6(True)
        else:
            test.step2to6(False)

    def cleanup(test):
        pass

    def step2to6(test, test_management_cert=False):
        if test_management_cert==False:
            test.certificates = InternetServicesCertificates(test.dut)
            test.certificates.dstl_delete_all_certificates_using_ssecua()
            test.log.step("2. Load client certificate and server public certificate on module.")
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)
            test.certificates.dstl_upload_certificate_at_index_0(
                join("openssl_certificates", "client.der"),
                join("openssl_certificates", "private_client_key"))
            test.certificates.dstl_upload_server_certificate("1", join("openssl_certificates",
                                                                       "certificate_conf_1.der"))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

            test.log.step("3. Restart the module and check if certificate has been kept unchanged.")
            test.expect(dstl_restart(test.dut))
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)

            test.log.step(
                "4. Execute AT^SCFG=\"MEopMode/Factory\",\"all\" command and restart the module.")
            test.expect(dstl_enter_pin(test.dut))
            test.sleep(3)
            test.expect(test.dut.dstl_reset_to_factory_default())
            test.expect(dstl_restart(test.dut))

            test.log.step("5. Check if certificate has been kept unchanged.")
            test.expect(test.certificates.dstl_count_uploaded_certificates() == 2)
            try:
                test.log.step("6. Remove certificates from module. ")
                test.certificates.dstl_delete_certificate("1")
                test.certificates.dstl_delete_certificate("0")
                test.log.info("Check if certificates are removed")
                if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                                   msg="Wrong amount of certificates installed"):
                    test.certificates.dstl_delete_all_certificates_using_ssecua()
            except AttributeError:
                test.log.error("InternetServicesCertificates was not created.")
        else:
            test.management_certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                                  mode="management_cert")
            management_cert_path = join("management_certificate", "MgntModuleCert.der")

            test.log.step("2. Load managment certificate and server public certificate on module.")
            test.management_certificate.dstl_delete_certificate(0)
            test.expect(test.management_certificate.dstl_count_uploaded_certificates() == 0)
            test.management_certificate.dstl_upload_certificate_at_index_0(management_cert_path)

            test.expect(test.management_certificate.dstl_count_uploaded_certificates() == 1)

            test.log.step("3. Restart the module and check if certificate has been kept unchanged.")
            test.expect(dstl_restart(test.dut))
            test.expect(test.management_certificate.dstl_count_uploaded_certificates() == 1)

            test.log.step(
                "4. Execute AT^SCFG=\"MEopMode/Factory\",\"all\" command and restart the module.")
            test.expect(dstl_enter_pin(test.dut))
            test.sleep(3)
            test.expect(test.dut.dstl_reset_to_factory_default())
            test.expect(dstl_restart(test.dut))

            test.log.step("5. Check if certificate has been kept unchanged.")
            test.expect(test.management_certificate.dstl_count_uploaded_certificates() == 1)
            test.log.step("6. Remove certificates from module. ")
            test.log.info("Delete management certificate.")
            test.management_certificate.dstl_delete_certificate(0)
            test.expect(test.management_certificate.dstl_count_uploaded_certificates() == 0,
                        msg="Wrong amount of certificates installed")


if "__main__" == __name__:
   unicorn.main()