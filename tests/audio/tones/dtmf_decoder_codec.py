# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0092970.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode



class DtmfDecoderCodec(BaseTest):
    """
    1. Select audio hardware set to 6
    2. Enable the DTMF indicator in SIND command,local and network source with different parameter,
    4. Send the DTMF tones from codec board, the dur and break is changed according to the setting in sind dtmf indicator.
    5. Check the URC from module under test
    6. Set up one voice call, and check the DTMF from both side.

    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        test.sleep(10)
        # dstl_restart(test.dut)
        # dstl_restart(test.r1)
        # test.sleep(10)
        test.log.info('Restore to default configuration')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        test.log.info('Register into network')
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.log.info('check the SIND')
        test.expect(test.dut.at1.send_and_verify('at^sind?','.*OK.*'))
        test.log.info('set and check sind value')
        test.expect(test.dut.at1.send_and_verify('at^sind="dtmf",1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^snfs=6','.*OK.*'))
        test.log.info('dut calls r1')
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata', '.*OK.*'))
        test.log.info('send dtmf from r1,check the URC in DUT side')
        test.expect(test.r1.at1.send_and_verify('at+vts="1"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"1",1,0',timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="1"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"1",1,0', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="2"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"2",1,0', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="3"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"3",1,0', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="A"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"A",1,0', timeout=5))
        test.expect(test.r1.at1.send_and_verify('at+vts="#"', '.*OK.*'))
        test.expect(test.dut.at1.wait_for('+CIEV: dtmf,"#",1,0', timeout=5))
        test.expect(test.dut.at1.send_and_verify('ath', '.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
