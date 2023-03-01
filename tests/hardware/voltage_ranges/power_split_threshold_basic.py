#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091973.002 - PowerSplit_ThresholdBasic


import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.security.lock_unlock_sim import dstl_unlock_sim,dstl_lock_sim
from dstl.configuration import functionality_modes

class ATSbvBasic(BaseTest):

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.step("SetUp_1: Initiate DUT and set configurations")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/CFUN",1',"OK"))

        test.log.info("*******************************************************************")
        test.log.step("SetUp_2: Enable DUT SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.step("RunTest_1: Check the default <vthresh> value before input SIM PIN")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup/threshold"','\^SCFG: "MEShutdown/sVsup/threshold","0"',wait_for ="OK", timeout=30))


        test.log.info("*******************************************************************")
        test.log.step("RunTest_2: Set <vthresh> with different valid values before input SIM PIN")
        test.log.info("*******************************************************************")
        vthresh_list = [-4, -3, -2, -1, 1, 2, 3, 4, 0]
        for vthresh in vthresh_list:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEShutdown/sVsup/threshold",{vthresh}',"OK"))
            test.dut.dstl_restart()
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup/threshold"',
                                                     f'\^SCFG: "MEShutdown/sVsup/threshold","{vthresh}"', wait_for="OK",
                                                     timeout=30))

        test.log.info("*******************************************************************")
        test.log.step("RunTest_3: Set <vthresh> with different valid values after input SIM PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_enter_pin()
        for vthresh in vthresh_list:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEShutdown/sVsup/threshold",{vthresh}',"OK"))
            test.dut.dstl_restart()
            test.dut.dstl_enter_pin()
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup/threshold"',
                                                     f'\^SCFG: "MEShutdown/sVsup/threshold","{vthresh}"', wait_for="OK",
                                                     timeout=30))

        test.log.info("*******************************************************************")
        test.log.step("RunTest_4: Repeat step 2 after change CFUN mode from 1 to 0")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_set_functionality_mode(0))
        for vthresh in vthresh_list:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEShutdown/sVsup/threshold",{vthresh}', "OK"))
            test.dut.dstl_restart()
            test.sleep(2)
            test.expect(test.dut.dstl_set_functionality_mode(0))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup/threshold"',
                                                     f'\^SCFG: "MEShutdown/sVsup/threshold","{vthresh}"', wait_for="OK",
                                                     timeout=30))

        test.log.info("*******************************************************************")
        test.log.step("RunTest_5: Set <vthresh> with different invalid values")
        test.log.info("*******************************************************************")
        invalid_vthresh_list = [-5,5,-6,6,"a","A"]
        for in_vthresh in invalid_vthresh_list:
            test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEShutdown/sVsup/threshold",{in_vthresh}', "ERROR"))

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Restore to default configurations")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_set_functionality_mode(1))
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK",timeout=30))


if (__name__ == "__main__"):
    unicorn.main()