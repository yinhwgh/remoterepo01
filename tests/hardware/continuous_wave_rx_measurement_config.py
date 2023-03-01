# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0092714.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init

from dstl.hardware import continuous_wave
from dstl.configuration import functionality_modes


class Test(BaseTest):
    """
    TC0092714.001 - ContinuousWaveRxMeasurementConfig
    Verification of different settings and syntax of at command responsible for measuring Continuous Wave signal.
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info('1. Check for available bands and technology.')
        available_blist = test.dut.dstl_get_available_bands()
        test.log.info('2. Set Factory Test Mode')
        test.expect(test.dut.dstl_set_factory_test_mode())
        test.log.info(
            '3. Check all possible settings, syntax, and ranges of command responsible for measuring Continuous Wave signal.')
        for band in available_blist:
            test.expect(test.dut.dstl_perform_measurement(band))
        test.log.info('4. Leave Factory Test Mode.')
        test.dut.dstl_set_full_functionality_mode()

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', 'OK'))


if "__main__" == __name__:
    unicorn.main()
