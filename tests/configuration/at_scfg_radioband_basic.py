#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092851.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.configuration import scfg_radio_band
from dstl.network_service import register_to_network
from itertools import combinations

class Test(BaseTest):
    """
    TC0092851.001 - TpAtSCFGRadioBandBasic
    check all supported bands enabled or disabled with 2G/3G/4G
    TimeSpend: about 15H
    """

    def setup(test):
        test.log.step('1.Power on the module and wait for its ready')
        test.dut.dstl_detect()

    def run(test):
        test.log.step('2-4.Start a loop to select all possible radio/band settings')
        if test.dut.dstl_is_gsm_supported():
            test.check_2g_band()
        if test.dut.dstl_is_umts_supported():
            test.check_3g_band()
        if test.dut.dstl_is_lte_supported():
            test.check_4g_band()

        test.log.step('5.Set at+cmee=2')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2'))

        test.log.step('6.Set umts_mask or lte_mask to 0x00000000')
        test.expect(test.dut.at1.send_and_verify('at^scfg="radio/band/3G","0x00000000"','ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="radio/band/4G","0x00000000"','ERROR'))

        test.log.step('7.For 3G, configure AT^SCFG="radio/band", 3G')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band", 3G','CME ERROR: invalid index'))

        test.log.step('8.For 4G, configure AT^SCFG="radio/band", 4G')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="radio/band", 4G', 'CME ERROR: invalid index'))

        test.log.step('9.Configure AT^SCFG="Radio/Band/3G","0x0"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/3G","0x0"', 'CME ERROR: invalid index'))

        test.log.step('10.Configure AT^SCFG="Radio/Band/4G","00000002"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/4G","00000002"', 'CME ERROR: invalid index'))

        test.log.step('11. Enable airplane mode')
        test.expect(test.dut.dstl_set_airplane_mode())

        test.log.step('12. Set radio band under 2g/3g/4g')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/2G","2"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/3G","2"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/4G","2","0"', 'OK'))


        test.log.step('13. Check at+cfun?')
        test.expect(test.dut.at1.send_and_verify('at+cfun?', 'CFUN: 4'))

        test.log.step('14. Disable airplane mode with at+cfun=1')
        test.expect(test.dut.dstl_set_full_functionality_mode())

        test.log.step('15. Check at+cfun?')
        test.expect(test.dut.at1.send_and_verify('at+cfun?', 'CFUN: 1'))


    def cleanup(test):
        test.log.step('16. Restore to all bands')
        test.expect(test.dut.dstl_set_all_radio_bands())
        test.expect(test.dut.max_band_config_check())


    def get_all_supported_combination(test,testlist):
        band_list = [int(x, 16) for x in testlist]
        test = combinations(band_list, 2)
        result = []
        for i in range(1, len(band_list) + 1):
            test = combinations(band_list, i)
            for item in test:
                result.append(hex(sum(item)))
        return result

    #for viper format
    def convert2_hex32(test,testlist):
        result = []
        for x in testlist:
            x = x[2:]
            if len(x)<8:
                x = '0'*(8-len(x))+x
            result.append(x)
        count = len(result)
        test.log.info(f'Total {count} Radio band combination to be test: {result}')
        return result

    def check_2g_band(test):
        test.log.step('2.Start test all 2G band combination')
        band_2g = test.dut.dstl_get_2g_band_list()
        with_prefix = test.get_all_supported_combination(band_2g)
        without_prefix = test.convert2_hex32(with_prefix)
        for band in without_prefix:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/2G","{band}"', 'OK'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/2G"', f'SCFG: "Radio/Band/2G","{band}".*OK.*'))

    def check_3g_band(test):
        test.log.step('3.Start test all 3G band combination')
        band_3g = test.dut.dstl_get_3g_band_list()
        with_prefix = test.get_all_supported_combination(band_3g)
        without_prefix = test.convert2_hex32(with_prefix)
        for band in without_prefix:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/3G","{band}"', 'OK'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/3G"', f'SCFG: "Radio/Band/3G","{band}".*OK.*'))

    def check_4g_band(test):
        test.log.step('4.Start test all 4G band combination')
        band_4g_1 = test.dut.dstl_get_4g_band_list()
        band_4g_2 = test.dut.dstl_get_4g_band_list(fourg_2=True)
        with_prefix_1 = test.get_all_supported_combination(band_4g_1)
        without_prefix_1 = test.convert2_hex32(with_prefix_1)
        with_prefix_2 = test.get_all_supported_combination(band_4g_2)
        without_prefix_2 = test.convert2_hex32(with_prefix_2)
        for band1 in without_prefix_1:
            for band2 in without_prefix_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/4G","{band1}","{band2}"', 'OK'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/4G"', f'SCFG: "Radio/Band/4G","{band1}"','.*OK.*'))


if "__main__" == __name__:
    unicorn.main()
