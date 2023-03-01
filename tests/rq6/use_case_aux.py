# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian

'''
Aux function for use case script
'''

from core import dstl
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from os.path import join


class OpenSslCertificates(InternetServicesCertificates):
    def __init__(self, device, configuration_id):
        """author: mariusz.piekarski1@globallogic.com
        Class constructor. Initializes class object.
        Parameters
        ----------
        device: device on which certificates will be handled
        configuration_id (1-3): ID of certificates configuration which should be loaded on module.
        The same client certificate will be used for all configurations
        """
        super().__init__(device)
        try:
            self.configuration_id = int(configuration_id)
        except ValueError:
            dstl.log.error("incorrect configuration ID value. Integer is expected.")
        self.client_certificate = join(self.certificates_path, "openssl_certificates", "client.der")
        self.client_private_key = join(self.certificates_path, "openssl_certificates", "private_client_key")
        # self.server_configuration_1 = join(self.certificates_path, "openssl_certificates", "certbinary.txt")
        self.server_configuration_1 = join(self.certificates_path, "openssl_certificates", "certificate_conf_1.der")
        self.server_configuration_2 = join(self.certificates_path, "openssl_certificates", "certificate_conf_2.der")
        self.server_configuration_3a = join(self.certificates_path, "openssl_certificates", "certificate_conf_3a.der")
        self.server_configuration_3b = join(self.certificates_path, "openssl_certificates", "certificate_conf_3b.der")
        self.key_store_file = join(self.certificates_path, "openssl_certificates", "client.ks")

    def dstl_upload_openssl_certificates(self):
        """author: mariusz.piekarski1@globallogic.com
        Method uploads certificates according to given configuration ID parameter.
        Returns
        True in case all certificates were uploaded successfully, False otherwise.
        """
        dstl.log.h2("DSTL: <dstl_upload_openssl_certificates>")
        # result = self.dstl_upload_certificate_at_index_0(self.client_certificate, self.client_private_key)
        result = True
        if self.configuration_id == 1 or self.configuration_id == 4:
            result &= self.dstl_upload_server_certificate(0, self.server_configuration_1)
        elif self.configuration_id == 2:
            result &= self.dstl_upload_server_certificate(1, self.server_configuration_2)
        elif self.configuration_id == 3:
            result &= self.dstl_upload_server_certificate(1, self.server_configuration_3a)
            result &= self.dstl_upload_server_certificate(2, self.server_configuration_3b)
        else:
            dstl.log.error("incorrect configuration ID value. Allowed values: 1, 2, 3.")
            return False
        return result

    def dstl_delete_openssl_certificates(self):
        """author: mariusz.piekarski1@globallogic.com
        Method deletes certificates according to given configuration ID parameter.
        Returns
        True in case all certificates were deleted successfully, False otherwise.
        """
        dstl.log.h2("DSTL: <dstl_delete_openssl_certificates>")
        result = True
        if self.configuration_id == 3:
            result &= self.dstl_delete_certificate(2)
        result &= self.dstl_delete_certificate(1)
        result &= self.dstl_delete_certificate(0)
        return result


def toggle_off_rts(test):
    test.dut.at1.connection.setRTS(False)
    test.sleep(1)
    test.log.info(f"Turn off RTS line,state: {test.dut.at1.connection.rts}")


def toggle_on_rts(test):
    test.dut.at1.connection.setRTS(True)
    test.sleep(1)
    test.log.info(f"Turn on RTS line, state: {test.dut.at1.connection.rts}")


def step_with_error_handle(max_retry, step_if_error):
    def wrapper(func):
        def retry(test, force_abnormal_flow, *args, **kw):
            if force_abnormal_flow:
                toggle_off_rts(test)
            i = 0
            while i < max_retry:
                test.log.info(f'Execute step: {func.__name__}, the {i + 1} time')
                result = func(test, force_abnormal_flow, *args, **kw)
                if result:
                    return True
                else:
                    i += 1
                    test.sleep(2)
            toggle_on_rts(test)
            step_if_error(test)

        return retry

    return wrapper


def generate_hash_file(test, file_name):
    dir = '/home/download/'
    cmd = f'openssl dgst -sha256 {dir + file_name}'
    test.ssh_server.send_and_verify('pwd')
    result = test.ssh_server.send_and_receive(f'{cmd}')
    crc = 0
    for i in range(2):
        if 'SHA256' in result:
            crc = result.split('=')[1].strip()
            break
        else:
            i += 1
    if crc:
        test.log.info(f'Hash Value is {crc}')
        test.ssh_server.send_and_verify(f'sudo echo {crc} > {dir}crc_value')
    else:
        test.log.error('Generate hash value fail')

    return crc
