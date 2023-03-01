#responsible: jiaqiang.liu@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_enter_pin
from os.path import join
from dstl.configuration.reset_to_factory_default_state import dstl_reset_to_factory_default
from dstl.configuration.ident_product import dstl_get_ident_product
from dstl.configuration.configure_scfg_provider_profile import dstl_get_provider_auto_select
from dstl.configuration.configure_scfg_provider_profile import dstl_read_provider_profile_config
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
       
        test.log.step('2.Execute AT^SCFG="MEopMode/Prov/AutoSelect" to get the default providor auto select.')
        default_provider_autoselect=dstl_get_provider_auto_select(test.dut)
        test.log.h2('The default provider auto select is {}'.format(default_provider_autoselect))

        test.log.step('3.Execute AT^SCFG="MEopMode/Prov/cfg" to get the default provider profile config.')
        default_provider_profileconfig=dstl_read_provider_profile_config(test.dut)
        test.log.h2('The default provider profile config is {}'.format(default_provider_profileconfig))

        if default_provider_autoselect.upper() == "ON":#
            if default_provider_profileconfig.lower() == "fallb3gpp":#
                test.expect(True)
            else:
                test.expect(False)
        else:
            test.expect(False)

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')
        pass

if "__main__" == __name__:
   unicorn.main()