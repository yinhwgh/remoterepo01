# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0092605.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class DtmfDecoderSettingsNonVolatile(BaseTest):
    """
    To test Sind Decoder function
    1.  Reset AT command settings to their factory default values,
    2. Check default value of DTMF decoder settings ,
    3. Change values of  DTMF decoder parameters
    4. Store changed settings in non – volatile memory with use AT&W,
    5. Restart module,
    6. Check current settings of DTMF decoder with use AT^SIND read command,
    7. Restore changed settings DTMF decoder with ATZ,
    8. Check current settings of DTMF decoder with use AT^SIND read command,
    9.  Reset DTMF decoder settings to their factory defaults with use AT&F command,
    10. Check current settings of DTMF decoder with use AT^SIND read command.
    11.  Reset AT command settings to their factory default values

    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_restart(test.dut)
        test.log.info('Restore to default configuration')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.pin1_value = test.dut.sim.pin1

    def run(test):
        # test.log.info('Register into network')
        # test.expect(dstl_enter_pin(test.dut))
        # test.expect(dstl_register_to_network(test.dut))
        test.log.info('check the SIND')
        test.expect(test.dut.at1.send_and_verify('at^sind?', '.*OK.*'))
        test.log.info('set and check sind value')
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",2', '.*OK.*'))
        test.log.info('Store changed settings in non – volatile memory with use AT&W')
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        dstl_restart(test.dut)
        test.sleep(10)

        test.expect(test.dut.at1.send_and_verify('at^sind?', '\^SIND: dtmf,0.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('at+cpin="1111"', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cpin={}'.format(test.pin1_value), ".*OK.*", append=True)
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('atz', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind?', '\^SIND: dtmf,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&f', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind?', '\^SIND: dtmf,0.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at^sind?', '.*OK.*'))



    def cleanup(test):
        dstl_restart(test.dut)
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
