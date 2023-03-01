#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0010206.002
#TC0103454.002

import unicorn
from core.basetest import BaseTest
from random import choice
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode


class Test(BaseTest):
    """
    The module shall be able to set the CDC line of the RS232 interface to either
    always on or on while it detects a data carrier.
    This version of TC is dedicated for modules which do not support CSD call.
    Data call is realized in this case only via initiation of PPP connection.

    1. Perform 'Set And Config' Block with AT&C0 parameter - DCD line is always ON.
    2. Initiate PPP connection.
    3. Check the DCD line state.
    4. Switch to AT command mode and check DCD line state.
    5. Return to data mode and check DCD line state.
    6. Abort PPP connection.
    7. Check the DCD line state.
    8. Perform 'Set And Config' Block with AT&C1 parameter - DCD line is intended to
    distinguish between AT Command and Data mode.
    9. Initiate PPP connection.
    10. Check the DCD line state.
    11. Switch to AT command mode and check DCD line state.
    12. Return to data mode and check DCD line state.
    13. Abort PPP connection.
    14. Check the DCD line state.
    15. Perform 'Set And Config' Block with AT&C2 parameter - DCD line shall be on when Internet
    service profiles are in state "Connecting" or "Up".
    16. Establish HTTP connection.
    17. Check the DCD line state.
    18. Abort HTTP connection.
    19. Check the DCD line state.
    20. Perform steps 1-7 but this time in first point of 'set and config' block send AT&C command
    without any parameter. Results should be the same like for steps 1-7.
    21. Perform steps 8-14 but this time in first point of 'set and config' block send AT&F command.
    Results should be the same like for steps 8-14.

    'Set And Config' Block:
    .1. Set specified AT&C parameter.
    .2. Query the current value of AT&C by AT&V and check state of DCD line.
    .3. Store AT&C to user profile by AT&W.
    .4. Set other value by AT&C command.
    .5. Query the current value of AT&C by AT&V and check state of DCD line.
    .6. Restore AT&C value from profile by ATZ.
    .7. Query the current value of AT&C by AT&V and check state of DCD line.
    .8. Set other value by AT&C command.
    .9. Query the current value of AT&C by AT&V and check state of DCD line.
    .10. Restart module.
    .11. Query the current value of AT&C by AT&V and check state of DCD line.
    """

    ATC_VALUES = [0, 1, 2]

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.at1.send_and_verify("AT&D2", '.*OK.*'))
        test.expect(test.dut.dstl_register_to_network())

    def run(test):
        execute_steps_1_7(test, 'AT&C0', 1)

        execute_steps_8_14(test, 'AT&C1', 8)

        test.log.step('15. Perform "Set And Config" Block with AT&C2 parameter - DCD line shall be on when '
                      'Internet service profiles are in state "Connecting" or "Up".')
        set_and_config(test, 'AT&C2', test.ATC_VALUES[2], 15)

        test.log.step('16. Establish HTTP connection.')
        test.http_server = HttpServer("IPv4")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        connection_setup.dstl_load_and_activate_internet_connection_profile()
        http_client = HttpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(), http_command="get",
                                  host=test.http_server.dstl_get_server_ip_address(), port=test.http_server.dstl_get_server_port())
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step('17. Check the DCD line state.')
        test.expect(test.dut.at1.connection.getCD())

        test.log.step('18. Abort HTTP connection.')
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())
        test.expect(connection_setup.dstl_deactivate_internet_connection())

        test.log.step('19. Check the DCD line state.')
        test.expect(not test.dut.at1.connection.getCD())

        test.log.step('20. Perform steps 1-7 but this time in first point of "set and config" block send AT&C command '
                      'without any parameter. Results should be the same like for steps 1-7.')
        execute_steps_1_7(test, 'AT&C', 20)

        test.log.step('21. Perform steps 8-14 but this time in first point of "set and config" block '
                      'send AT&F command. Results should be the same like for steps 8-14.')
        execute_steps_8_14(test, 'AT&F', 21)

    def cleanup(test):
        try:
            if not test.http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.dut.dstl_switch_to_command_mode_by_dtr()
        test.expect(test.dut.at1.send_and_verify('AT&F', ".*OK.*"))
        test.expect(test.dut.dstl_restart())


