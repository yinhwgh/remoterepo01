#responsible: bin.chen@thalesgroup.com
#location: Beijing
#This script is only for serval_step6(TX62-W-C)
#SRV03-4786

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import  dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import customization_network_types
from dstl.network_service import network_monitor
from dstl.security import lock_unlock_sim
from dstl.configuration.functionality_modes import dstl_set_airplane_mode,dstl_set_full_functionality_mode
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.info('********************^KCELL Test Start******************************')
        test.log.step("=== 1. +KCELL: monitor serving cell in registered state in CAT-M ===")
        test.dut.dstl_restart()
        test.sleep(15)
        test.expect(test.dut.dstl_register_to_lte())
        test.sleep(30)
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-M', 'registered',False))

        #This case can be only verified with R&S CMW Card
        test.log.step("=== 2. +KCELL: monitor serving cell and neighbor cell in registered state in CAT-M shall shall be verified manually! ===") 

        test.log.step("=== 3. +KCELL: monitor serving cell and neighbor cell in deregistered state ===")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-M', 'deregistered',False))
        test.expect(test.dut.dstl_register_to_lte())
        test.sleep(5)

        test.log.step("=== 4. +KCELL: test with invalid parameters ===")
        test.expect(test.dut.dstl_monitor_network_kcell(10,'CAT-M'))
        test.sleep(2)
        test.expect(test.dut.dstl_monitor_network_kcell(255,'CAT-M'))

        test.log.step("=== 5. +KCELL: monitor serving cell in registered state in CAT-NB ===")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatNB","96","0"', ".*OK.*"))
        test.expect(test.dut.dstl_register_to_nbiot())
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-NB','registered'))
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatNB","0","0"', ".*OK.*"))

        test.log.step("=== 6. +KCELL: monitor serving cell in pin and airplane protected mode ===")
        test.expect(dstl_set_airplane_mode(test.dut))
        test.sleep(5)
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-M', 'deregistered',False))
        test.sleep(5)
        test.expect(test.dut.dstl_lock_sim())
        test.dut.dstl_restart()
        test.sleep(15)
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-M', 'deregistered',False))
        test.sleep(5)
        test.expect(test.dut.dstl_unlock_sim())
        test.dut.dstl_restart()
        test.sleep(15)
        test.expect(test.dut.dstl_register_to_lte())
        test.sleep(30)
        test.expect(test.dut.dstl_monitor_network_kcell(0,'CAT-M', 'registered',False))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + 'test_key' + ') - End *****')

if "__main__" == __name__:
    unicorn.main()