#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0093350.001

import unicorn
from core.basetest import BaseTest


from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.status_control import extended_indicator_control
from dstl.network_service import network_access_type
from dstl.auxiliary import check_urc

class test(BaseTest):
    '''
    TC0093350.001--TpSindRoam
    Check ^SIND: roam-URC with roaming sim card
    Roaming SIM card need be plugged in 
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        cops_timeout = 100
        roam_urc_timeout = 60
        ok_or_error = "\s+(OK|ERROR)\s+"
        test.log.info("Step 1. Test, read, exec and write command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?", "\^SIND: .*\(roam,\(0\-1\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", "\^SIND: roam,0,0\s+"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND", "ERROR"))

        test.log.info("Step 2. Turn on roaming indicator")
        test.expect(test.dut.dstl_enable_one_indicator("roam", check_result=True))

        test.log.info("Step 3. Enter pin, module should be registered to network and roaming URC appears")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,1\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear, please check if Roam SIM card is used.")

        test.log.info("Step 4. After 15 seconds, module is still on roaming network")
        test.expect(test.dut.at1.send_and_verify("AT^SIND?", "\^SIND: roam,1,1\s+"))

        test.log.info("Step 5. Deregister from network, URC should appear")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error, timeout=cops_timeout))
        test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,0\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear for deregistering from network")

        test.log.info("Step 6. Check roaming URC for each type of network that module supports")
        index = 1
        network_types = test.dut.dstl_supported_network_types()
        type_rat_map = {'GSM': '0', 'UMTS': 2, 'LTE': '7'}
        for network_type, is_supported in network_types.items():
            if is_supported == True and network_type in ('GSM', 'UMTS', 'LTE'):
                test.dut.dstl_set_network_single_mode(network_type)
                index +=1
                test.log.info(f"Step 6.{index}. Check roaming URC for network: {network_type}")
                test.expect(test.dut.at1.send_and_verify(f"AT+COPS=0,,,{type_rat_map[network_type]}", "OK", wait_for=ok_or_error, timeout=cops_timeout))
                test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,1\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear when registering to {network_type} network")
                test.monitor_network_status()
                test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error, timeout=cops_timeout))
                test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,0\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear when deregistering from {network_type} network")

                test.log.info(f"Step 6.{index}. Restart module, checking roaming urc")
                test.expect(test.dut.dstl_restart())
                test.expect(test.dut.dstl_enable_one_indicator("roam", check_result=True))
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,1\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear after restarting for {network_type} network")
                test.monitor_network_status()
                test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error, timeout=cops_timeout))
                test.expect(test.dut.dstl_check_urc("\s+\+CIEV: roam,0\s+", timeout=roam_urc_timeout), msg="Roaming URC did not appear when deregistering network")


        test.log.info("Step 7. Turn off roaming indicator")
        test.dut.dstl_set_network_max_modes()
        test.expect(test.dut.dstl_disable_one_indicator("roam", check_result=True))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", wait_for=ok_or_error, timeout=cops_timeout))
        test.expect(not test.dut.dstl_check_urc("\s+\+CIEV: roam.*", timeout=roam_urc_timeout), msg="Roaming URC should not appear when indicator is turned off.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", wait_for=ok_or_error, timeout=cops_timeout))
        test.expect(not test.dut.dstl_check_urc("\s+\+CIEV: roam.*", timeout=roam_urc_timeout), msg="Roaming URC should not appear when indicator is turned off.")

    def cleanup(test):
        pass

    def monitor_network_status(test):
        test.dut.at1.send_and_verify("AT+COPS?")
        test.dut.at1.send_and_verify("AT^SMONI?")
        test.dut.at1.send_and_verify("AT^MONI?")

if __name__=='__main__':
    unicorn.main()
