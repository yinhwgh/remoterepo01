#responsible: wenbin.du@thalesgroup.com
#location: Beijing
#SRV03-4882

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network, network_monitor
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes
from dstl.identification import get_imei
from dstl.auxiliary.write_json_result_file import *

class  AtCRCES(BaseTest):
    """
        Test Case for LM0008394.001 - Report Coverage Enhancement Status in LTE Cat.M/NB
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        test.log.info("Please make sure IMEI is available")
    def run(test):
        test.sleep(1)
        test.log.info("**************** LM0008394.001 at+crces - begin *******************")
        test.log.info("************************************************")
        test.log.info(" case 1.1  To verify the test function and execution function works well. ")
        test.log.step('1. Check the test command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES=?", ".*OK.*"))
        test.log.step('2. Force module to register on LTE CatM ')
        test.expect(test.dut.dstl_register_to_lte())
        test.log.step('3. Check the execute command of SMONI and CRCES, the CE level should be the same ')
        smoni_ce_level = test.dut.dstl_monitor_network_ce_level()
        test.expect(test.dut.dstl_report_coverage_enhancement_status() == smoni_ce_level)
        test.log.step('4. Force module to register on LTE CatNB ')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatNB","90"', 'OK'))
        test.expect(test.dut.dstl_register_to_nbiot())
        test.log.step('5. Check the execute command of SMONI and CRCES, the CE level should be the same ')
        smoni_ce_level = test.dut.dstl_monitor_network_ce_level()
        test.expect(test.dut.dstl_report_coverage_enhancement_status() == smoni_ce_level)
        # GSM was removed in TX62-W-C
        # test.log.step('6. Force module to register on GSM ')
        # test.expect(test.dut.dstl_register_to_gsm())
        # test.log.step('7. Check the execute command of CRCES ')
        # test.expect(test.dut.at1.send_and_verify("AT+CRCES", ".*OK.*"))

        test.log.info("************************************************")
        test.log.info(" case 1.2 Test module's behavior in PIN enabled/Airplane mode/de-registered status. ")
        test.log.step('1. Enable PIN code and restart module ')
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.log.step('2. Check the execute command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES", "+CME ERROR: SIM PIN required"))
        test.log.step('3. Unlock PIN code and force module to airplene mode ')
        test.expect(test.dut.dstl_unlock_sim())
        test.expect(test.dut.dstl_set_airplane_mode())
        test.log.step('4. Check the execute command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES", "+CRCES: 0,0,0"))
        test.log.step('5. Force mudule to de-registered status ')
        test.log.step('6. Check the execute command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES", "+CRCES: 0,0,0"))

        test.log.info("************************************************")
        test.log.info(" case 1.3  Test module's behavior with improper setting. ")
        test.log.step('1. Check the write command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES=0", "+CME ERROR: operation not supported"))
        test.log.step('2. Check the read command of CRCES ')
        test.expect(test.dut.at1.send_and_verify("AT+CRCES?", "+CME ERROR: unknown"))

        test.log.info("**************** LM0008394.001 at+crces - end*******************")

    def cleanup(test):
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatNB","00"', 'OK'))
        test.expect(test.dut.dstl_restart())
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()