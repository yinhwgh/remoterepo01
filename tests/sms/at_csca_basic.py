# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0091834.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.sms_center_address import dstl_set_sms_center_address, dstl_get_sms_center_address


class Test(BaseTest):
    """TC0091834.001    AtCscaBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CSCA

    1. check command without and with PIN
    1.1 check command without PIN authentication: test, write and read commands should be PIN protected
    1.2 check command with PIN authentication
    - check test command response
    - try to set empty string for SCA
    - set only SCA and check read command
    - set SCA and TOSCA and check read command
    2. check all parameters and also with invalid values: (error should be displayed)
    - check exec command
    - try to set empty write command
    - set invalid TOSCA value
    - invalid SCA value - SCA too long
    - check test command invalid value
    - check read command invalid value

    A functional check is not done here
    """

    OK_RESPONSE = r'.*OK.*'
    CMS_ERROR = r'.*CMS ERROR.*'
    CMS_CME_ERROR = r'.*CMS ERROR:|CME ERROR:.*'
    CMS_ERROR_PIN = r'.*CMS ERROR: SIM PIN required.*'

    def setup(test):
        test.international_sca = test.dut.sim.sca_int
        test.national_sca = test.dut.sim.sca

        test.international_tosca = "145"
        test.national_tosca = "129"

        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.step("1. Check command without and with PIN")

        test.log.step("1.1 Check command without PIN authentication")

        test.log.step("Check test command response")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSCA=?', test.CMS_ERROR_PIN))

        test.log.step("Check read command response")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSCA?', test.CMS_ERROR_PIN))

        test.log.step("Check write command response")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSCA="{test.international_sca}"',
                                                 test.CMS_ERROR_PIN))

        test.log.step("1.2 Check command with PIN authentication")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)

        test.log.info("Set correct sms center address at beginning of the test")
        test.expect(dstl_set_sms_center_address(test.dut))
        test.current_csca = (test.international_sca, test.international_tosca)

        test.log.step("Check test command response")
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=?", test.OK_RESPONSE))
        test.expect(not re.search(".CSCA:.", test.dut.at1.last_response))

        test.log.step("Try to set empty string for SCA")
        test.expect(test.dut.at1.send_and_verify('AT+CSCA=""', test.CMS_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Set only SCA and check read command")
        test.expect(dstl_set_sms_center_address(test.dut, center_addr=test.international_sca))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Set SCA and TOSCA and check read command")
        test.expect(dstl_set_sms_center_address(test.dut, center_addr=test.national_sca,
                                                type_of_service=test.national_tosca))
        test.current_csca = (test.national_sca, test.national_tosca)
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)
        test.expect(dstl_set_sms_center_address(test.dut, center_addr=test.international_sca,
                                                type_of_service=test.international_tosca))
        test.current_csca = (test.international_sca, test.international_tosca)
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("2. Check all parameters and also with invalid values")

        test.log.step("Check exec command")
        test.expect(test.dut.at1.send_and_verify("AT+CSCA", test.CMS_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Try to set empty write command")
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=", test.CMS_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Set invalid TOSCA value")
        invalid_values = ["-1", "256", "300", "aaa", '"aaa"', '"231"', "11as/"]
        for value in invalid_values:
            test.expect(not dstl_set_sms_center_address(test.dut,
                        center_addr=test.national_sca,type_of_service=value))
            test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)
            test.expect(not dstl_set_sms_center_address(test.dut,
                        center_addr=test.international_sca,type_of_service=value))
            test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Invalid SCA value - SCA too long")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSCA="{test.international_sca + str(1) * 10}"',
                                                 test.CMS_CME_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Check test command invalid value")
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=2?", test.CMS_CME_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

        test.log.step("Check read command invalid value")
        test.expect(test.dut.at1.send_and_verify("AT+CSCA1?", test.CMS_CME_ERROR))
        test.expect(dstl_get_sms_center_address(test.dut) == test.current_csca)

    def cleanup(test):
        test.expect(dstl_set_sms_center_address(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))


if "__main__" == __name__:
    unicorn.main()
