#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0105649.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.http_profile import HttpProfile


class Test(BaseTest):
    """
    TC intention: Basic check of SNI extension
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.srv_id = 0
        test.con_id = 1

        test.log.step("1. Create HTTPS service profile with \"secsni\" parameter set to \"1\"")
        http_server = "http://www.httpbin.org"
        test.http_profile = HttpProfile(test.dut, test.srv_id, test.con_id, address=http_server, http_command="get")
        test.expect(test.http_profile.dstl_get_service().dstl_load_profile())
        test.expect(test.dut.at1.send_and_verify("AT^SISS={},\"secsni\",\"1\"".format(test.srv_id)))

        test.log.step("2. Check the value of parameter \"secsni\"")
        test.expect(test.dut.at1.send_and_verify("AT^SISS?", expect=".*{},\"secsni\",\"1\".*".format(test.srv_id)))

        test.log.step("3. Set SNI Extension to \"0\"")
        test.expect(test.dut.at1.send_and_verify("AT^SISS={},\"secsni\",\"0\"".format(test.srv_id)))

        test.log.step("4. Check the value of parameter \"secsni\"")
        test.expect(test.dut.at1.send_and_verify("AT^SISS?", expect=".*{},\"secsni\",\"0\".*".format(test.srv_id)))

        test.log.step("5. Set 255 character long name using \"sniname\" parameter")
        sniname_text = dstl_generate_data(255)
        test.expect(test.dut.at1.send_and_verify("AT^SISS={},\"sniname\",\"{}\"".format(test.srv_id, sniname_text)))

        test.log.step("6. Check the value of parameter \"sniname\"")
        test.expect(test.dut.at1.send_and_verify("AT^SISS?", expect=".*{},\"sniname\",\"{}\".*".format(test.srv_id,
                                                                                                       sniname_text)))

    def cleanup(test):
        test.expect(test.http_profile.dstl_get_service().dstl_reset_service_profile())


if __name__ == "__main__":
    unicorn.main()