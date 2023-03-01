#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105396.002

import unicorn
from core.basetest import BaseTest
from os.path import join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary import init

class Test(BaseTest):
    '''
    TC0105396.002 - SecureModeTLSErrorCheck
    This test case is used to test the secure mode which
    protects configuration of DM security error check.
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
        test.signature = InternetServiceSignatures(test.dut, revoke_list_path)
        test.signature.dstl_set_security_parameters(key_alias, key_password, key_store_path,
                                               store_password)

        test.log.step('3.Secure mode 0 function check, not protect cmd')
        test.signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))
        test.check_tls_secure_map(3, False, False)

        test.log.step('4.Secure mode 1 function check')
        test.signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",1'))
        test.check_tls_secure_map(4, False, True)
        test.log.step('5.Secure mode 2 function check')
        test.signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",2'))
        test.check_tls_secure_map(5, True, True)

        test.log.step('6. Quit secure mode')
        test.signature.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))

    def cleanup(test):
        test.certificate.dstl_delete_certificate(0)
        test.expect(test.is_management_cert_installed()==False)

    def is_management_cert_installed(test):
        cert_size = int(test.certificate.dstl_get_certificate_size(0))
        if cert_size > 0:
            return True
        return False

    def check_tls_secure_map(test, i, with_imei, is_secure):
        test.log.step('{}.3-4 Set secure tag as TLS and secure map as 0x0001'.format(i))
        test.expect(
            test.signature.dstl_sign_at_command_with_signature('AT^SSECUC="SEC/LEVEL","TLS","0x0001"',with_imei))

        test.log.step('{}.5-7 Check sign and execute AT^SCFG="Tcp/TLS/Version"'.format(i))
        atc_to_test_1=r'AT^SCFG=\"Tcp/TLS/Version\"'
        atc_to_send_1 = 'AT^SCFG="Tcp/TLS/Version"'
        atc_to_test_2 = r'AT^SBNW=\"ciphersuites\",0'
        atc_to_send_2 = 'AT^SBNW="ciphersuites",0'
        atc_to_test_3 = r'AT^SSECUA="CertStore/Preconfigured/DeleteAll"'
        atc_to_send_3 = 'AT^SSECUA="CertStore/Preconfigured/DeleteAll","xxx"'

        test.expect(test.dut.at1.send_and_verify(atc_to_send_1, 'OK'))
        test.expect(test.signature.dstl_sign_at_command_without_signature(atc_to_test_1,with_imei))
        test.expect(test.dut.at1.send_and_verify(atc_to_send_1, 'OK'))

        test.log.step('{}.8 Check sign and execute AT^SBNW="ciphersuites"'.format(i))

        test.set_ciphersuite("PSK-AES128-CBC-SHA256")
        test.expect(test.signature.dstl_sign_at_command_without_signature(atc_to_test_2, with_imei))
        test.expect(test.dut.at1.send_and_verify(atc_to_send_2, 'OK'))

        test.log.step('{}.9 Set secure tag as TLS and secure map as 0x0002'.format(i))
        test.expect(
            test.signature.dstl_sign_at_command_with_signature(
                'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', with_imei))
        test.log.step('{}.10 Check AT^SSECUA="CertStore/Preconfigured/DeleteAll"'.format(i))
        test.expect(test.signature.dstl_sign_at_command_with_signature(atc_to_test_3, with_imei))
        test.expect(test.dut.at1.send_and_verify(atc_to_send_3, 'OK'))

    def set_ciphersuite(test, ciphersuite):
        test.dut.at1.send("at^sbnw=\"ciphersuites\",{}".format(len(ciphersuite)))
        test.expect(test.dut.at1.wait_for(".*CIPHERSUITES.*"))

        test.dut.at1.send(ciphersuite, end="")
        test.expect(test.dut.at1.wait_for(".*OK.*"))

        test.dut.at1.send("at^sbnr=\"ciphersuites\", \"current\"")
        test.expect(test.dut.at1.wait_for(ciphersuite))


if __name__=='__main__':
    unicorn.main()
