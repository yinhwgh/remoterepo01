#responsible: xiaowu.wu@thalesgroup.com
#location: beijing
#SRV03-4640

import unicorn
import math
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.configuration import scfg_radio_band
from dstl.network_service import register_to_network
from dstl.network_service.register_to_network import dstl_enter_pin
from itertools import combinations
from dstl.configuration.reset_to_factory_default_state import dstl_reset_to_factory_default
from dstl.auxiliary.write_json_result_file import *
class Test(BaseTest):
    """
    check all supported bands enabled or disabled with CatM and CatNB
    """

    def setup(test):
        test.log.step('1.Power on the module and wait for its ready')
        test.dut.dstl_detect()

    def run(test):
        test.log.step('2-3.Start a loop to select all possible radio/band settings')
        if test.dut.dstl_is_catm_supported():
            test.check_catm_band()
        if test.dut.dstl_is_nbiot_supported():
            test.check_catnb_band()

        test.log.step('4.Set at+cmee=2')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2'))

        test.log.step('5.Set catm_mask 0x00000000')
        test.expect(test.dut.at1.send_and_verify('at^scfg="radio/band/CatM","0x00000000"','CME ERROR: invalid index'))

        test.log.step('6.Configure AT^SCFG="Radio/Band/CatM","0x0"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatM","0x0"', 'CME ERROR: invalid index'))

        test.log.step('7.Configure AT^SCFG="Radio/Band/CatM","0","0"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatM","0","0"', '+CME ERROR: operation not supported'))

    def cleanup(test):
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(2)
        test.log.step('8. Factory reset the bands.')
        test.expect(dstl_reset_to_factory_default(test.dut))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')
        
    def get_all_supported_combination(test,testlist):
        band_list = [int(x, 16) for x in testlist]
        result = []
        #for i in range(1, len(band_list) + 1):
        #shrink the test range to save time.
        for i in range(1, 3):
            test = combinations(band_list, i)
            for item in test:
                result.append(hex(sum(item)))
        return result

    def get_unsupported_combination(test,testlist,list2=False):
        valuelist = []
        result = []
        i = int(1)
        while (i<32):
            value = str(hex(pow(2,i)))
            value = value[2:]
            if value not in testlist:
                valuelist.append(value)
            i = i+1
        for x in valuelist:
            if len(x)<8:
                x = '0'*(8-len(x))+x
                if not list2:
                    test.log.com('unsupported band list 1 include ' + x)
                else:
                    test.log.com('unsupported band list 2 include ' + x)
            result.append(x)
        return result

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
		
    def check_catm_band(test):
        test.log.step('2.Start test all cat-M band combination')
        band_catm_1 = test.dut.dstl_get_catm_band_list()
        band_catm_2 = test.dut.dstl_get_catm_band_list(catm_2=True)
        with_prefix_1 = test.get_all_supported_combination(band_catm_1)
        without_prefix_1 = test.convert2_hex32(with_prefix_1)
        with_prefix_2 = test.get_all_supported_combination(band_catm_2)
        without_prefix_2 = test.convert2_hex32(with_prefix_2)

        for band1 in without_prefix_1:
            for band2 in without_prefix_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatM","{band1}","{band2}"', 'OK'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatM"', f'SCFG: "Radio/Band/CatM","{band1}"','.*OK.*'))
                test.log.com('***** ban1: ' + band1 + ' -------band2: ' + band2)
				

        unsupported_band_1 = test.get_unsupported_combination(band_catm_1)
        unsupported_band_2 = test.get_unsupported_combination(band_catm_2, list2 = True)
        for band1 in band_catm_1:
            for band2 in unsupported_band_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatM","{band1}","{band2}"', '+CME ERROR: operation not supported'))
                test.log.com('***** ban1: ' + band1 + ' unsupported band2: ' + str(band2))
				
        for band1 in unsupported_band_1:
            for band2 in band_catm_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatM","{band1}","{band2}"', '+CME ERROR: operation not supported'))
                test.log.com('***** unsupported band1: ' + band1 + ' band2: ' + band2)
                
    def check_catnb_band(test):
        test.log.step('3.Start test all cat-NB band combination')
        band_catnb_1 = test.dut.dstl_get_catnb_band_list()
        band_catnb_2 = test.dut.dstl_get_catnb_band_list(catnb_2=True)
        with_prefix_1 = test.get_all_supported_combination(band_catnb_1)
        without_prefix_1 = test.convert2_hex32(with_prefix_1)
        with_prefix_2 = test.get_all_supported_combination(band_catnb_2)
        without_prefix_2 = test.convert2_hex32(with_prefix_2)
        for band1 in without_prefix_1:
            for band2 in without_prefix_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatNB","{band1}","{band2}"', 'OK'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatNB"', f'SCFG: "Radio/Band/CatNB","{band1}"','.*OK.*'))

        unsupported_band_1 = test.get_unsupported_combination(band_catnb_1)
        unsupported_band_2 = test.get_unsupported_combination(band_catnb_2, list2 = True)
        for band1 in band_catnb_1:
            for band2 in unsupported_band_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatNB","{band1}","{band2}"', '+CME ERROR: operation not supported'))
                test.log.com('***** ban1: ' + band1 + ' unsupported band2: ' + str(band2))
				
        for band1 in unsupported_band_1:
            for band2 in band_catnb_2:
                test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="Radio/Band/CatNB","{band1}","{band2}"', '+CME ERROR: operation not supported'))
                test.log.com('***** unsupported band1: ' + band1 + ' band2: ' + band2)
if "__main__" == __name__:
    unicorn.main()
