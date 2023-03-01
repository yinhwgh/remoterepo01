# responsible: marcin.drozd@globallogic.com
# location: Wroclaw
# TC0102354.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_check_if_module_is_on_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.identification.get_identification import dstl_get_defined_ati_parameters
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
    Checking option "Power off module after closing ports" of linux multiplexer.
    """

    def setup(test):
        test.expect(dstl_detect(test.dut))
        test.dut.at1.close()
        test.sleep(1)
        test.os.execute('linmuxcfg -p=/dev/dAsc0 -o=0')

    def run(test):
        test.log.step('1. Open mux channels (MUX1, MUX2, MUX3) and '
                      'query identification commands using every mux.')
        open_mux_channels(test)
        send_commands(test)

        test.log.step('2. Close all virtual COM ports. Module should be on after closing all '
                      'mux channels "Power off module after closing ports" option '
                      'shound be unchecked in multiplexer options.')
        close_mux_channels(test)
        test.expect(dstl_check_if_module_is_on_via_dev_board(test.dut))

        test.log.step('3. Enable "Power off module after closing ports" in multiplexer options.')
        test.os.execute('linmuxcfg -p=/dev/dAsc0 -o=1')

        test.log.step('4. Open mux channels (MUX1, MUX2, MUX3) and '
                      'query identification commands using every mux.')
        open_mux_channels(test)
        send_commands(test)

        test.log.step('5. Close all virtual COM ports. Module should turn off after closing all '
                      'mux channels "Power off module after closing ports" option '
                      'should be checked in multiplexer options.')
        close_mux_channels(test)
        test.expect(test.dut.devboard.verify_or_wait_for("PWRIND: 1", timeout=10))

        test.log.step('6. Turn on module.Wait for SYSSTART')
        test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
        test.dut.at1 = test.dut.mux_1
        test.dut.mux_1.open()
        test.expect(test.dut.at1.wait_for('SYSSTART', timeout = 10))

        test.log.step('7. Disable "Power off module after closing ports" in multiplexer options.')
        test.os.execute('linmuxcfg -p=/dev/dAsc0 -o=0')

    def cleanup(test):
        close_mux_channels(test)
        test.os.execute('linmuxcfg -p=/dev/dAsc0 -o=0')


def open_mux_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.dut.mux_3.open()
    test.sleep(3)


def close_mux_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.dut.mux_3.close()
    test.sleep(5)


def send_commands(test):
    test.dut.at1 = test.dut.mux_1
    test.expect(dstl_detect(test.dut))
    test.expect(dstl_get_defined_ati_parameters(test.dut))
    test.dut.at1 = test.dut.mux_2
    test.expect(dstl_detect(test.dut))
    test.expect(dstl_get_defined_ati_parameters(test.dut))


if "__main__" == __name__:
    unicorn.main()
