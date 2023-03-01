#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0105210.001	SIMRefresh_AutomaticResponseMode_Basic


'''
This test script only valid for Viper
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




class SIMRefresh_AutomaticResponseMode(BaseTest):


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
        test.dut.dstl_restart()
        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Switch on SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.dstl_switch_on_sat_urc()
        #test.dut.dstl_restart()


    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Check default refresh mode and default refuse reason in teminal response ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "SAT/AR/REFRESH"','^SCFG: "SAT/AR/REFRESH","0","2002"'))


        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Sent a refresh SSTK command ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010382028182"','030100',wait_for='030100'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Set refresh mode to 2")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "SAT/AR/REFRESH",2', '^SCFG: "SAT/AR/REFRESH","2","2002"'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Sent a refresh SSTK command ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010382028182"', '03022002',wait_for='03022002'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Change teminal response refuse reason to other valid value")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "SAT/AR/REFRESH",2,"FFFF"', '^SCFG: "SAT/AR/REFRESH","2","ffff"'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Sent a refresh SSTK command ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SSTK="D009810301010382028182"', '0302FFFF', wait_for='0302FFFF'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Restart module and check if restore to default refresh mode and default teminal response refuse reason")
        test.log.info("*******************************************************************")
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SAT/AR/REFRESH"', '^SCFG: "SAT/AR/REFRESH","0","2002"'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Set the refresh mode to other invalid values")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="SAT/AR/REFRESH",-1', 'ERROR'))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_9: Set the refuse reason in teminal response to other invalid values")
        test.log.info("*******************************************************************")
        test.expect(
            test.dut.at1.send_and_verify('AT^SCFG="SAT/AR/REFRESH",2,"HHHH"', 'ERROR'))



    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Switch off SAT/URC")
        test.log.info("*******************************************************************")
        test.dut.at1.send_and_verify('AT^SCFG="SAT/URC","0"', ".*OK.*", timeout=30)



if (__name__ == "__main__"):
    unicorn.main()
