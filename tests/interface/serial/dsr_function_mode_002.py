# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0010200.002
# TC0103452.002

import unicorn
from core.basetest import BaseTest
from random import choice
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode


class Test(BaseTest):
    """
    The module shall be able to set the DSR line of the RS232 interface to either always on or on while it is in data mode.
    This version of TC is dedicated for modules which do not support CSD call. Data call is realized in this case only
    via initiation of PPP connection.

    1. Perform "Set And Config" Block with AT&S0 parameter - DSR line is always ON.
    2. Initiate PPP connection.
    3. Check the DSR line state.
    4. Switch to AT command mode and check DSR line state.
    5. Return to data mode and check DSR line state.
    6. Abort the PPP connection.
    7. Check the DSR line state.
    8. Perform 'Set And Config' Block with AT&S1 parameter - ME in command mode: DSR is OFF. ME in data mode: DSR is ON.
    9. Initiate PPP connection.
    10. Check the DSR line state.
    11. Switch to AT command mode and check DSR line state.
    12. Return to data mode and check DSR line state.
    13. Abort the PPP connection.
    14. Check the DSR line state.
    15. Perform steps 1-7 but this time in first point of 'set and config' block send AT&S command without any parameter.
    Results should be the same like for steps 1-7.
    16. Perform steps 1-7 but this time in first point of 'set and config' block send AT&F command.
    Results should be the same like for steps 1-7.

    'Set And Config' Block:
    .1. Set specified AT&S parameter.
    .2. Query the current value of AT&S by AT&V and check state of DSR line.
    .3. Store AT&S to user profile by AT&W.
    .4. Set other value by AT&S command.
    .5. Query the current value of AT&S by AT&V and check state of DSR line.
    .6. Retsore AT&S value from profile by ATZ.
    .7. Query the current value of AT&S by AT&V and check state of DSR line.
    .8. Set other value by AT&S command.
    .9. Query the current value of AT&S by AT&V and check state of DSR line.
    .10. Restart module.
    .11. Query the current value of AT&S by AT&V and check state of DSR line.
    """

    ATS_VALUES = [0, 1]

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.at1.send_and_verify('AT&D2', '.*OK.*'))
        test.expect(test.dut.dstl_enter_pin())

    def run(test):
        execute_steps_1_7(test, 'AT&S0', 1)

        test.log.step('8. Perform "Set And Config" Block with AT&S1 parameter - ME in command mode: DSR is OFF. '
                      'ME in data mode: DSR is ON.')
        set_and_config(test, 'AT&S1', test.ATS_VALUES[1], 8)

        test.log.step('9. Initiate PPP connection.')
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

        test.log.step('10. Check the DSR line state.')
        test.expect(test.dut.at1.connection.getDSR())

        test.log.step('11. Switch to AT command mode and check DSR line state.')
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.expect(not test.dut.at1.connection.getDSR())

        test.log.step('12. Return to data mode and check DSR line state.')
        test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))
        test.expect(test.dut.at1.connection.getDSR())

        test.log.step('13. Abort the PPP connection.')
        test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

        test.log.step('14. Check the DSR line state.')
        test.expect(not test.dut.at1.connection.getDSR())

        test.log.step('15. Perform steps 1-7 but this time in first point of "set and config" block send AT&S command '
                      'without any parameter. Results should be the same like for steps 1-7.')
        execute_steps_1_7(test, 'AT&S', 15)

        test.log.step('16. Perform steps 1-7 but this time in first point of "set and config" block send AT&F command. '
                      'Results should be the same like for steps 1-7.')
        execute_steps_1_7(test, 'AT&F', 16)

    def cleanup(test):
        test.dut.dstl_switch_to_command_mode_by_dtr()
        test.expect(test.dut.at1.send_and_verify('AT&F', ".*OK.*"))


def execute_steps_1_7(test, ats_command, step):
    if step == 1:
        info = 'EXECUTING STEPS 1-7'
    else:
        info = 'REPEATING STEPS 1-7 DURING STEP {}'.format(step)

    test.log.step('1. Perform "Set And Config" Block with {} parameter - DSR line is always ON'.format(ats_command))
    test.log.info(info)
    set_and_config(test, ats_command, test.ATS_VALUES[0], 1)

    test.log.step('2. Initiate PPP connection.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step('3. Check the DSR line state.')
    test.log.info(info)
    test.expect(test.dut.at1.connection.getDSR())

    test.log.step('4. Switch to AT command mode and check DSR line state.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    test.expect(test.dut.at1.connection.getDSR())

    test.log.step('5. Return to data mode and check DSR line state.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))
    test.expect(test.dut.at1.connection.getDSR())

    test.log.step('6. Abort the PPP connection.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

    test.log.step('7. Check the DSR line state.')
    test.log.info(info)
    test.expect(test.dut.at1.connection.getDSR())


def set_and_config(test, ats_command, ats_mode, step):
    test.log.step('{}.1. Set specified AT&S parameter.'.format(step))
    test.expect(test.dut.at1.send_and_verify(ats_command, '.*OK.*'))

    test.log.step('{}.2. Query the current value of AT&S by AT&V and check state of DSR line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&S{}'.format(ats_mode), wait_for='OK'))
    check_dsr(test, ats_mode)

    test.log.step('{}.3. Store AT&S to user profile by AT&W.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&W', ".*OK.*"))

    test.log.step('{}.4. Set other value by AT&S command.'.format(step))
    other_parameter = (ats_mode + 1) % 2
    test.expect(test.dut.at1.send_and_verify('AT&S{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.5. Query the current value of AT&S by AT&V and check state of DSR line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&S{}'.format(other_parameter), wait_for='OK'))
    check_dsr(test, other_parameter)

    test.log.step('{}.6. Retsore AT&S value from profile by ATZ.'.format(step))
    test.expect(test.dut.at1.send_and_verify('ATZ', ".*OK.*"))

    test.log.step('{}.7. Query the current value of AT&S by AT&V and check state of DSR line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&S{}'.format(ats_mode), wait_for='OK'))
    check_dsr(test, ats_mode)

    test.log.step('{}.8. Set other value by AT&S command.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&S{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.9. Query the current value of AT&S by AT&V and check state of DSR line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&S{}'.format(other_parameter), wait_for='OK'))
    check_dsr(test, other_parameter)

    test.log.step('{}.10. Restart module.'.format(step))
    test.expect(test.dut.dstl_restart())
    test.expect(test.dut.dstl_enter_pin())

    test.log.step('{}.11. Query the current value of AT&S by AT&V and check state of DSR line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&S{}'.format(ats_mode), wait_for='OK'))
    check_dsr(test, ats_mode)


def check_dsr(test, ats_parameter):
    if ats_parameter == 1:
        test.expect(not test.dut.at1.connection.getDSR())
    else:
        test.expect(test.dut.at1.connection.getDSR())


if "__main__" == __name__:
    unicorn.main()
