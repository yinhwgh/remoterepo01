#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091896.001 - TpAtSbvBasic

'''
Test with McTest4 board
'''

import unicorn
import re

from core.basetest import BaseTest

from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_umts
from dstl.auxiliary.init import dstl_detect
from dstl.security.lock_unlock_sim import dstl_unlock_sim,dstl_lock_sim
from dstl.call.setup_voice_call import dstl_voice_call_by_number,dstl_release_call,dstl_check_voice_call_status_by_clcc,dstl_is_voice_call_supported

class ATSbvBasic(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate DUT and restore to default configurations")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Initiate Remote module and register to network")
        test.log.info("*******************************************************************")
        test.r1.detect()
        test.r1.dstl_register_to_network()


        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Enable DUT SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Test SBV before input SIM PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT^SBV=?", "OK", timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT^SBV", "\^SBV: (4\d{3}|3\d{3})", wait_for = "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Test SBV after input SIM PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify("AT^SBV=?", "OK", timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT^SBV", "\^SBV: (4\d{3}|3\d{3})", wait_for = "OK",timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Test SBV during a call")
        test.log.info("*******************************************************************")
        if test.dut.dstl_is_voice_call_supported() == True:
            test.dut.dstl_register_to_umts()
            test.dut.dstl_voice_call_by_number(test.r1,test.r1.sim.nat_voice_nr)
            test.sleep(2)
            test.dut.dstl_check_voice_call_status_by_clcc(number=test.r1.sim.nat_voice_nr)
            test.expect(test.dut.at1.send_and_verify("AT^SBV", "\^SBV: (4\d{3}|3\d{3})", wait_for="OK", timeout=30))
            test.dut.dstl_release_call()
        else:
            test.log.info("DUT doesn't support call functionality, skip this step!")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Test SBV during a call")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT^SBV=1", "ERROR", timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT^SBV?", "ERROR", timeout=30))

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))


if (__name__ == "__main__"):
    unicorn.main()