#responsible: jiaqiang.liu@thalesgroup.com
#location: Beijing
#SRV03-4672

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_enter_pin
from os.path import join
from dstl.configuration.reset_to_factory_default_state import dstl_reset_to_factory_default
from dstl.configuration.scfg_radio_band import dstl_is_default_radio_band
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):
        test.log.step('1.Execute AT^SCFG="MEopMode/Factory","all" to reset module to default state shipped from factory.')
        test.log.h2('AT^SCFG="MEopMode/Factory","all" is PIN protected sub-command,enter PIN to unlock it.')
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(2)

        test.log.h2('To reset module to default state.')
        test.expect(dstl_reset_to_factory_default(test.dut))

        test.log.step('2.Check whether the radio band setting is match the default radio band setting.')
        test.expect(dstl_is_default_radio_band(test.dut), critical=True)

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')
        pass

if "__main__" == __name__:
   unicorn.main()