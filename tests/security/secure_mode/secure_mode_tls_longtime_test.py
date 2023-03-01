# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0105427.002

import unicorn
from core.basetest import BaseTest
from os.path import join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import \
    InternetServicesCertificates
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0105427.002 - SecureModeTLSLongTimeTest
    This test case is used to test the secure mode which protects configuration of TLS security,
    server and basic device identification parameters.
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
        management_cert_path = join(test.certificate.certificates_path, "management_certificate",
                                    "MgntModuleCert.der")
        test.key_file = join(test.certificate.certificates_path,
                        "echo_certificates", "client",
                        "client_priv.der")
        test.cert_file = join(test.certificate.certificates_path,
                         "echo_certificates", "client",
                         "client.der")

        # path to server certificate
        test.server_cert_file_1= join(test.certificate.certificates_path, "echo_certificates", "server",
                                 "1.sec")
        test.server_cert_file_2 = join(test.certificate.certificates_path, "echo_certificates", "server",
                                "2.sec")

        test.certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.expect(test.is_management_cert_installed(), critical=True,
                    msg="Management certificate is not installed.")
        test.signature = InternetServiceSignatures(test.dut, revoke_list_path)
        test.signature.dstl_set_security_parameters(key_alias, key_password, key_store_path,
                                                    store_password)
        test.preconfig_certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                                  mode="preconfig_cert")

        test.log.step('3. Verify sec mode 0 ')
        test.signature.dstl_mode_switch_without_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))

        test.log.step(f'3.1.Set secure tag as TLS and secure map as 0x0001')
        # preconditon
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
                'AT^SSECUC="SEC/LEVEL","TLS","0x0001"', False))
        test.sec_map_check_0001(3, 0, False)

        test.log.step(f'3.7.Set secure tag as TLS and secure map as 0x0002')
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', False))
        test.sec_map_check_0002(3, 0, False)

        test.log.step(f'3.10.Set secure tag as TLS and secure map as 0xFFFF')
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0xFFFF"', False))
        test.sec_map_check_ffff(3, 0, False)
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', False))

        test.log.step('4. Verify sec mode 1 ')
        test.signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITHOUT_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",1'))

        test.log.step(f'4.1.Set secure tag as TLS and secure map as 0x0001')
        # preconditon
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0001"', False))
        test.sec_map_check_0001(4, 1, False)

        test.log.step(f'4.7.Set secure tag as TLS and secure map as 0x0002')
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', False))
        test.sec_map_check_0002(4, 1, False)

        test.log.step(f'4.10.Set secure tag as TLS and secure map as 0xFFFF')
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0xFFFF"', False))
        test.sec_map_check_ffff(4, 1, False)
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', False))

        test.log.step('5. Verify sec mode 2 ')
        test.signature.dstl_mode_switch_without_imei(sec_constans.SECURITY_WITH_IMEI)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",2'))
        test.log.step(f'5.1.Set secure tag as TLS and secure map as 0x0001')
        #preconditon
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0001"', True))
        test.sec_map_check_0001(5, 1, True)

        test.log.step(f'5.7.Set secure tag as TLS and secure map as 0x0002')
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0x0002"', True))
        test.sec_map_check_0002(5, 1, True)

        test.log.step(f'5.10.Set secure tag as TLS and secure map as 0xFFFF')
        test.clear_and_load_cert()
        test.expect(test.signature.dstl_sign_at_command_with_signature(
            'AT^SSECUC="SEC/LEVEL","TLS","0xFFFF"', True))
        test.sec_map_check_ffff(5, 1, True)

    def cleanup(test):
        test.log.step('Quit secure mode')
        test.signature.dstl_mode_switch_with_imei(sec_constans.NON_SECURITY_MODE)
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"', 'SSECUC: "SEC/MODE",0'))
        test.certificate.dstl_delete_certificate(0)
        test.expect(test.is_management_cert_installed() == False)

    def is_management_cert_installed(test):
        cert_size = int(test.certificate.dstl_get_certificate_size(0))
        if cert_size > 0:
            return True
        return False

    def clear_is_store(test):
        test.log.info("Empty IS store certificates.")
        is_certificate = InternetServicesCertificates(test.dut, device_interface="at1")
        is_certificate.dstl_delete_all_uploaded_certificates()

    def clear_and_load_cert(test):
        test.log.info('*** Preconditon for AT^SSECUA="CertStore/TLS/PreconfigureCerts" ***')
        test.clear_is_store()
        test.preconfig_certificate.dstl_upload_certificate_at_index_0(test.cert_file, test.key_file)
        test.preconfig_certificate.dstl_upload_server_certificate(1, test.server_cert_file_1)
        test.preconfig_certificate.dstl_upload_server_certificate(2, test.server_cert_file_2)

    def sec_map_check_0001(test, i, mode, with_imei=False):
        atc_to_test_1 = r'AT^SSECUA="CertStore/TLS/PreconfigureCerts"'
        atc_to_send_1 = 'AT^SSECUA="CertStore/TLS/PreconfigureCerts","xxx"'
        atc_to_test_2 = r'AT^SSECUA="CertStore/TLS/PreconfigureCert",1'
        atc_to_send_2 = 'AT^SSECUA="CertStore/TLS/PreconfigureCert","xxx",1'
        atc_to_test_3 = r'AT^SSECUA="CertStore/TLS/UpdateServerCerts",1'
        atc_to_send_3 = 'AT^SSECUA="CertStore/TLS/UpdateServerCerts","xxx",1'
        atc_to_test_4 = r'AT^SSECUC="CertStore/TLS/UpdateServerCerts/Mode",0'
        atc_to_send_4 = 'AT^SSECUC="CertStore/TLS/UpdateServerCerts/Mode","xxx",0'
        atc_to_test_5 = r'AT^SSECUA="CertStore/Preconfigured/DeleteAll"'
        atc_to_send_5 = 'AT^SSECUA="CertStore/Preconfigured/DeleteAll","xxx"'
        test.check_single_cmd(i, 1, mode, with_imei, atc_to_test_1, atc_to_send_1)
        test.check_single_cmd(i, 2, mode, with_imei, atc_to_test_2, atc_to_send_2)
        test.check_single_cmd(i, 3, mode, with_imei, atc_to_test_3, atc_to_send_3)
        test.check_single_cmd(i, 4, mode, with_imei, atc_to_test_4, atc_to_send_4)
        test.check_single_cmd(i, 5, mode, with_imei, atc_to_test_5, atc_to_send_5)

    def sec_map_check_0002(test, i, mode, with_imei=False):
        atc_to_test_1 = r'AT^SCFG=\"Tcp/TLS/Version\"'
        atc_to_send_1 = 'AT^SCFG="Tcp/TLS/Version"'
        atc_to_test_2 = r'AT^SBNW=\"ciphersuites\",0'
        atc_to_send_2 = 'AT^SBNW="ciphersuites",0'
        test.log.step(f'{i}.8. Check protect of {atc_to_send_1}')
        test.log.step(f'{i}.8.1 Send {atc_to_send_1} with correct sign')
        test.expect(test.signature.dstl_sign_at_command_without_signature(atc_to_test_1, with_imei))
        test.expect(test.dut.at1.send_and_verify(atc_to_send_1, 'OK'))
        test.log.step(f'{i}.8.2 Send {atc_to_send_1} with invalid sign')
        test.expect(test.dut.at1.send_and_verify('AT^SSECRUN="sign","XXXXXX"', 'OK'))
        if mode == 0:
            test.expect(test.dut.at1.send_and_verify(atc_to_send_1, 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify(atc_to_send_1, 'ERROR'))

        test.log.step(f'{i}.9. Check protect of {atc_to_send_2}')
        test.log.step(f'{i}.9.1 Send {atc_to_send_2} with correct sign')
        test.set_ciphersuite("PSK-AES128-CBC-SHA256", mode, with_imei)
        test.expect(test.signature.dstl_sign_at_command_without_signature(atc_to_test_2, with_imei))
        test.expect(test.dut.at1.send_and_verify(atc_to_send_2, 'OK'))

        test.log.step(f'{i}.9.2 Send {atc_to_send_2} with invalid sign')
        test.set_ciphersuite("PSK-AES128-CBC-SHA256", mode, with_imei)
        test.expect(test.dut.at1.send_and_verify('AT^SSECRUN="sign","XXXXXX"', 'OK'))
        if mode == 0:
            test.expect(test.dut.at1.send_and_verify(atc_to_send_2, 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify(atc_to_send_2, 'ERROR'))

    def set_ciphersuite(test, ciphersuite, mode, with_imei):
        if mode !=0:
            test.expect(
                test.signature.dstl_sign_at_command_without_signature(
                    f'AT^SBNW=\\"ciphersuites\\",{len(ciphersuite)}', with_imei))
        test.dut.at1.send("AT^SBNW=\"ciphersuites\",{}".format(len(ciphersuite)))
        test.expect(test.dut.at1.wait_for(".*CIPHERSUITES.*"))
        test.dut.at1.send(ciphersuite, end="")
        test.expect(test.dut.at1.wait_for(".*OK.*"))
        test.dut.at1.send("at^sbnr=\"ciphersuites\", \"current\"")
        test.expect(test.dut.at1.wait_for(ciphersuite))

    def sec_map_check_ffff(test, i, mode, with_imei=False):
        test.sec_map_check_0001(i, mode, with_imei)
        test.sec_map_check_0002(i, mode, with_imei)

    def check_single_cmd(test, i, j, mode, with_imei, cmd_1, cmd_2):
        test.log.step(f'{i}.{j}. Check protect of {cmd_1}')
        test.log.step(f'{i}.{j}.1 Send {cmd_1} with correct sign')
        test.expect(test.signature.dstl_sign_at_command_with_signature(cmd_1, with_imei))

        test.log.step(f'{i}.{j}.2 Send {cmd_1} with invalid sign')
        if mode == 0 and j==1:
            test.clear_and_load_cert()
            test.expect(test.dut.at1.send_and_verify(cmd_2, 'OK'))
        elif mode == 0:
            test.expect(test.dut.at1.send_and_verify(cmd_2, 'OK'))
        else:
            test.expect(test.dut.at1.send_and_verify(cmd_2, 'ERROR'))


if __name__ == '__main__':
    unicorn.main()
