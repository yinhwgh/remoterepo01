# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0085473.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class DaiWithDifAudioModiQct(BaseTest):
    """
    1.Change of audio modes (2-6) within an existing voice call over the Digital Audio Interface.
    2.Activation and registration of subscriber1 (counterpart).
    3.Activation configuration and registration of DUT.
    4.Selection of digital audio interface on DUT.
    5.MO call from DUT -> Subscriber 1.
    6.Check of audio functionality (speech in up/down link direction)
    7.for audio modes 2 - 6 and different clock rates.
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
        test.log.info('1.1 Register into network')
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        test.log.info('check the audio mode')
        test.expect(test.dut.at1.send_and_verify('at^snfs?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^snfs=?','.*OK.*'))
        test.log.info('set up call')
        test.expect(test.dut.at1.send_and_verify('ATD{};'.format(test.r1.sim.nat_voice_nr), '.*OK.*'))
        test.r1.at1.wait_for('RING')
        test.sleep(2)
        test.expect(test.r1.at1.send_and_verify('ata', '.*OK.*'))
        test.log.info('Check mute function')
        test.expect(test.dut.at1.send_and_verify('at+cmut=0','.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cmut=1', '.*OK.*'))
        test.log.info('get the audio mode value')
        test.expect(test.dut.at1.send_and_verify('at^snfs=?', '.*OK.*'))
        result = re.findall('\^SNFS: \(1-(\\d+)\)', test.dut.at1.last_response)
        audMode = int(result[0])
        test.log.info('check if all the audio mode value can be set into module')
        for audmode in range(2, audMode):
            test.expect(test.dut.at1.send_and_verify('at^snfs={}'.format(audmode), '.*OK.*'))
        test.log.info('Try to change audio input path parameters (microphone)')
        test.expect((test.dut.at1.send_and_verify('at^snfi?','.*OK.*')))
        test.log.info('Try to change audio output path parameters (loudspeaker)')
        test.log.info('get the audio output value')
        test.expect((test.dut.at1.send_and_verify('at^snfo=?', '.*OK.*')))
        test.log.info('set audio output parameters')
        for rxVolStep in range(6):
            test.expect(
                    test.dut.at1.send_and_verify('at^snfo=57,33,0,{}'.format(rxVolStep), '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ath', '.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
