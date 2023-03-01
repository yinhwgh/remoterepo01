# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095389.001
# jira: xxx
# feature: LM0000331.001, LM0001323.001, LM0003216.001, LM0003216.002, LM0003216.003, LM0003216.004
# LM0003216.005, LM0003216.007, LM0004449.001, LM0004449.002, LM0004449.003, LM0004449.006

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.restart_module import dstl_restart
import re

class Test(BaseTest):

    def own_restart(test,SIMPIN):
        'extra restart rotine, because Tiger has no Mctest connected'
        'call via test.own_restart()'
        if (re.search(test.dut.project, 'TIGER')):
            test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
            test.sleep(20)
            test.dut.at1.send_and_verify("ati", "MTK2")
            if SIMPIN:
                test.expect(test.dut.at1.send_and_verify("at+CPIN?", "SIM PIN"))
            else:
                test.expect(test.dut.at1.send_and_verify("at+CPIN?", "READY"))
            test.sleep(1)
        else:
            test.dut.dstl_restart()
        return 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_collect_module_info_for_mail()

    def run(test):
        """
        Intention:
        Simple check of the ati command with all parameters
        """
        test.log.step('Step 1: check if PIN is entered - Start')

        test.log.step('Step 1a: If PIN was is not entered, enter PIN')
        test.dut.at1.send_and_verify("at+cpin?", "OK")
        res = test.dut.at1.last_response
        if "SIM PIN" in res:
            test.log.step('Step 1b: PIN is NOT enter, enter PIN')
            # test.dut.dstl_enter_pin()
            test.expect(test.dut.dstl_enter_pin())
        test.log.step('Step 2: lock SIM PIN ')
        test.dut.at1.send_and_verify("at+clck=\"SC\",2", "OK")
        res = test.dut.at1.last_response
        if "CLCK: 0" in res:
            # SIM lock was disabled, activate SIM PIN
            test.expect(test.dut.dstl_lock_sim())
        else:
            # SIM LOCK is active
            test.log.info("bla")

        test.own_restart(SIMPIN=True)

        test.log.step("Step 3: enter wrong pin one time")
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.dut.at1.send_and_verify("at+cpin=\"8578\"", "incorrect password")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+clck=\"SC\",2", "+CLCK: 1"))

        test.log.step('Step 4: unlock SIM PIN and restart')
        test.dut.dstl_unlock_sim()
        test.own_restart(SIMPIN=False)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "READY"))

        test.log.step('Step 5: lock SIM PIN and restart')
        test.dut.dstl_lock_sim()
        test.own_restart(SIMPIN=True)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "+CPIN: SIM PIN"))

        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)

        test.log.step("Step 6: change PIN via GSM command atd**04")
        if (re.search(test.dut.project, 'DAHLIA|COUGAR|KOALA')):
            test.expect(test.dut.at1.send_and_verify("at+cpwd=\"SC\"," + test.dut.sim.pin1 + "\",\"4567\"", "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify("atd**04*" + test.dut.sim.pin1 + "*4567*4567#;" , "OK"))
        test.own_restart(SIMPIN=True)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.dut.at1.send_and_verify("at+cpin?", "+CPIN: SIM PIN")
        test.sleep(5) # is needed because some projcets need time between sim-pin commands
        test.expect(test.dut.at1.send_and_verify("at+cpin=\"4567\"", "OK"))
        test.sleep(5)
        test.dut.at1.send_and_verify("at+cpwd=\"SC\",\"4567\",\"" + test.dut.sim.pin1 + "\"", "OK")
        test.own_restart(SIMPIN=True)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "+CPIN: SIM PIN"))

        test.log.step("Step 7: enter wrong PIN 3 times")
        test.dut.at1.send_and_verify("at+cpin=\"0001\"", "incorrect password")
        test.dut.at1.send_and_verify("at+cpin=\"0020\"", "incorrect password")
        if (re.search(test.dut.project, 'ROM|KINGSTON|FLORENCE|DEIMOS')):
            test.dut.at1.send_and_verify("at+cpin=\"0020\"", "incorrect password")
        else:
            test.dut.at1.send_and_verify("at+cpin=\"0300\"", "SIM PUK required")

        test.expect(test.dut.at1.send_and_verify("at+cpin?", "+CPIN: SIM PUK"))

        test.dut.at1.send_and_verify("at+cpin=\"" + test.dut.sim.puk1 + "\",\"" + test.dut.sim.pin1 + "\"", "OK")
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "READY"))

    def cleanup(test):
        """Cleanup method.
		Nothing to do in this Testcase
        Steps to be executed after test run steps.
        """
        test.own_restart(SIMPIN=True)
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "+CPIN: SIM PIN"))

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
