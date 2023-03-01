#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0010205.002, TC0103453.002

import unicorn
from core.basetest import BaseTest
from random import choice
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary import restart_module
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses


class Test(BaseTest):
    """
    The module shall be able to either ignore the DTR line of the RS232 interface or switch to command mode during a
    data call or release the data call, depending on the DTR value.
    This version of TC is dedicated for modules which do not support CSD call. Data call is realized in this case
    only via initiation of PPP connection.

    1. Perform 'Set And Config' Block with AT&D0 parameter(ME ignores status of DTR line),
    2. Initiate PPP connection,
    3. Toogle DTR line, should be ignored,
    4. Switch to AT command mode,
    5. Return to data mode,
    6. Toogle DTR line, should be ignored,
    7. Abort PPP connection (check if NO CARRIER appears),
    8. Perform 'Set And Config' Block with AT&D1 parameter,
    9. Initiate PPP connection,
    10. Toogle DTR line, ME should switch to command mode,
    11. Return to data mode,
    12. Abort PPP connection (check if NO CARRIER appears),
    13. Perform 'Set And Config' Block with AT&D2 parameter,
    14. Initiate PPP connection,
    15. Toogle DTR line, (check if NO CARRIER appears),
    16. Perform steps 1-7 but this time in first point of 'set and config' block send AT&D command without any parameter.
    Results should be the same like for steps 1-7,
    17. Perform steps 13-15 but this time in first point of 'set and config' block send AT&F command.
    Results should be the same like for steps 13-15,
    18. Set DTR line to OFF.
    19. Check connection.

    'Set And Config' Block:
    .1. Set specified AT&D parameter.
    .2. Query the current value of AT&D by AT&V,
    .3. Store AT&D to user profile by AT&W,
    .4. Set other value by AT&D command,
    .5. Query the current value of AT&D by AT&V,
    .6. Retsore AT&D value from profile by ATZ,
    .7. Query the current value of AT&D by AT&V,
    .8. Set other value by AT&D command,
    .9. Query the current value of AT&D by AT&V,
    .10. Restart module,
    .11. Query the current value of AT&D by AT&V,
    """

    def setup(test):
        test.ATD_VALUES = [0, 1, 2]
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.at1.connection.setDTR(True)

    def run(test):
        execute_steps_1_7(test, "AT&D0", 1)

        test.log.step("8. Perform 'Set And Config' Block with AT&D1 parameter.")
        set_and_config(test, "AT&D1", test.ATD_VALUES[1], 8)

        test.log.step("9. Initiate PPP connection.")
        test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

        test.log.step("10. Toogle DTR line, ME should switch to command mode.")
        toggle_dtr_line(test, test.ATD_VALUES[1])

        test.log.step("11. Return to data mode.")
        test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))

        test.log.step("12. Abort PPP connection (check if NO CARRIER appears).")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        # In this case, PPP connection can be aborted by restart module.
        test.expect(test.dut.dstl_restart())

        execute_steps_13_15(test, "AT&D2", 13)

        test.log.step("16. Perform steps 1-7 but this time in first point of 'set and config' block send AT&D command without any parameter. "
                      "Results should be the same like for steps 1-7.")
        execute_steps_1_7(test, "AT&D", 16)

        test.log.step("17. Perform steps 13-15 but this time in first point of 'set and config' block send AT&F command. "
                      "Results should be the same like for steps 13-15.")
        execute_steps_13_15(test, "AT&F", 17)

        test.log.step("18. Set DTR line to OFF.")
        test.dut.at1.connection.setDTR(False)

        test.log.step("19. Check connection.")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))

    def cleanup(test):
        test.dut.at1.connection.setDTR(True)
        test.dut.at1.send("AT", wait_after_send=5)
        if "OK" not in test.dut.at1.read():
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.expect(test.dut.at1.send_and_verify('AT&F', ".*OK.*"))


