#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0092138.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.step("A. To test the user defined profile function of at+cscs.")
        test.log.step("1. Check the default setting of cscs. \nAT+CSCS?")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"GSM\""))

        test.log.step("2. Set the parameter to UCS2 and check if the setting takes effect. \nAT+CSCS=\"UCS2\"")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"UCS2\""))

        test.log.step("3. Execute at&w and check the function of at&w \nAT+CSCS=\"GSM\" \nAT+CSCS? \nATZ \nAT+CSCS?")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"GSM\""))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"UCS2\""))

        test.log.step("4.Execute at&f and check the function of at&f \nAT+CSCS?")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"GSM\""))

        test.log.step("5. Set to default value \nAT&W \nAT+CSCS?")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", "+CSCS: \"GSM\""))

        test.log.step("B. To test the user defined profile function of at^sled")
        test.log.step("1. Check the default setting of sled. \nAT^SLED?")
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 0"))

        test.log.step("2. Set the parameter to at^sled=2, 30 and check if the setting takes effect. \n"
                      "(For products which supports only one parameter, set AT^SLED=2)")
        test.expect(test.dut.at1.send_and_verify("AT^SLED=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 2"))

        test.log.step("3. Execute at&w and check the function of at&w \nAT^SLED=0 \nAT^SLED? \nATZ \nAT^SLED?")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 0"))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 2"))

        test.log.step("4.Execute at&f and check the function of at&f \nAT^SLED?")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 0"))

        test.log.step("5. Set to default value \nAT&W \nAT+SLED?")
        test.expect(test.dut.at1.send_and_verify("AT^SLED=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", "^SLED: 0"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
   unicorn.main()