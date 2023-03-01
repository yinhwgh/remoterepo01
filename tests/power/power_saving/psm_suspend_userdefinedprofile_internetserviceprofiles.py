#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0104874.001 - PSM_Suspend_UserDefinedProfile_InternetServiceProfiles

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

class psm_suspend_userdefinedprofile_internetserviceprofiles(BaseTest):

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
        test.log.info("1. Restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*(OK|ERROR).*",timeout=30))
        test.log.info("*******************************************************************")
        test.log.info("2. Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()
        test.disable_uart_powersaving()
        test.dut.dstl_register_to_lte()

    def run(test):
        test.log.info("*******************************************************************")
        test.log.info("1. Change some settings to non-default value and IP service profile")
        test.log.info("*******************************************************************")

        test.dut.at1.send_and_verify(r'AT^SISS=0,"srvType","Socket"', r'.*OK.*')
        test.dut.at1.send_and_verify(r'AT^SISS=0,"conId","1"', r'.*OK.*')
        test.dut.at1.send_and_verify(r'AT^SISS=0,"address","socktcp://10.163.101.3:2000;etx" ', r'.*OK.*')
        test.dut.at1.send_and_verify(r'AT^SISS?',
                                     r'.*SISS: 0,"srvType","Socket"[\S\s]*SISS: 0,"conId","1"[\S\s]*SISS: 0,"address","socktcp://10.163.101.3:2000;etx"[\s\S]*OK.*')

        test.expect(test.dut.at1.send_and_verify(r'AT&C0', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&D0', r'.*OK.*'))
        test.sleep(2)

        test.expect(test.dut.at1.send_and_verify(r'AT&S1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CGREG=1', r'.*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMGF=1', r'.*OK.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI', r'.*OK.*')) ;Not support yet
        #test.expect(test.dut.at1.send_and_verify(r'AT+COPS=2', r'.*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CREG=2', r'.*OK.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS="UCS2"', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSDH=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSMP=17,168,1,1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSMS=1', r'.*OK.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CGSMS=3', r'.*OK.*')) Restore to NV, and not be restore by AT&F
        # test.expect(test.dut.at1.send_and_verify(r'AT+CSSN', r'.*OK.*')) ; releated to call, Serval doesn't support it
        test.expect(test.dut.at1.send_and_verify(r'AT+CTZU=1', r'.*OK.*'))


        test.expect(test.dut.at1.send_and_verify(r'ATX1', r'.*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT^SCKS=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCTM=1', r'.*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT^SSET=1', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SLED=1', r'.*OK.*'))

        test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         '.*X1[\s\S]*\&C0[\s\S]*\&D0[\s\S]*\&S1[\s\S]*CMGF: 1[\s\S]*CSDH: 1[\s\S]*CMEE: 1[\s\S]*CSMS: 1[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))

        test.log.info(test.dut.at1.last_response)

        test.expect(test.dut.at1.send_and_verify(r'AT+CREG?', r'.*\+CREG: 2.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI?', r'.*OK.*'));Not support yet
        #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS?', r'.*\+CSCS: "UCS2".*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', r'.*\+CMEE: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCKS?', r'.*\^SCKS: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SLED?', '.*\^SLED: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSDH?', '.*\+CSDH: 1'))
        test.dut.at1.send_and_verify('AT&W','.*OK.*')

        test.log.info("*******************************************************************")
        test.log.info("2. Enable SUSPEND mode")
        test.log.info("*******************************************************************")
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")
        test.dut.dstl_enable_suspend_mode(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("3. Enable AT+CPSMS")
        test.log.info("*******************************************************************")
        test.enable_uart_powersaving()
        test.dut.dstl_disable_psm()
        test.dut.dstl_enable_psm()
        test.sleep(1)
        test.dut.dstl_psm_timer_parser()
        while (test.dut.dstl_get_actual_periodic_tau() == 0):
            test.dut.dstl_disable_psm()
            test.dut.dstl_enable_psm()
            test.sleep(1)
            test.dut.dstl_psm_timer_parser()

        test.log.info("*******************************************************************")
        test.log.info("4.Wait after module enters to SUSPEND mode")
        test.log.info("*******************************************************************")

        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout= 100 + test.dut.dstl_get_actual_active_time()))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("5. Wakeup module from Suspend mode via ON PIN")
        test.log.info("*******************************************************************")
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC), timeout=10))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("6. Check if the pre-set values are keep")
        test.log.info("*******************************************************************")
        test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         '.*X1[\s\S]*\&C0[\s\S]*\&D0[\s\S]*\&S1[\s\S]*CMGF: 1[\s\S]*CSDH: 1[\s\S]*CMEE: 1[\s\S]*CSMS: 1[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CREG?', r'.*\+CREG: 2.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI?', r'.*OK.*'));Not support yet
        #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS?', r'.*\+CSCS: "UCS2".*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', r'.*\+CMEE: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCKS?', r'.*\^SCKS: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SLED?', '.*\^SLED: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSDH?', '.*\+CSDH: 1'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS="GSM"', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SISS?',
                                     r'.*SISS: 0,"srvType","Socket"[\S\s]*SISS: 0,"conId","1"[\S\s]*SISS: 0,"address","socktcp://10.163.101.3:2000;etx"[\s\S]*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS="UCS2"', r'.*OK.*'))
        test.dut.dstl_enable_one_indicator("suspendavailable")
        test.dut.dstl_enable_one_indicator("suspendready")

        test.log.info("*******************************************************************")
        test.log.info("7. Enable AT+CPSMS again")
        test.log.info("*******************************************************************")
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
        test.log.info("8.Wait after module enters to SUSPEND mode again")
        test.log.info("*******************************************************************")
        test.expect(
            test.dut.at1.wait_for(r"{}".format("suspendReady,1"), timeout=100 + test.dut.dstl_get_actual_active_time()))
        test.sleep(1)
        # test.expect(not test.dut.dstl_check_if_module_is_on_via_dev_board())
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 1', 'MC:   OK', timeout=2))

        test.log.info("*******************************************************************")
        test.log.info("9. Wait module TAU and check the URC")
        test.log.info("*******************************************************************")
        test.expect(test.dut.at1.wait_for(r"{}".format(PSM_URC),
                                          timeout=10+test.dut.dstl_get_actual_periodic_tau() - test.dut.dstl_get_actual_active_time()))
        test.expect(test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0', 'MC:   OK', timeout=2))
        test.sleep(2)

        test.log.info("*******************************************************************")
        test.log.info("10. Check if the pre-set values are keep")
        test.log.info("*******************************************************************")
        test.wakeup_module_via_rts()
        test.expect(
            test.dut.at1.send_and_verify(r'AT&V',
                                         '.*X1[\s\S]*\&C0[\s\S]*\&D0[\s\S]*\&S1[\s\S]*CMGF: 1[\s\S]*CSDH: 1[\s\S]*CMEE: 1[\s\S]*CSMS: 1[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CREG?', r'.*\+CREG: 2.*'))
        #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI?', r'.*OK.*'));Not support yet
        #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS?', r'.*\+CSCS: "UCS2".*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CMEE?', r'.*\+CMEE: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SCKS?', r'.*\^SCKS: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SLED?', '.*\^SLED: 1.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT+CSDH?', '.*\+CSDH: 1'))

        test.expect(test.dut.at1.send_and_verify(r'AT+CSCS="GSM"', r'.*OK.*'))
        test.expect(test.dut.at1.send_and_verify(r'AT^SISS?',
                                     r'.*SISS: 0,"srvType","Socket"[\S\s]*SISS: 0,"conId","1"[\S\s]*SISS: 0,"address","socktcp://10.163.101.3:2000;etx"[\s\S]*OK.*'))

    def cleanup(test):
        test.log.info("Disable Suspend mode ")
        if (test.dut.devboard.send_and_verify(r"MC:PWRIND", r'.*MC:   PWRIND: 0','MC:   OK',timeout=2)) == False:
            test.dut.dstl_reset_with_vbatt_via_dev_board()
        test.wakeup_module_via_rts()
        test.dut.dstl_disable_suspend_mode()
        test.disable_uart_powersaving()
        test.dut.at1.send_and_verify('AT&F', '.*OK.*')
        test.dut.at1.send_and_verify('AT&W', '.*OK.*')


if (__name__ == "__main__"):
    unicorn.main()