def execute_steps_1_7(test, atd_command, step):
    if step == 1:
        info = 'EXECUTING STEPS 1-7'
    else:
        info = 'REPEATING STEPS 1-7 DURING STEP {}'.format(step)

    test.log.step("1. Perform 'Set And Config' Block with {} parameter (ME ignores status of DTR line).".format(atd_command))
    test.log.info(info)
    set_and_config(test, atd_command, test.ATD_VALUES[0], step)

    test.log.step("2. Initiate PPP connection.")
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step("3. Toggle DTR line, should be ignored.")
    test.log.info(info)
    toggle_dtr_line(test, test.ATD_VALUES[0])

    test.log.step("4. Switch to AT command mode.")
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

    test.log.step("5. Return to data mode.")
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step("6. Toggle DTR line, should be ignored.")
    test.log.info(info)
    toggle_dtr_line(test, test.ATD_VALUES[0])

    test.log.step("7. Abort PPP connection (check if NO CARRIER appears).")
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    # In this case, PPP connection can be aborted by restart module.
    test.expect(test.dut.dstl_restart())


def execute_steps_13_15(test, atd_command, step):
    if step == 13:
        info = 'EXECUTING STEPS 13-15'
    else:
        info = 'REPEATING STEPS 13-15 DURING STEP {}'.format(step)

    test.log.step("13. Perform 'Set And Config' Block with {} parameter.".format(atd_command))
    test.log.info(info)
    set_and_config(test, atd_command, test.ATD_VALUES[2], step)

    test.log.step("14. Initiate PPP connection.")
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step("15. Toggle DTR line, (check if NO CARRIER appears).")
    test.log.info(info)
    toggle_dtr_line(test, test.ATD_VALUES[2])


def set_and_config(test, atd_command, atd_mode, step):
    test.expect(test.dut.dstl_enter_pin())

    test.log.step('{}.1. Set specified AT&D parameter.'.format(step))
    test.expect(test.dut.at1.send_and_verify(atd_command, '.*OK.*'))

    test.log.step('{}.2. Query the current value of AT&D by AT&V.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&D{}'.format(atd_mode), wait_for='OK'))

    test.log.step('{}.3. Store AT&D to user profile by AT&W.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&W', ".*OK.*"))

    test.log.step('{}.4. Set other value by AT&D command.'.format(step))
    other_parameter = get_random_parameter(test, atd_mode)
    test.expect(test.dut.at1.send_and_verify('AT&D{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.5. Query the current value of AT&D by AT&V.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&D{}'.format(other_parameter), wait_for='OK'))

    test.log.step('{}.6. Restore AT&D value from profile by ATZ.'.format(step))
    test.expect(test.dut.at1.send_and_verify('ATZ', ".*OK.*"))

    test.log.step('{}.7. Query the current value of AT&D by AT&V.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&D{}'.format(atd_mode), wait_for='OK'))

    test.log.step('{}.8. Set other value by AT&D command.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&D{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.9. Query the current value of AT&D by AT&V.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&D{}'.format(other_parameter), wait_for='OK'))

    test.log.step('{}.10. Restart module.'.format(step))
    test.expect(test.dut.dstl_restart())
    test.expect(test.dut.dstl_enter_pin())

    test.log.step('{}.11. Query the current value of AT&D by AT&V.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&D{}'.format(atd_mode), wait_for='OK'))


def toggle_dtr_line(test, atd_value):
    test.dut.at1.connection.setDTR(False)
    test.sleep(1)
    test.dut.at1.connection.setDTR(True)
    test.sleep(1)

    if atd_value == test.ATD_VALUES[0]:
        test.dut.at1.send("AT", wait_after_send=5)
        test.expect("OK" not in test.dut.at1.read())
    elif atd_value == test.ATD_VALUES[1]:
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
    elif atd_value == test.ATD_VALUES[2]:
        test.sleep(5)
        test.expect("NO CARRIER" in test.dut.at1.read())


def get_random_parameter(test, parameter_to_exclude):
    random_range = test.ATD_VALUES.copy()
    random_range.remove(parameter_to_exclude)
    return choice(random_range)


if "__main__" == __name__:
    unicorn.main()
