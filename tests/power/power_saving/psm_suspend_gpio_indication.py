#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104318.001- PSM_Suspend_GPIO_Indication

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
from dstl.configuration import suspend_mode_operation
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.status_control import extended_indicator_control


PSM_URC= "^SYSRESUME"

class PSM_Suspend_GPIO_Indication(BaseTest):

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
        test.log.info("*******************************************************************")
        test.log.info("SetUp_3: Disable UART power saving mode and register to network")
        test.log.info("*******************************************************************")
        test.disable_uart_powersaving()
        test.dut.dstl_register_to_lte()


    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Check deafult SUSPEND mode indication status")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_verify_suspend_gpio_indication_status(expectedstatus="off"))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Enable SUSPEND mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")

        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout = 2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.at1.read(append = True)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving(0, 50)
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout = 100 + test.dut.dstl_get_actual_active_time()))
        # test.expect(not test.dut.dstl_check_if_module_is_on_via_dev_board())
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5:Read the GPIO 11 status via MC test, the status should be LOW")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:MODULE=EHS5", r'.*MC:   Module family: EHS5.*', 'MC:   OK', timeout = 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIOcfg=1.8V", r'.*MC:   Module family: EHS5.*', 'MC:   OK',
                                                      timeout=2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO10", r'.*MC:   GPIO10: IN, 0.*', 'MC:   OK',
                                                      timeout=2, ))
        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Wakeup module from Suspend mode via ON PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_turn_on_igt_via_dev_board()
        #dstl_turn_on_igt_via_dev_board(test.dut)
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Read the GPIO 11 status via MC test, the status should be Low")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:MODULE=EHS5", r'.*MC:   Module family: EHS5.*', 'MC:   OK', timeout = 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIOcfg=1.8V", r'.*MC:   Module family: EHS5.*', 'MC:   OK',
                                                      timeout= 2, ))
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO10", r'.*MC:   GPIO10: IN, 0.*', 'MC:   OK',
                                                      timeout= 2, ))
        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Change SUSPEND mode indication status to std")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.dut.dstl_set_suspend_gpio_indication_status("std")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_9: Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_10: Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout = 60 + test.dut.dstl_get_actual_active_time()))
        # test.expect(not test.dut.dstl_check_if_module_is_on_via_dev_board())
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout = 2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_11:Read the GPIO 11 status via MC test, the status should be LOW")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO10", r'.*MC:   GPIO10: IN, 0.*', 'MC:   OK',
                                                      timeout=2, ))
        test.log.info("*******************************************************************")
        test.log.info("RunTest_12: Wakeup module from Suspend mode via ON PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_turn_on_igt_via_dev_board()
        #dstl_turn_on_igt_via_dev_board(test.dut)
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout = 2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_13: Read the GPIO 11 status via MC test, the status should be High")
        test.log.info("*******************************************************************")
        test.expect(test.dut.devboard.send_and_verify(r"MC:GPIO10", r'.*MC:   GPIO10: IN, 1.*', 'MC:   OK',
                                                      timeout = 2, ))


    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Disable UART power saving mode")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Set suspend gpio indication to OFF")
        test.log.info("*******************************************************************")
        test.dut.dstl_set_suspend_gpio_indication_status("off")
        test.expect(test.dut.dstl_verify_suspend_gpio_indication_status(expectedstatus = "off"))

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_3: Disable suspend mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_suspend_mode()

if (__name__ == "__main__"):
    unicorn.main()
