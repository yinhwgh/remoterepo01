#responsible marek.kocela@globallogic.com
#Wroclaw
#TC TC0103902.002
import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """Short description:
       Check basic commands of SNI extension.

       Detailed description:
       1. Set SNI Extension to be "off"
       2. Check the value of parameter "secsni"
       3. Set SNI Extension to be "on"
       4. Check the value of parameter "secsni"
       5. Try to set empty "sniname" parameter
       6. Set value of "sniname" using 161 characters
       7. Check the value of parameters "secsni" and "sniname"
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

        test.tcp_client = SocketProfile(test.dut, 0, 1)
        test.tcp_client.dstl_get_service().dstl_load_profile()

    def run(test):
        test.log.info("Executing script for test case: TC0103902.002 - SNIExtensionBasic")

        test.log.step("1) Set SNI Extension to be \"off\"")
        test.expect(test.dut.at1.send_and_verify("at^siss=0,secsni,\"0\"", expect="OK", wait_for="OK", timeout=10))

        test.log.step("2) Check the value of parameter \"secsni\"")
        test.expect(test.dut.at1.send_and_verify("at^siss?", expect="0,\"secsni\",\"0\"", wait_for="OK", timeout=10))

        test.log.step("3) Set SNI Extension to be \"on\"")
        test.expect(test.dut.at1.send_and_verify("at^siss=0,secsni,\"1\"", expect="OK", wait_for="OK", timeout=10))

        test.log.step("4) Check the value of parameter \"secsni\"")
        test.expect(test.dut.at1.send_and_verify("at^siss?", expect="0,\"secsni\",\"1\"", wait_for="OK", timeout=10))

        test.log.step("5) Try to set empty \"sniname\" parameter")
        test.expect(test.dut.at1.send_and_verify("at^siss=0,sniname,\"\"",
                                                 expect="ERROR", wait_for="ERROR", timeout=10))

        test.log.step("6) Set value of \"sniname\" using 161 characters")
        test_string = dstl_generate_data(161)
        test.expect(test.dut.at1.send_and_verify("at^siss=0,sniname,\"{}\"".format(test_string),
                                     expect="OK", wait_for="OK", timeout=10))

        test.log.step("7) Check the value of parameters \"secsni\" and \"sniname")
        test.expect(test.dut.at1.send_and_verify("at^siss?", expect="0,\"secsni\",\"1\"", wait_for="OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("at^siss?", expect="0,\"sniname\",\"{}\"".format(test_string),
                                                 wait_for=test_string, timeout=10))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()