def set_and_config(test, atc_command, atc_mode, step):
    test.log.step('{}.1. Set specified AT&C parameter.'.format(step))
    test.expect(test.dut.at1.send_and_verify(atc_command, '.*OK.*'))

    test.log.step('{}.2. Query the current value of AT&C by AT&V and check state of DCD line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&C{}'.format(atc_mode), wait_for='OK'))
    check_dcd(test, atc_mode)

    test.log.step('{}.3. Store AT&C to user profile by AT&W.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&W', ".*OK.*"))

    test.log.step('{}.4. Set other value by AT&C command.'.format(step))
    other_parameter = get_random_parameter(test, atc_mode)
    test.expect(test.dut.at1.send_and_verify('AT&C{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.5. Query the current value of AT&C by AT&V and check state of DCD line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&C{}'.format(other_parameter), wait_for='OK'))
    check_dcd(test, other_parameter)

    test.log.step('{}.6. Retsore AT&C value from profile by ATZ.'.format(step))
    test.expect(test.dut.at1.send_and_verify('ATZ', ".*OK.*"))

    test.log.step('{}.7. Query the current value of AT&C by AT&V and check state of DCD line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&C{}'.format(atc_mode), wait_for='OK'))
    check_dcd(test, atc_mode)

    test.log.step('{}.8. Set other value by AT&C command.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&C{}'.format(other_parameter), '.*OK.*'))

    test.log.step('{}.9. Query the current value of AT&C by AT&V and check state of DCD line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&C{}'.format(other_parameter), wait_for='OK'))
    check_dcd(test, other_parameter)

    test.log.step('{}.10. Restart module.'.format(step))
    test.expect(test.dut.dstl_restart())
    test.dut.dstl_register_to_network()

    test.log.step('{}.11. Query the current value of AT&C by AT&V and check state of DCD line.'.format(step))
    test.expect(test.dut.at1.send_and_verify('AT&V', expect='&C{}'.format(atc_mode), wait_for='OK'))
    check_dcd(test, atc_mode)


def execute_steps_1_7(test, atc_command, step):
    if step == 1:
        info = 'EXECUTING STEPS 1-7'
    else:
        info = 'REPEATING STEPS 1-7 DURING STEP {}'.format(step)

    test.log.step('1. Perform "Set And Config" Block with {} parameter - DCD line is always ON'.format(atc_command))
    test.log.info(info)
    set_and_config(test, atc_command, test.ATC_VALUES[0], 1)

    test.log.step('2. Initiate PPP connection.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step('3. Check the DCD line state.')
    test.log.info(info)
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('4. Switch to AT command mode and check DCD line state.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('5. Return to data mode and check DCD line state.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('6. Abort PPP connection.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

    test.log.step('7. Check the DCD line state.')
    test.log.info(info)
    test.expect(test.dut.at1.connection.getCD())


def execute_steps_8_14(test, atc_command, step):
    if step == 8:
        info = 'EXECUTING STEPS 8-14'
    else:
        info = 'REPEATING STEPS 8-14 DURING STEP {}'.format(step)

    test.log.step('8. Perform "Set And Config" Block with '
                  '{} parameter - DCD line is intended to distinguish between AT Command and Data mode.'.format(atc_command))
    test.log.info(info)
    set_and_config(test, atc_command, test.ATC_VALUES[1], 8)

    test.log.step('9. Initiate PPP connection.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    test.log.step('10. Check the DCD line state.')
    test.log.info(info)
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('11. Switch to AT command mode and check DCD line state.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('12. Return to data mode and check DCD line state.')
    test.log.info(info)
    test.expect(test.dut.at1.send_and_verify('ATO', '.*CONNECT.*', wait_for="CONNECT"))
    test.expect(test.dut.at1.connection.getCD())

    test.log.step('13. Abort PPP connection.')
    test.log.info(info)
    test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())

    test.log.step('14. Check the DCD line state.')
    test.log.info(info)
    test.expect(not test.dut.at1.connection.getCD())


def check_dcd(test, atc_parameter):
    if atc_parameter == 0:
        test.expect(test.dut.at1.connection.getCD())
    else:
        test.expect(not test.dut.at1.connection.getCD())


def get_random_parameter(test, parameter_to_exclude):
    random_range = test.ATC_VALUES.copy()
    random_range.remove(parameter_to_exclude)
    return choice(random_range)


if "__main__" == __name__:
    unicorn.main()
