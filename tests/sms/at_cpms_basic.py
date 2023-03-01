#responsible: aleksander.denis@globallogic.com
#location: Wroclaw
#TC0091833.001
import re

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.sms.sms_configurations import dstl_check_supported_settings_of_sms_memory, \
    dstl_set_preferred_sms_memory, dstl_get_current_sms_memory


class Test(BaseTest):
    """
    TC0091833.001    AtCpmsBasic

    This procedure provides basic tests for the test and write command of +CPMS.

    1.check command without and with PIN
    2.check all parameters and also with invalid values
    3.check functionality by switch all 3 memories from SM to MT/ME (in case of 3GPP2 only ME
    memory will be available)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        dstl_set_error_message_format(test.dut)

    def run(test):
        test.log.h2("Executing script for test case TC0091833.001 AtCpmsBasic")
        test.log.step("Step 1.check command without and with PIN")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))

        test.log.info("=== Checking the command without PIN entered ===")
        test.expect(not dstl_check_supported_settings_of_sms_memory(test.dut))
        test.expect(re.search(r".*\+CMS ERROR: SIM PIN required.*", test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM"',
                                                 r".*\+CMS ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS?',
                                                 r".*\+CMS ERROR: SIM PIN required.*"))

        test.log.info("=== Checking the command with PIN entered ===")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_check_supported_settings_of_sms_memory(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut))
        test.expect(dstl_get_current_sms_memory(test.dut) == ('ME', 'ME', 'ME'))

        test.log.step("Step 2.check all parameters and also with invalid values")
        test.log.info("=== Checking the command with correct parameters ===")

        test.expect(dstl_set_preferred_sms_memory(test.dut,'MT',memory_index=1))
        test.expect(dstl_get_current_sms_memory(test.dut)[0] == "MT")

        test.expect(dstl_set_preferred_sms_memory(test.dut,'SM,SR'))
        test.expect(dstl_get_current_sms_memory(test.dut)[0:2] == ("SM", "SR"))

        memory = {"ME", "MT", "SM", "SR"}
        for slot1 in memory:
            for slot2 in memory:
                for slot3 in memory:
                    test.expect(dstl_set_preferred_sms_memory(test.dut,
                                                              '{},{},{}'.format(slot1,slot2,slot3)))
                    test.expect(dstl_get_current_sms_memory(test.dut) == (slot1,slot2,slot3))

        test.log.info("=== Checking the command with incorrect parameters ===")
        test.expect(test.dut.at1.send_and_verify('AT+CPMS=1,2,3',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="ME","ME",-1',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="ME","ME","ME",1',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS=,"ME"',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS=,,"ME"',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="ME",0,"ME"',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="PB","ME","ME"',
                                                 r".*\+CMS ERROR: invalid parameter.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CPMS="ME","ME 1","ME"',
                                                 r".*\+CMS ERROR: text string too long.*"))

        test.log.step("Step 3.check functionality by switch all 3 memories from SM to MT/ME "
                      "(in case of 3GPP2 only ME memory will be available)")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_get_current_sms_memory(test.dut) == ("SM", "SM", "SM"))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))
        test.expect(dstl_get_current_sms_memory(test.dut) == ("ME", "ME", "ME"))

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))

if "__main__" == __name__:
    unicorn.main()
