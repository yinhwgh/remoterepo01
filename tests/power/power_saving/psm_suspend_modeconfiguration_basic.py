#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104396.001 - PSM_Suspend_Mode_Configuration_Basic

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.configuration.suspend_mode_operation import *
from dstl.status_control.extended_indicator_control import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *

PSM_URC = "^SYSRESUME"


class PSM_Suspend_ModeConfiguration_Basic(BaseTest):


    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate module and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=30))
        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()
        test.disable_uart_powersaving()
        test.dut.at1.send_and_verify("AT+COPS=2", "OK")
        test.dut.dstl_register_to_lte()


    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Check defaut value of SUSPEND mode should be disabled!")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"', '\^SCFG: "MEopMode/PowerMgmt/Suspend","0"[\s\S].*OK',timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Enable SUSPEND mode with volatility 1")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')
        test.dut.dstl_enable_suspend_mode()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau()== 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout= 200 + test.dut.dstl_get_actual_active_time()))
        test.sleep(5)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Wakeup module from Suspend mode via ON PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 30))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.disable_uart_powersaving()
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Check current Suspend mode ")
        test.log.info("*******************************************************************")

        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","1","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Enable AT+CPSMS again")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0) or (test.dut.dstl_get_actual_periodic_tau() > 900):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Wait after module enters to SUSPEND mode again")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.expect(test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout = 200+ test.dut.dstl_get_actual_active_time()))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1','MC:   OK',timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_9: Wait module TAU and check the URC")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10 + test.dut.dstl_get_actual_periodic_tau() - test.dut.dstl_get_actual_active_time()))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.sleep(2)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_10: Check current Suspend mode ")
        test.log.info("*******************************************************************")
        test.disable_uart_powersaving()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","1","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_11: Enable SUSPEND mode with volatility 0")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')
        test.dut.dstl_enable_suspend_mode(volatility=0)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_12: Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0) or (test.dut.dstl_get_actual_periodic_tau() > 900):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_13: Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout= 200 + test.dut.dstl_get_actual_periodic_tau()))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_14: Wakeup module from Suspend mode via ON PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.disable_uart_powersaving()
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')

        test.log.info("*******************************************************************")
        test.log.info("RunTest_15: Check current Suspend mode ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","0","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_16: Enable SUSPEND mode with volatility 0")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')
        test.dut.dstl_enable_suspend_mode(volatility=0)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_17: Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(2)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0) or (test.dut.dstl_get_actual_periodic_tau() > 900):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(2)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("RunTest_18: Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout=200 + test.dut.dstl_get_actual_active_time()))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_19: Wait module TAU and check the URC")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout= 20 + test.dut.dstl_get_actual_periodic_tau() -test.dut.dstl_get_actual_active_time()))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2))
        test.sleep(2)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_20: Check current Suspend mode ")
        test.log.info("*******************************************************************")
        test.disable_uart_powersaving()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","0","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_21: Enable SUSPEND mode with volatility 0")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')
        test.dut.dstl_enable_suspend_mode(volatility = 0)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_22: Restart module and check current Suspend mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","0","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_23: Disable SUSPEND mode with volatility 0")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator('suspendAvailable')
        test.dut.dstl_enable_one_indicator('suspendReady')
        test.dut.dstl_disable_suspend_mode(volatility = 0)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_24: Restart module and check current Suspend mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","0","1"[\s\S].*OK', timeout=30))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_25: Configurate Suspend mode with invalid values")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend",2',
                                                 '.*ERROR.*', timeout=30))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","1","2"',
                                                 '.*ERROR.*', timeout=30))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","-1"',
                                                 '.*ERROR.*', timeout=30))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","1","-1"',
                                                 '.*ERROR.*', timeout=30))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","a","1"',
                                                 '.*ERROR.*', timeout=30))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","1","a"',
                                                 '.*ERROR.*', timeout=30))

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Disable UART power saving mode")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.disable_uart_powersaving()

        test.log.info("*******************************************************************")
        test.log.info("CleanUp_2: Disable Suspend mode ")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.send_and_verify(r'AT^SCFG="MEopMode/PowerMgmt/Suspend","0"',
                                                 '\^SCFG: "MEopMode/PowerMgmt/Suspend","0"[\s\S].*OK', timeout=30))


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
