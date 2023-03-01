# responsible: marcin.kossak@globallogic.com
# location:  Wroclaw
# TC0102549.001

from typing import NamedTuple

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.configure_sms_text_mode_parameters import dstl_read_sms_display_availability, \
    dstl_get_supported_sms_display_availability, dstl_enable_sms_class_0_display, \
    dstl_disable_sms_class_0_display, dstl_set_sms_display_availability
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention of this TC is to check if SSDA command works properly.
    1. Make sure that no PIN1 is entered and module requires SIM PIN1,
    2. execute AT&F and check factory default value off parameter via read command,
    3. check test and write command AT^SSDA without PIN1,
    4. enter PIN1,
    5. check test, write and read command AT^SSDA with PIN1,
    6. check invalid values (error should be displayed)
    - check EXEC command
    - try to set not supported value for write command: -1 and 2
    - try to set empty write command
    - try to set parameter value not as a number
    - try to set write command with more than 1 parameter
    """

    class InvalidParameter(NamedTuple):
        param: str
        message: str

    INVALID_PARAMETERS = [
        InvalidParameter('-1', '- try to set not supported value for write command: -1 '),
        InvalidParameter('2', '-try to set not supported value for write command: 2'),
        InvalidParameter('', '- try to set empty write command'),
        InvalidParameter('abc', '- try to set parameter value not as a number'),
        InvalidParameter('1a', '- try to set parameter value not as a number'),
        InvalidParameter('"ERROR"', '- try to set parameter value not as a number'),
        InvalidParameter('"1"', '- try to set parameter value not as a number'),
        InvalidParameter('"0"', '- try to set parameter value not as a number'),
        InvalidParameter('1,0', '- try to set write command with more than 1 parameter'),
        InvalidParameter('0,1', '- try to set write command with more than 1 parameter'),
        InvalidParameter('0,0', '- try to set write command with more than 1 parameter')]

    INVALID_PARAMETERS_STEP3 = [
        InvalidParameter('-1', '- try to set not supported value for write command: -1 '),
        InvalidParameter('2', '-try to set not supported value for write command: 2'),
        InvalidParameter('abc', '- try to set parameter value not as a number'),
        InvalidParameter('1a', '- try to set parameter value not as a number'),
        InvalidParameter('11', '-try to set not supported value for write command: 11'),
        InvalidParameter('-0', '- try to set not supported value for write command: -0'),
    ]
    def setup(test):
        test.log.info('===== Preparing DUT for test =====')
        dstl_detect(test.dut)
        test.expect(dstl_get_imei(test.dut), critical=True)
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.step("1. Make sure that no PIN1 is entered and module requires SIM PIN1")
        test.expect(dstl_set_sim_waiting_for_pin1(test.dut))

        test.log.step("2. Execute AT&F and check factory default value off parameter via read command")
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        status, sdda_value, _ = dstl_read_sms_display_availability(test.dut,
                                    expected_response=r".*SSDA:\s*1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

        test.log.step("3. Check test and write command AT^SSDA without PIN1")
        status, sdda_values = dstl_get_supported_sms_display_availability(test.dut,
                                expected_response=r".*SSDA:\s*\(0,1\).*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: [0, 1], got {sdda_values}")

        test.expect(dstl_disable_sms_class_0_display(test.dut, ".*OK.*"))
        status, sdda_value, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=".*SSDA: 0.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 0, got {sdda_value}")
        test.expect(dstl_enable_sms_class_0_display(test.dut, ".*OK.*"))

        status, sdda_value, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=".*SSDA: 1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

        test.log.info("===== Check write commands with invalid values without PIN =====")

        for invalid_param in test.INVALID_PARAMETERS_STEP3:
            test.log.info(invalid_param.message)
            status, _ = dstl_set_sms_display_availability(test.dut, parameter=invalid_param.param,
                                                          expected_response=".*CME ERROR.*|"
                                                                            ".*CMS ERROR.*")
            test.expect(status)

        test.log.info("===== Check that the SSDA command setting has not been changed "
                      "after trying to use incorrect values =====")
        status, sdda_values, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=r".*SSDA:\s*1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

        test.log.step("4. enter PIN1")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(2)

        test.log.step("5. check test, write and read command AT^SSDA with PIN1")
        status, sdda_values, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=r".*SSDA:\s*1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

        status, sdda_values = dstl_get_supported_sms_display_availability(
                                test.dut, expected_response=r".*SSDA:\s*\(0,1\).*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: [0, 1], got {sdda_values}")

        test.expect(dstl_disable_sms_class_0_display(test.dut, ".*OK.*"))
        status, sdda_values, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=".*SSDA: 0.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 0, got {sdda_value}")
        test.expect(dstl_enable_sms_class_0_display(test.dut, ".*OK.*"))
        status, sdda_values, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=".*SSDA: 1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

        test.log.step("6. check invalid values (error should be displayed)")
        test.log.step("check EXEC command")
        test.expect(test.dut.at1.send_and_verify("AT^SSDA", ".*ERROR.*"))

        test.log.info("===== Check write commands with invalid values =====")
        for invalid_param in test.INVALID_PARAMETERS:
            test.log.step(invalid_param.message)
            status, _ = dstl_set_sms_display_availability(test.dut, parameter=invalid_param.param,
                                                          expected_response=".*CME ERROR.*|"
                                                                            ".*CMS ERROR.*")
        test.log.info("===== Check that the SSDA command setting has not been changed "
                      "after trying to use incorrect values =====")
        status, sdda_values, _ = dstl_read_sms_display_availability(
                                    test.dut, expected_response=".*SSDA: 1.*OK.*")
        test.expect(status, msg=f"SSDA status in not equal to: 1, got {sdda_value}")

    def cleanup(test):
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))


if "__main__" == __name__:
    unicorn.main()
