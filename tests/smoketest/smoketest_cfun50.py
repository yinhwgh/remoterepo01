# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095489.001
# jira: xxx
# feature: LM0000307.001, LM0003039.001, LM0003039.002, LM0003039.003,
# LM0003039.005, LM0003039.006, LM0004489.001, LM0004489.002, LM0004489.003, LM0004489.004, LM0004489.005

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.restart_module import dstl_restart
import re

class Test(BaseTest):

    def own_restart(test):
        'extra restart function, because Tiger has no Mctest connected'
        'to call via test.own_restart()'

        if (re.search(test.dut.project, 'TIGER')):
            test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
            test.sleep(20)
            test.dut.at1.send_and_verify("ati", "MTK2")
            test.sleep(1)
            result = 1
        else:
            result = test.dut.dstl_restart()
        return result

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()
        # open log port if set in config for receive EXITs
        if hasattr(test.dut, 'log'):
            test.dut.log.open()
        # SIM PIN must be active
        test.dut.at1.send_and_verify("AT+CPIN?", "OK")
        res = test.dut.at1.last_response
        if "READY" in res:
            # check if SIM PIN is active
            test.dut.dstl_lock_sim()
        else:
            test.log.info("SIM PIN is active")


    def run(test):
        """
        Intention:
        Simple restart check check
        without and with SIM PIN and registration
        """
        loop = 25
        timebetweenrestarts = 5 # wait time at the end of every restart loop in sec
        test.log.step('Step 1: Restart module in a loop of ' + str(loop ) + " without Pin entered and network registration")
        n=0
        i=0
        while n<2:
            while i<loop:
                if ( n==0):
                    test.log.info("++++++++++++++++++++++++ restart loop " + str(i+1) + " ++++++++++++++++++++++++")
                else:
                    if ( i==0):
                        test.log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                        test.log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                        test.log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                        test.log.step(
                            'Step 2: Restart module in a loop of ' + str(loop) + " with Pin and network registration")
                    test.log.info("+++++++++++++++++++++++ restart loop with registration " + str(i+1) + " +++++++++++++++++++++++")
                test.expect(test.own_restart())
                test.expect(test.dut.at1.send_and_verify("ati1", "OK"))
                test.dut.at1.send_and_verify("AT^sos=ver", "O")
                test.dut.at1.send_and_verify("AT^siekret=0", "O")
                test.dut.at1.send_and_verify("AT^cicret=swn", "O")
                test.expect(test.dut.at1.send_and_verify("AT+cpin?", "SIM PIN"))
                if ( n==1):
                    if (test.dut.project != 'TIGER' ):
                        test.dut.at1.send_and_verify("AT^cicret=swn", "O")
                        test.expect(test.dut.dstl_register_to_network())
                    else:
                        # with network registration
                        test.expect(test.dut.dstl_enter_pin())
                        j=0
                        while j<5:
                            test.dut.at1.send_and_verify("AT+CREG?", "OK")
                            res = test.dut.at1.last_response
                            if "+CREG: 0,1" in res:
                                test.log.info("Module is registered")
                                j=10
                            else:
                                test.log.info("Module is not registered, wait 5 secons and check it again")
                                test.sleep(5)
                                j +=1
                        if j != 10:
                            # loop was finish without network register
                            test.expect(False)
                i +=1
                test.sleep(timebetweenrestarts)
            n +=1
            i=0

    def cleanup(test):
        """Cleanup method.
		Nothing to do in this Testcase
        Steps to be executed after test run steps.
        """

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
