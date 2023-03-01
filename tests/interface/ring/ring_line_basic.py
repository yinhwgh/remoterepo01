# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0095548.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.devboard import devboard


class Test(BaseTest):
    """
    Check basic functionality of RING0 line.

    1. Set AT^SCFG="URC/Ringline","ASC0"
    2. Set AT^SCFG="URC/Ringline/ActiveTime","2"
    3. Run command to generate regular URCs, e.g. AT^SRADC=1,5000
    4. Using McTest check if RING0 line is activated when new URC appears
    5. Stop generating URC
    6. Set AT^SCFG="URC/Ringline","local"
    7. Repeat steps 3-5
    8. Set AT^SCFG="URC/Ringline","OFF"
    9. Run command to generate regular URCs, e.g. AT^SRADC=1,5000
    10. Using McTest check if RING0 line is NOT activated when new URC appears
    11. Stop generating URC
    12. Restore default values for both commands:
        AT^SCFG="URC/Ringline/ActiveTime","2",
        AT^SCFG="URC/Ringline","local"
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.devboard.send_and_verify('MC:URC=RING', '.*OK.*'))

    def run(test):
        test.log.step('1. Set AT^SCFG="URC/Ringline","ASC0"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","asc0"', expect='"URC/Ringline","asc0"', wait_for='OK'))

        test.log.step('2. Set AT^SCFG="URC/Ringline/ActiveTime","2"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"', expect='"URC/Ringline/ActiveTime","2"', wait_for='OK'))

        execute_steps_3_5(test, 'Executing step with "URC/Ringline","asc0" mode')

        test.log.step('6. Set AT^SCFG="URC/Ringline","local"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"', expect='"URC/Ringline","local"', wait_for='OK'))

        test.log.step('7. Repeat steps 3-5')
        execute_steps_3_5(test, 'Repeating step with "URC/Ringline","local" mode')

        test.log.step('8. Set AT^SCFG="URC/Ringline","OFF"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"', expect='"URC/Ringline","off"', wait_for='OK'))

        test.log.step('9. Run command to generate regular URCs, e.g. AT^SRADC=1,5000')
        test.expect(test.dut.at1.send_and_verify('AT^SRADC=0,1,5000', '.*OK.*'))

        test.log.step('10. Using McTest check if RING0 line is NOT activated when new URC appears')
        check_ringline(test, 'off')

        test.log.step('11. Stop generating URC')
        test.expect(test.dut.at1.send_and_verify('AT^SRADC=0,0', '.*OK.*'))
        check_ringline(test, 'off')

    def cleanup(test):
        test.log.step('12. Restore default values for both commands: '
                      'AT^SCFG="URC/Ringline/ActiveTime","2", AT^SCFG="URC/Ringline","local"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"',
                                                 expect='"URC/Ringline","local"', wait_for='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"',
                                                 expect='"URC/Ringline/ActiveTime","2"', wait_for='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SRADC=0,0', '.*OK.*'))
        test.dut.dstl_turn_on_dev_board_urcs()


def check_ringline(test, urc_mode):
    test.sleep(8)
    devboard_buffer = test.dut.devboard.read()

    if urc_mode == 'on':
        test.expect('RINGline' in devboard_buffer)
    else:
        test.expect('RINGline' not in devboard_buffer)


def execute_steps_3_5(test, info):
    test.log.info(info)
    test.log.step('3. Run command to generate regular URCs, e.g. AT^SRADC=1,5000')
    test.expect(test.dut.at1.send_and_verify('AT^SRADC=0,1,5000', '.*OK.*'))

    test.log.info(info)
    test.log.step('4. Using McTest check if RING0 line is activated when new URC appears')
    check_ringline(test, 'on')

    test.log.info(info)
    test.log.step('5. Stop generating URC')
    test.expect(test.dut.at1.send_and_verify('AT^SRADC=0,0', '.*OK.*'))
    check_ringline(test, 'off')


if "__main__" == __name__:
    unicorn.main()
