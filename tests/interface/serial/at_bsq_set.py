#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0010247.001, TC0103493.001

import unicorn
from core.basetest import BaseTest
from random import choice
from dstl.serial_interface import serial_interface_flow_control
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.network_service import register_to_network


class AtBsQSet(BaseTest):
    """
    To check is supported AT\Q values can be set, also saved and load as user profile.

    Repeat steps 1-13 for all available AT\Q parameters.
    1. Load manufacturer defaults at ASC0.
    2. Query the current profile at ASC0.
    3. Set  the \Q to first supported value at ASC0.
    4. Query the current profile at ASC0.
    5. Save the current profile.
    6. Set the \Q to different supported value ASC0.
    7. Query the current profile at ASC0.
    8. Load saved profile.
    9. Query the current profile at ASC0.
    10. Set the \Q to different supported  value ASC0.
    11. Query the current profile at ASC0.
    12. Restart the module.
    13. Query the current profile at ASC0.
    14. Try to set few invalid \Q values.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK", wait_for="(OK|ERROR)"))

    def run(test):
        SUPPORTED_ATQ_VALUES = test.dut.dstl_get_supported_flow_control_numbers()
        UNSUPPORTED_ATQ_VALUES = [x for x in (0, 1, 2, 3) if x not in SUPPORTED_ATQ_VALUES]
        unsupported_atq_value = None
        if len(UNSUPPORTED_ATQ_VALUES) > 0:
            unsupported_atq_value = UNSUPPORTED_ATQ_VALUES[0]
        last_atq_set_in_profile = None

        test.log.step("Repeat steps 1-13 for all available AT\\Q parameters.")
        for atq_value in SUPPORTED_ATQ_VALUES:
            test.log.step("Step for AT\\Q{}. 1. Load manufacturer defaults at ASC0.".format(atq_value))
            test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

            test.log.step("Step for AT\\Q{}. 2. Query the current profile at ASC0.".format(atq_value))
            test.expect(test.dut.dstl_get_flow_control_number() == 3)

            test.log.step("Step for AT\\Q{}. 3. Set the \\Q to first supported value at ASC0.".format(atq_value))
            # This step is executed in step 4 by method: dstl_check_flow_control_number_after_set. This method
            # sets AT\Q value and checks, if has been set correctly.

            test.log.step("Step for AT\\Q{}. 4. Query the current profile at ASC0.".format(atq_value))
            # For Serval products, AT\Q set to 2, returns 3. Expected value must be saved in another variable.
            is_correct, number_in_profile = test.dut.dstl_check_flow_control_number_after_set(atq_value)
            test.expect(is_correct)

            test.log.step("Step for AT\\Q{}. 5. Save to current profile.".format(atq_value))
            test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

            another_atq_value = get_random_parameter(SUPPORTED_ATQ_VALUES, atq_value)
            if another_atq_value:
                test.log.step("Step for AT\\Q{}. 6. Set the \\Q to different supported value ASC0.".format(atq_value))
                # This step is executed in step 7 by method: dstl_check_flow_control_number_after_set. This method
                # sets AT\Q value and checks, if has been set correctly.

                test.log.step("Step for AT\\Q{}. 7. Query the current profile at ASC0.".format(atq_value))
                test.expect(test.dut.dstl_check_flow_control_number_after_set(another_atq_value))
                test.sleep(5)
                test.log.step("Step for AT\\Q{}. 8. Load saved profile.".format(atq_value))
                test.expect(test.dut.at1.send_and_verify("ATZ", "OK"))

                test.log.step("Step for AT\\Q{}. 9. Query the current profile at ASC0.".format(atq_value))
                test.expect(test.dut.dstl_get_flow_control_number() == number_in_profile)

                test.log.step("Step for AT\\Q{}. 10. Set the \\Q to different supported value ASC0.".format(atq_value))
                # This step is executed in step 11 by method: dstl_check_flow_control_number_after_set. This method
                # sets AT\Q value and checks, if has been set correctly.

                test.log.step("Step for AT\\Q{}. 11. Query the current profile at ASC0".format(atq_value))
                test.expect(test.dut.dstl_check_flow_control_number_after_set(another_atq_value))

                test.log.step("Step for AT\\Q{}. 12. Restart the module.".format(atq_value))
                test.expect(test.dut.dstl_restart())
                test.expect(test.dut.dstl_enter_pin())

                test.log.step("Step for AT\\Q{}. 13. Query the current profile at ASC0.".format(atq_value))
                test.expect(test.dut.dstl_get_flow_control_number() == number_in_profile)

            last_atq_set_in_profile = atq_value

        test.log.step("15. Try to set few invalid \\Q values")
        test.log.info("ERROR response with CMEE=0")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=0", "OK"))
        error_in_cme0 = "\\s+ERROR\\s+"
        try_to_set_invalid_parameters(test, error_in_cme0, unsupported_atq_value)

        error_in_cme2 = "\\s+[+]CME ERROR.*"
        test.log.info("ERROR response with CMEE=2")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        try_to_set_invalid_parameters(test, error_in_cme2, unsupported_atq_value)

        test.expect(test.dut.dstl_get_flow_control_number() == last_atq_set_in_profile)

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))


def get_random_parameter(parameters_range, parameter_to_exclude):
    random_range = list(parameters_range).copy()
    random_range.remove(parameter_to_exclude)
    return choice(random_range)


def try_to_set_invalid_parameters(test, error_response, unsupported_atq_value):
    for invalid_atq_value in ["AT\\Q*", "AT\\Q123", "AT\\Q1b", "AT\\Qb", "AT\\Q\"A\""]:
        test.expect(test.dut.at1.send_and_verify(invalid_atq_value, error_response))
    if unsupported_atq_value:
        test.expect(test.dut.at1.send_and_verify(f"AT\\Q{unsupported_atq_value}", error_response))


if "__main__" == __name__:
    unicorn.main()
