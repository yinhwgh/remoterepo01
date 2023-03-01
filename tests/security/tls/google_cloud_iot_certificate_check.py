#responsible: bartlomiej.mazurek2@globallogic.com
#location: Wroclaw
#TC0105435.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state\
    import dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates\
    import InternetServicesCertificates
from dstl.network_service.attach_to_network import dstl_enter_pin


class Test(BaseTest):
    """TC0105435.001

    Check if certificates for Google cloud IoT service are preloaded on the module.

    1. Check if certificates are installed on module.
    2. Check syntax of response.

    Server Certificate should include "Google" in ^SBNR response (according to LM)
    """

    def setup(test):
        test.google_certs = [
            "/OU=GlobalSign Root CA - R2/O=GlobalSign/CN=GlobalSign",
            "/OU=GlobalSign ECC Root CA - R4/O=GlobalSign/CN=GlobalSign",
            "/C=US/O=Google Trust Services LLC/CN=GTS Root R1",
            "/C=US/O=Google Trust Services LLC/CN=GTS Root R2",
            "/C=US/O=Google Trust Services LLC/CN=GTS Root R3",
            "/C=US/O=Google Trust Services LLC/CN=GTS Root R4"
        ]

        test.valid_cert = r'.*\^SBNR: \d+, size: "\d+", issuer: ".+", serial number: "\S+", ' \
                          r'subject: ".+", signature: "\S+", thumbprint algorithm: "sha1", ' \
                          r'thumbprint: "\S{40}", expiry date: "\d{4},\d{1,2},\d{0,2}"*.*'

        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_error_message_format(test.dut, "2"))
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)

    def run(test):
        test.log.step("1. Check if certificates are installed on module")
        test.preloaded_cert = InternetServicesCertificates(test.dut, mode="preconfig_cert")
        test.expect(test.preloaded_cert.dstl_count_uploaded_certificates() > 6)

        for cert in test.google_certs:
            test.log.info(f"Checking for certificate {cert}")
            test.expect(cert in test.dut.at1.last_response)

        test.log.step("2. Check syntax of response")
        test.expect(re.search(test.valid_cert, test.dut.at1.last_response))

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))


if "__main__" == __name__:
    unicorn.main()