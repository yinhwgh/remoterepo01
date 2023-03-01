# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0094161.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class AudioModeBasicFunc(BaseTest):
    """
    To test Audio Mode function
    1. Check the module status
    2. set appropriate audio mode,
    3. check all supported audio modes ,
    4. check current selected audio mode ,
    5. check all possible digital audio interface configuration combinations,
    6. restart module and check if the powerup values of audio mode parameters are set,
    7. do all steps from point 3 to 5 for all supported audio modes.
    8.reset audio parameters to default values
    """
    def setup(test):

        dstl_detect(test.dut)
        test.log.info('Reset to default value')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        test.log.info('check all supported audio interfaces with AT^SAIC test command via AT^SAIC')
        # check AT^SNFS default value
        test.expect((test.dut.at1.send_and_verify("AT^SAIC=?",".*OK.*")))

        # check AT^SAIC default value
        test.expect(test.dut.at1.send_and_verify("AT^SAIC?", '5,1,1,3,0,0,1,1','.*OK.*'))
        # check audio mode and audio interface setting
        # for every audio mode check whether audio interface setting is right
        for audio_mode in [1, 2, 3, 4, 5, 6]:
            test.expect(test.dut.at1.send_and_verify('AT^SNFS={}'.format(audio_mode), '.*OK.*'))
            for io in [4, 5]:
                for bclk in [0, 1, 2, 3]:
                    for mode in [0]:
                        for frame_mode in [0, 1]:
                            for clk_mode in [1]:
                                for sample_rate in [0, 1]:
                                    if bclk == 0 and sample_rate == 0:
                                        test.expect(test.dut.at1.send_and_verify('AT^SAIC={},1,1,{},{},{},{},{}'.format(
                                            io, bclk, mode, frame_mode, clk_mode, sample_rate), '.*ERROR.*'))
                                    else:
                                        test.expect(test.dut.at1.send_and_verify('AT^SAIC={},1,1,{},{},{},{},{}'.format(
                                            io, bclk, mode, frame_mode, clk_mode, sample_rate), '.*OK.*'))
        dstl_restart(test.dut)
        test.expect(test.dut.at1.send_and_verify('AT^SAIC?','5,1,1,3,0,0,1,1','.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SNFS?', '1', '.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()







