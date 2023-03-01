#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0092702.001

import unicorn
from core.basetest import BaseTest
from random import choice
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.configuration import functionality_modes
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary import restart_module
from dstl.configuration import sled_mode_symbols

class Test(BaseTest):
    """
    Verification of AT^SLED command syntax and parameter configurations.

    Check if:
    1. Test, read and write command syntax are correct for all supported parameters
    2. Values are presented by at&v (if (&v) is marked)
    3. Command is not protected by PIN - enter PIN and repeat steps 1 and 2.
    4. Command works in airplane mode
    5. Parameters marked as (P) after changes are reset to this value after restart
    6. Parameters marked as (D) after changes are not reset after restart
    7. Parameters marked as [x] are set if parameter was omitted
    8. Parameters marked as (&W) are stored in user profile by at&w
    9. Parameters marked as (&F) are reset to factory values after at&f
    10. Parameters stored previously in user profile are restored by atz, and after restart module
    """

    SLED_VALUES = [0, 1, 2]

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        execute_steps_1_2(test, "Executing step without PIN")

        test.log.step("3. Command is not protected by PIN - enter PIN and repeat steps 1 and 2.")
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        execute_steps_1_2(test, "Executing step with PIN")

        test.log.step("4. Command works in airplane mode.")
        test.expect(test.dut.dstl_set_airplane_mode())
        for parameter in test.SLED_VALUES:
            test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(parameter), ".*OK.*"))
        test.expect(test.dut.dstl_set_full_functionality_mode())

        test.log.step("5. Parameters marked as (P) after changes are reset to this value after restart.")
        if test.dut.dstl_sled_mode_support_p_symbol():
            test.log.error("Step not implemanted for product {}".format(test.dut.project))
        else:
            test.log.info(
                "Product {} doesn't have parameters marked as [P]".format(test.dut.project))

        test.log.step("6. Parameters marked as (D) after changes are not reset after restart.")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", expect="\\^SLED: 1", wait_for="OK"))

        test.log.step("7. Parameters marked as [x] are set if parameter was omitted.")
        if test.dut.dstl_sled_mode_support_p_symbol():
            test.log.error("Step not implemanted for product {}".format(test.dut.project))
        else:
            test.log.info(
                "Product {} doesn't have parameters marked as [x]".format(test.dut.project))

        test.log.step("8. Parameters marked as (&W) are stored in user profile by at&w.")
        for parameter in test.SLED_VALUES:
            other_parameter = get_random_parameter(test, parameter)
            test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(parameter), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(other_parameter), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SLED?", expect="\\^SLED: {}".format(parameter), wait_for="OK"))

        test.log.step("9. Parameters marked as (&F) are reset to factory values after at&f.")
        test.expect(test.dut.at1.send_and_verify("AT^SLED=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", expect="\\^SLED: 0", wait_for="OK"))

        test.log.step("10. Parameters stored previously in user profile are restored by atz, and after restart module.")
        for parameter in test.SLED_VALUES:
            other_parameter = get_random_parameter(test, parameter)
            test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(parameter), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(other_parameter), ".*OK.*"))
            test.expect(test.dut.dstl_restart())
            test.expect(test.dut.dstl_enter_pin(test.dut.sim))
            test.expect(test.dut.at1.send_and_verify("AT^SLED?", expect="\\^SLED: {}".format(parameter), wait_for="OK"))

    def cleanup(test):
        test.dut.at1.send_and_verify("AT+CFUN=1", ".*OK.*")
        test.dut.at1.send_and_verify("AT^SLED=0", ".*OK.*")
        test.dut.dstl_restart()


def execute_steps_1_2(test, info):
    test.log.info(info)
    test.log.step("1. Test, read and write command syntax are correct for all supported parameters.")
    test.expect(test.dut.at1.send_and_verify("AT^SLED=?", "\\^SLED: \\(0-2\\)", wait_for="OK"))
    for parameter in test.SLED_VALUES:
        test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(parameter), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SLED?", expect="\\^SLED: {}".format(parameter), wait_for="OK"))

    test.log.info(info)
    test.log.step("2. Values are presented by at&v (if (&v) is marked).")
    for parameter in test.SLED_VALUES:
        test.expect(test.dut.at1.send_and_verify("AT^SLED={}".format(parameter), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&V", expect="\\^SLED: {}".format(parameter), wait_for="OK"))


def get_random_parameter(test, parameter_to_exclude):
    random_range = test.SLED_VALUES.copy()
    random_range.remove(parameter_to_exclude)
    return choice(random_range)


if "__main__" == __name__:
    unicorn.main()
