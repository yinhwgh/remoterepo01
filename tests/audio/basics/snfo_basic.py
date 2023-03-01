# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0091820.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class AtSnfoBasic(BaseTest):
    """
    To test Snfo basic function

    """

    def setup(test):
        dstl_detect(test.dut)
        test.sleep(10)
        dstl_restart(test.dut)
        test.sleep(10)
        test.log.info('Restore to default configuration')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        # for VIPER does not need below 2 steps
        # test.log.info('set at^scfg="Gpio/mode/DAI"')
        # test.expect(test.dut.at1.send_and_verify('at^scfg="Gpio/mode/DAI","std"', '.*OK.*'))
        # dstl_restart(test.dut)
        # test.sleep(10)
        test.log.info('check the default value of audio output')
        test.expect(test.dut.at1.send_and_verify('at^snfo?', '57,33,0,0.*OK.*'))
        test.log.info('get the audio output value')
        test.expect((test.dut.at1.send_and_verify('at^snfo=?', '.*57.*33.*0.*0-5.*OK.*')))
        test.log.info('set audio output parameters')
        for rxVolStep in range(6):
            test.expect(test.dut.at1.send_and_verify('at^snfo=57,33,0,{}'.format(rxVolStep),'.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
