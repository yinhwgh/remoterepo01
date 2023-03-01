# responsible: jie.jin@thalesgroup.com
# location: Beijing
# TC0093921.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode


class AudioInterfaceSet(BaseTest):
    """
    To test Audio Interface function
    1. check all supported audio interfaces with AT^SAIC test command,
    2. check settings for current audio interface with use AT^SAIC read command,
    3. try to change current audio interface settings with use AT^SAIC write command,
    4. check if previous changes takes effect immediately,
    5. restart module,
    6. check if previous changes are saved.
    """
    def setup(test):

        dstl_detect(test.dut)
        test.log.info('Reset to default value')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))

    def run(test):
        test.log.info('1.check all supported audio interfaces with AT^SAIC test command via AT^SAIC')
        # check AT^SNFS default value
        test.expect((test.dut.at1.send_and_verify("AT^SAIC=?", ".*OK.*")))

        # check AT^SAIC default value
        test.expect(test.dut.at1.send_and_verify("AT^SAIC?", ".*5,1,1,3,0,0,1,1.*"))
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
        test.expect(test.dut.at1.send_and_verify('AT^SAIC?', '5,1,1,3,0,0,1,1','.*OK.*'))

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()







