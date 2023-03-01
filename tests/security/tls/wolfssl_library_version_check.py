# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0096579.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.dstl_general_product_info import dstl_general_product_info
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Short description:
    To check if WolfSSL TLS library version is as expected.
    Detailed description:
    Execute command: AT^SINFO="SSLLibrary/Ver" and check the output
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.h2('Execute command: AT^SINFO="SSLLibrary/Ver" and check the output.')
        expected_wolfssl_version = "4.5.0"
        test.expect(dstl_general_product_info(test.dut, information_type="ssl_lib"))
        test.expect(expected_wolfssl_version in test.dut.at1.last_response)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
