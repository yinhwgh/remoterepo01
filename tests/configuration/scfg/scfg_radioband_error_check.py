#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0105076.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration import scfg_radio_band
from dstl.auxiliary import restart_module


class Test(BaseTest):
    '''
    TC0105076.001 - SCFGRadioBandError_DefaultCheck
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1. Restart module and check radio band setting ")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_set_all_radio_bands())
        test.expect(test.dut.max_band_config_check())
        test.log.step("2. Set a valid band but not in band support list, "
                      "check should respond with an error")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band/4G",20000000,00000002000001a0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band/4G",20000001,00000002000001a0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band/3G",20000000','ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band/3G",20000004','ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band/2G",00000010', 'ERROR'))
        test.expect(test.dut.max_band_config_check())

    def cleanup(test):
        test.expect(test.dut.dstl_set_all_radio_bands())
        test.expect(test.dut.max_band_config_check())


if '__main__' == __name__:
    unicorn.main()

