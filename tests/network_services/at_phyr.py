#responsible: minglin.zhu@thalesgroup.com
#location: Beijing
#SRV03-4789

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.identification import get_imei
from dstl.auxiliary.write_json_result_file import *

class  AtPHYR(BaseTest):
    """
        Test Case for LM0008373.001 - Iskraemeco: Randomized Network Registration (AT+PHYR) Skip to end of metadata
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_unlock_sim())
        test.expect(test.dut.dstl_restart())
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        test.log.info("Please make sure IMEI is available")
    def run(test):
        test.sleep(5)
        test.log.info("attach to network")
        test.expect(test.dut.dstl_register_to_network())
        test.log.info("****************LM0008373.001 at+phyr - begin*******************")
        test.log.info("************************************************")
        test.log.info("                   case 1.1                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=65535", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*"))
        
        test.log.info("************************************************")
        test.log.info("                   case 1.2                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=65536", "+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=1,1,1", "+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=abc", "+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=-1", "+CME ERROR: invalid index"))
        
        test.log.info("************************************************")
        test.log.info("                   case 1.3                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))

        '''
        #caculate PHYR time value according to the timing of URC printing.
        '''
        start_time_airplane_mode = time.time()
        test.log.info("SYSSTART AIRPLANE MODE print")

        test.log.info("start_time_airplane_mode: {}".format(start_time_airplane_mode))
        
        #test.sleep(1)
        test.expect(test.dut.at1.wait_for("^SYSSTART"))
        test.log.info("^SYSSTART is printed")

        start_time_system_start = time.time()
        phyr_value = start_time_system_start - start_time_airplane_mode

        test.log.info("start_time_system_start: {}, PHYR timer value: {}".format(start_time_system_start,phyr_value))
        
        test.expect(test.dut.dstl_register_to_network())

        test.sleep(5)

        test.expect(test.dut.at1.send_and_verify("AT+PHYR?", "\s+\+PHYR: 60\s+"))
 
        test.log.info("************************************************")
        test.log.info("                   case 1.4                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.wait_for('^SYSSTART AIRPLANE MODE')==False)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\s+\+CFUN: 1\s+"))
        test.expect(test.dut.dstl_register_to_network())
        
        test.log.info("************************************************")
        test.log.info("                   case 2.1                    ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\s+\+CFUN: 4\s+"))
        test.expect(test.dut.at1.send_and_verify("at+cfun=1", expect="\s+\^SYSSTART\s+",
                                                         wait_for="\s+\^SYSSTART\s+"))   
        test.expect(test.dut.dstl_register_to_network())
        test.sleep(5)

        test.log.info("************************************************")
        test.log.info("                   case 2.2                    ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\s+\+CFUN: 4\s+"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=5", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cfun=1", expect="\s+\^SYSSTART\s+",
                                                         wait_for="\s+\^SYSSTART\s+"))  

        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 1"))
        test.expect(test.dut.dstl_register_to_network())
      
        test.log.info("************************************************")
        test.log.info("                   case 2.3                    ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=5", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 5"))
        test.sleep(phyr_value)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 5"))

        test.log.info("************************************************")
        test.log.info("                   case 2.4                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+cops=0", "+CME ERROR: operation not supported"))
        test.expect(test.dut.at1.send_and_verify("AT+cops=2", "+CME ERROR: operation not supported"))
 
        test.log.info("************************************************")
        test.log.info("                   case 2.5                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=5", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 5"))

        test.log.info("************************************************")
        test.log.info("                   case 2.6                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "+CFUN: 0"))

        test.log.info("************************************************")
        test.log.info("                   case 2.7                     ")
        test.log.info("************************************************")
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=4", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart())
       
        test.log.info("************************************************")
        test.log.info("                   case 3.1                     ")
        test.log.info("************************************************")
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))
        test.sleep(phyr_value)
        test.expect(test.dut.dstl_unlock_sim())
        test.expect(test.dut.dstl_register_to_network())

        test.log.info("************************************************")
        test.log.info("                   case 3.2                     ")
        test.log.info("************************************************")
        test.expect(test.dut.dstl_lock_sim())

        test.expect(test.dut.at1.send_and_verify("AT+PHYR=60", ".*OK.*"))
        test.expect(test.dut.dstl_restart(expect_urc="^SYSSTART AIRPLANE MODE"))

        test.expect(test.dut.dstl_unlock_sim())
        #restart 3-5s,start PHYR timer when print SYSSTART AIRPLANE MODE,unlock sim 1s, 
        # 5 is not a Exact value, just for check DUT should not receive ^systart immediatly
        if phyr_value > 5: 
            test.expect(test.dut.at1.wait_for("^SYSSTART",timeout = 5) == False )
        
        test.expect(test.dut.at1.wait_for("^SYSSTART"))

        test.expect(test.dut.dstl_register_to_network())
     
        test.log.info("****************LM0008373.001 at+phyr - end*******************")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+PHYR=0", ".*OK.*")) 
        test.expect(test.dut.dstl_restart())
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                    test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                    test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key', default='no_test_key') + ') - End *****')


if "__main__" == __name__:
    unicorn.main()