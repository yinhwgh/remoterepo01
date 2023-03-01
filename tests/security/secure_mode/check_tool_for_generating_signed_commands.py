# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0105246.001

import unicorn
from core.basetest import BaseTest
from os.path import join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0105246.001 - CheckToolforGeneratingSignedCommands
    Check Tool for Generating Signed Commands hasn_gen.jar
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        store_password = "MgntStorePwd"
        test.log.step('0. Load management certificate to module')
        test.certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                        mode="management_cert")
        key_store_path = join(test.certificate.certificates_path, "management_certificate",
                              "MgntKeystore.ks")
        revoke_list_path = join(test.certificate.certificates_path, "echo_certificates", "server",
                                "RevokeList.cfg")
        management_cert_path = join(test.certificate.certificates_path, "management_certificate",
                                    "MgntModuleCert.der")
        test.certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.expect(test.is_management_cert_installed(), critical=True,
                    msg="Management certificate is not installed.")

        test.log.step('1.Generation of signed protected command for AT^SSECUC')
        signature = InternetServiceSignatures(test.dut, revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path,
                                               store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",1'))

        test.log.step(
            '2.Generation of signed protected command that is run using AT^SSECRUN,seperated')
        atc_to_test = r'AT^SCFG=\"Tcp/TLS/Version\"'
        atc_to_send = 'AT^SCFG="Tcp/TLS/Version"'
        test.expect(
            signature.dstl_sign_at_command_with_signature('AT^SSECUC="SEC/LEVEL","TLS","0x0002"'))
        test.log.step('2.1 Check the command is under protect')
        test.expect(test.dut.at1.send_and_verify(atc_to_send, 'ERROR'))
        test.log.step('2.2 Sign and send again')
        test.expect(signature.dstl_sign_at_command_without_signature(atc_to_test))
        test.expect(test.dut.at1.send_and_verify(atc_to_send, 'OK'))

        test.log.step(
            '3.Generation of signed protected command that is run using AT^SSECRUN,concatenated')
        test.expect(test.dut.at1.send_and_verify(atc_to_send, 'ERROR'))
        command_with_sign = signature.dstl_sign_at_command_without_signature_concatenated(
            atc_to_test)
        test.expect(test.dut.at1.send_and_verify(command_with_sign, 'OK'))

        test.log.step('4. Quit secure mode')
        signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))

    def cleanup(test):
        test.log.step('5. delete management certificate from module')
        test.certificate.dstl_delete_certificate(0)
        test.expect(test.is_management_cert_installed() == False)

    def is_management_cert_installed(test):
        cert_size = int(test.certificate.dstl_get_certificate_size(0))
        if cert_size > 0:
            return True
        return False


if __name__ == '__main__':
    unicorn.main()
