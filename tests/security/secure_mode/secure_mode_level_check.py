#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105245.001

import unicorn
from core.basetest import BaseTest
from os.path import dirname, realpath, join
from dstl.security.internet_service_signature import InternetServiceSignatures, sec_constans
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0105245.001 - SecureModeLevelCheck
    Test case to check AT^SSECUC="SEC/LEVEL",<signature>,<sectag>,<secmap>
    '''
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step('0. Load management certificate to module')
        management_cert_path = join("management_certificate", "MgntModuleCert.der")
        test.certificate = InternetServicesCertificates(test.dut, device_interface="at1",
                                                   mode="management_cert")
        test.certificate.dstl_upload_certificate_at_index_0(management_cert_path)
        test.expect(is_management_cert_installed(test.dut), critical=True,
                    msg="Management certificate is not installed.")
        test.log.step('1. Select a signature and secure mode')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/MODE"','SSECUC: "SEC/MODE",0.*OK.*'))
        test.log.step('2. Check the different value of <secmap> by <sectag> "TLS"')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"TLS","0x0001"','OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan",.*'))
        test.log.step('3. Check the different value of <secmap> by <sectag> "DevMan"')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"DevMan","0x0002"','OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan","0x0002"'))
        #Skipped step4 for LM change
        test.log.step('4. Non-Volatile check, skipped')
        test.log.step('5. Change back to default value for "TLS" and "DevMan".')
        test.expect(
            test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"DevMan","0xFFFF"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan","0xFFFF"'))
        test.expect(
            test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"TLS","0x0001"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan","0xFFFF"'))
        test.log.step('6. Change secmap of TLS to 0x03.')
        test.expect(
            test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"TLS","0x0003"', 'OK'))
        test.log.step('7. Make sure the secmap DevMan is not changed.')
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan","0xFFFF"'))

        test.log.step('Change back to default value for "TLS" and "DevMan".')
        test.expect(
            test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa,"DevMan","0x0001"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SSECUC="SEC/LEVEL",aaa',
                                                 'SSECUC: "SEC/LEVEL",,"DevMan","0x0001"'))

    def cleanup(test):
        test.certificate.dstl_delete_certificate(0)
        test.expect(is_management_cert_installed(test.dut)==False)

def is_management_cert_installed(device):
    certificate = InternetServicesCertificates(device, device_interface="at1", mode="management_cert")
    cert_size = int(certificate.dstl_get_certificate_size(0))
    if cert_size > 0:
        return True
    return False


if __name__=='__main__':
    unicorn.main()
