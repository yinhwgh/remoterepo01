# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0091817.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class AtCmutBasic(BaseTest):
    """
    To Test mute function:
    This procedure provides basic tests for the test, read and write command of +CMUT (audio muting).
    For functionality test a voice call will be established.
    The functionality to check if the audio channel is really muted is not verified here
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)

        test.sleep(10)
        dstl_restart(test.dut)
        dstl_restart(test.r1)

        test.sleep(10)
        test.log.info('Restore to default configuration')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        test.log.info('1.Set up call')
        test.log.info('1.1 Register into network')
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.log.info('1.2 dut calls r1')
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata', '.*OK.*'))
        test.log.info('set DUT to mute')
        test.expect(test.dut.at1.send_and_verify('at+cmut=1','.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cmut=0','.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ath','.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
