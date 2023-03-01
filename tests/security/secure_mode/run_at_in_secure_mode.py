#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105244.001

import unicorn
from core.basetest import BaseTest
from os.path import join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary import init

class Test(BaseTest):
    '''
    TC0105244.001 - RunAtInSecureMode
    Test case to check AT^SSECRUN command
    '''
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        key_alias = "CinterionMgnt"
        key_password = "MgntKeyPwd"
        store_password = "MgntStorePwd"
        test.log.step('1-2. Load management certificate to module')
        test.certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                   mode="management_cert")
        key_store_path = join(test.certificate.certificates_path, "management_certificate",
                              "MgntKeystore.ks")
        revoke_list_path = join(test.certificate.certificates_path, "echo_certificates", "server",
                                "RevokeList.cfg")
        management_cert_path = join(test.certificate.certificates_path,"management_certificate", "MgntModuleCert.der")
        test.certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.expect(test.is_management_cert_installed(), critical=True,
                    msg="Management certificate is not installed.")

        test.log.step('3-4.Enable secure mode 1')
        signature = InternetServiceSignatures(test.dut, revoke_list_path)
        signature.dstl_set_security_parameters(key_alias, key_password, key_store_path, store_password)
        signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",1'))

        test.log.step('5-7. Run AT^SSECRUN="sign",<at-command-signature>, enter the atc')
        atc_to_test=r'AT^SCFG=\"Tcp/TLS/Version\"'
        atc_to_send = 'AT^SCFG="Tcp/TLS/Version"'
        test.expect(signature.dstl_sign_at_command_with_signature('AT^SSECUC="SEC/LEVEL","TLS","0x0002"'))
        test.expect(signature.dstl_sign_at_command_without_signature(atc_to_test))
        test.expect(test.dut.at1.send_and_verify(atc_to_send,'OK'))

        test.log.step('8-9. Run AT^SSECRUN="sign",<concatenated-at-command>, enter the atc')
        command_with_sign=signature.dstl_sign_at_command_without_signature_concatenated(atc_to_test)
        cmd_to_send=command_with_sign
        test.expect(test.dut.at1.send_and_verify(cmd_to_send, 'OK'))

        test.log.step('10-12. Run AT^SSECRUN="sign",<at-command-signature>, with a wrong signature')
        test.expect(test.dut.at1.send_and_verify('AT^SSECRUN="sign","XXXXXX"','OK'))
        test.expect(test.dut.at1.send_and_verify(atc_to_send, 'ERROR'))

        test.log.step('13-14. Run AT^SSECRUN="sign",<at-command-signature>, with a wrong format')
        test.expect(test.dut.at1.send_and_verify('AT^SSECRUN="sign","XXXXXX";^SCFG="Tcp/TLS/Version"','ERROR'))

        test.log.step('15-17. Run AT^SSECRUN="sign",; with a normal at command')
        test.expect(signature.dstl_sign_at_command_without_signature('ATI'))
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))

        test.log.step('18-20. Run AT^SSECRUN="sign",<at-command-signature> asc0, enter at on asc1')
        test.expect(signature.dstl_sign_at_command_without_signature(atc_to_test))
        test.expect(test.dut.at2.send_and_verify(atc_to_send, 'ERROR'))

        test.log.step('21-22. No enter AT^SSECRUN="sign",<at-command-signature>, '
                      'enter the at command in protect')
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
        test.expect(test.dut.at1.send_and_verify(atc_to_send, 'ERROR'))

        test.log.step('23. Quit secure mode')
        signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))

    def cleanup(test):
        test.certificate.dstl_delete_certificate(0)
        test.expect(test.is_management_cert_installed()==False)

    def is_management_cert_installed(test):
        cert_size = int(test.certificate.dstl_get_certificate_size(0))
        if cert_size > 0:
            return True
        return False


if __name__=='__main__':
    unicorn.main()
