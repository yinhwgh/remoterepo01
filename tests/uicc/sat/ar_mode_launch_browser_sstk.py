#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104189.001- TpSATLaunchBrowser_AR_SSTK

'''
This test script only valid for Serval Step1
'''

import unicorn
import random
import re
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control
from dstl.usat.ssta_command import *
from dstl.usat.sim_instance import *
#from dstl.usat.local_ssta_mode import *




class SATLaunchBrowser_AR_SSTK(BaseTest):


    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=30))
        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()
        test.dut.dstl_register_to_network()
        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Set Module to AR mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_set_and_check_ssta_mode(0,0,False)
        #test.dut.dstl_enable_ar_mode()

        test.log.info("*******************************************************************")
        test.log.info("SetUp_4: Switch on SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.dstl_switch_on_sat_urc()
        #test.dut.dstl_restart()


    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Send the launch browser SSTK to module and check the terminal response")
        test.log.info("*******************************************************************")
        SSTK_Command = '"D038810301150082028182311B687474703A2F2F6461767335312E697076342E6572696373736F6E0500470E0462657231086572696373736F6E"'
        SSTK_Response = '[08]103011500[08]2028281[08]30130'

        test.expect(test.dut.at1.send_and_verify('AT^SSTK={}'.format(SSTK_Command),SSTK_Command,SSTK_Response,30))
        test.expect(re.search(SSTK_Response,test.dut.at1.last_response))

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Switch off SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.at1.send_and_verify('AT^SCFG="SAT/URC","0"', ".*OK.*", timeout=30)



if (__name__ == "__main__"):
    unicorn.main()
