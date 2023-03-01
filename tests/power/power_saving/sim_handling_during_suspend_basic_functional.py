#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104377.001 - SIMHandlingDuringSuspendModeFunctional

import unicorn
import random
import re


from core.basetest import BaseTest

from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.configuration.suspend_mode_operation import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control
from dstl.network_service.register_to_network import dstl_enter_pin


PSM_URC= "^SYSRESUME"

class sim_handling_during_suspend_basic_functional(BaseTest):



    def setup(test):
        test.dut.detect()
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate module and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*(OK|ERROR).*",timeout=30))
        test.disable_uart_powersaving()
        test.dut.dstl_disable_suspend_mode(1)
        test.dut.dstl_disable_psm()
        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()
        test.dut.dstl_restart()
        #test.dut.dstl_register_to_lte()
        test.dut.dstl_register_to_network()
        test.expect(test.dut.dstl_set_sim_suspend_mode(0))


    def run(test):

        test.log.step("RunTest_1: Check deafult SIM/Suspend value")
        test.expect(test.dut.dstl_verify_sim_suspend_mode(0))

        test.log.step("RunTest_2: Check if module can enable SUSPEND mode with a SIM PIN Unlocked Card")
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        # test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout=100 + test.dut.dstl_get_actual_active_time()))
        # test.expect(not test.dut.dstl_check_if_module_is_on_via_dev_board())
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.step("RunTest_3: Wakeup module from Suspend mode via ON PIN, Change SIM/Suspend to 2 and restart module")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.wakeup_module_via_rts()
        test.expect(test.dut.dstl_set_sim_suspend_mode(2))
        test.dut.dstl_restart()

        test.log.step("RunTest_4: Check if module can enable SUSPEND mode with a SIM PIN Unlocked Card")
        test.wakeup_module_via_rts()
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout=100 + test.dut.dstl_get_actual_active_time()))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.step("RunTest_5: Wakeup module from Suspend mode via ON PIN, set the SIM card with PIN locked")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()


        test.log.info("RunTest_6: Input PIN code,  Check if module can enable SUSPEND mode with a SIM PIN locked Card")
        dstl_enter_pin(test.dut)
        test.dut.dstl_register_to_network()
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout=100 + test.dut.dstl_get_actual_active_time()))
        # test.expect(not test.dut.dstl_check_if_module_is_on_via_dev_board())
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("RunTest_7: Wakeup module from Suspend mode via ON PIN, Change SIM/Suspend to 2 and restart module")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.wakeup_module_via_rts()
        test.expect(test.dut.dstl_set_sim_suspend_mode(0))
        test.dut.dstl_restart()

        test.log.info("RunTest_8:  Input PIN code,  Check if module can enable SUSPEND mode with a SIM PIN locked Card")
        test.disable_uart_powersaving()
        dstl_enter_pin(test.dut)
        test.dut.dstl_register_to_network()
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.enable_uart_powersaving()
        test.sleep(60 + test.dut.dstl_get_actual_active_time())
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.log.info("RunTest_9:  Press power on button to Wake up module, and try to set AT^SCFG=SIM/Suspend to other unsupported value")
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()
        invalidvalues= [3,1,-1,'A','B']
        for invalidvalue in invalidvalues:
            test.dut.at1.send_and_verify(r'AT^SCFG="SIM/Suspend","{}"'.format(invalidvalue), "ERROR", timeout=30)


    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Disable UART power saving")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()
        if (test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2)) == False:
            test.dut.dstl_reset_with_vbatt_via_dev_board()
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Disable Suspend mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_suspend_mode()

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_3: Restore SIM Suspend mode to 0")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_set_sim_suspend_mode(0))

    def enable_uart_powersaving(test, pwrsave_period=0, pwrsave_wakeup=50):
        test.dut.at1.send_and_verify(
            'AT^SCFG="MEopMode/PwrSave","enabled",{},{}'.format(pwrsave_period, pwrsave_wakeup), "OK", timeout=10)

    def disable_uart_powersaving(test):
        test.wakeup_module_via_rts()
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","disabled"', "OK", timeout=10)

    def wakeup_module_via_rts(test):
        test.dut.at1.connection.setRTS(False)
        test.sleep(0.1)
        test.dut.at1.connection.setRTS(True)

if (__name__ == "__main__"):
    unicorn.main()
