# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0071771.002

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class AudioModesTwoToSix(BaseTest):
    """
    1.Set all current parameters to manufacturer defaults
    2.The status of the module should be AUDIO-MODE 1 - default handset used
    3.Set up a voice connection (default handset used)
    4.The user has to coice the Audio Mode, he wants to test
    5.Verify the Mute function
    6.It is possible to change any audio parameter in Audio modes 2-6
    7.Try to change audio input path parameters (microphone)
    8.Try to change audio output path parameters (loudspeaker)
    9.Terminate the voice connection.
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
        print(result)
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
            test.expect(test.dut.at1.send_and_verify('at^snfo=57,33,0,{}'.format(rxVolStep), '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('ath', '.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
