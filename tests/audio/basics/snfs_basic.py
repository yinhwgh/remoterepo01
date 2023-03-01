# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0091818.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode



class AtSnfsBasic(BaseTest):
    """
    To test Snfs basic function
    The range of audio mode is from 1 to 6 for VIPER
    For other modules, the audio mode depends on what is described in at spec.
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
        # test.log.info('check at^scfg="Gpio/mode/DAI"')
        # test.expect(test.dut.at1.send_and_verify('at^scfg="Gpio/mode/DAI","std"','.*OK.*'))
        # dstl_restart(test.dut)
        # test.sleep(10)
        test.log.info('check the audio mode')
        test.expect(test.dut.at1.send_and_verify('at^snfs=?','.*OK.*'))
        test.log.info('get the audio mode value')
        result = re.findall('\^SNFS: \(1-(\\d+)\)', test.dut.at1.last_response)
        audMode = int(result[0])
        test.log.info('check if all the audio mode value can be set into module')
        for audmode in range(1,audMode+1):
            test.expect(test.dut.at1.send_and_verify('at^snfs={}'.format(audmode),'.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
