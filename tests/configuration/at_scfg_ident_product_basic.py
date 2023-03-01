#responsible: jiaqiang.liu@thalesgroup.com
#location: Beijing
#SRV03-4795

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
from dstl.configuration.ident_product import dstl_set_ident_product
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

        #test.log.step('2.Execute AT+CFUN=1,1 to restart the module.')
        #test.log.h2('To restart module')
        #test.expect(dstl_restart(test.dut))

        test.log.step('2.Execute AT^SCFG="+" to get the default product name.')
        default_productname=dstl_get_ident_product(test.dut)
        test.log.h2('The default product name is {}.'.format(default_productname))

        test.log.step('3.Execute AT^SCFG="Ident/Product","MyProductName" to specified user defined product name.')
        #test.expect(dstl_set_ident_product(test.dut,"MyProductName"), '.*{}.*'.format("MyProductName"))
        test.expect(dstl_set_ident_product(test.dut,"MyProductName"), critical=True)

        test.log.step('4.Execute AT^SCFG="Ident/Product" to get user defined product name and check whether it equals to {} or not.'.format("MyProductName"))
        test.expect(dstl_get_ident_product(test.dut),".*MyProductName.*")

        test.log.step('5.Execute AT^SCFG="Ident/Product","{}" to set the default product name back.'.format(default_productname))
        #test.expect(dstl_set_ident_product(test.dut,default_productname), '.*{}.*'.format(default_productname))
        test.expect(dstl_set_ident_product(test.dut,default_productname), critical=True)

        test.log.step('6.Execute AT^SCFG="Ident/Product" to get the default product name and check whether it equals to {} or not.'.format(default_productname))
        test.expect(dstl_get_ident_product(test.dut),".*{}.*".format(default_productname))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')
        pass           

if "__main__" == __name__:
   unicorn.main()