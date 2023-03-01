# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# test case:cm fallback and local switch performance test.
# Debug version:

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from tests.device_management.iot_service_agent.mods_e2e_unicorn_performance_api import *
from dstl.auxiliary.restart_module import dstl_restart
import json
import datetime


class Test(BaseTest):
    """
    Use Case:
    """
    iccids=['']*100
    time_consumption_dict = {'register device': [0]*100, 'download profile': [0]*100, 'trigger restart': [0]*100,
                             'register network': [0] * 100}
    
    def setup(test):
        test.fallback_test=True
        setup_for_provision_or_swich(test)
        test.log.step('[Setup]-End.Fallback to bootstrap enabled')
        fallback_to_bootstrap_enalbed(test, step='[Setup]-End')
        return

    def run(test):
        test.log.info('*' * 80)
        test.log.step(f'Connectivity provision with RAT={test.rat}.')
        test.log.info('*' * 80)
        test.cm_fallback_and_local_switch_test()
        return

    def cm_fallback_and_local_switch_test(test):
        test.log.step("1. Configure module for provisioning.")
        test.expect(connectivity_provision_module_configure(test, step=1))
        test.log.step("2. Register to network, rat={test.rat}")
        test.expect(register_network(test))
        test.log.step("3. Trigger provisioning to download one operational profile")
        test.expect(record_time_consumption(test, test.time_consumption_dict, 1))
        test.dut.dstl_stop_mods_agent()
        test.log.step("4. Configure module for provisioning.")
        test.fallback_timeout = 60
        test.localswitch_timeout = 60
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout,
                                           cm_fb_local_sw_timer=test.localswitch_timeout)
        for i in range(1, 51):
            test.log.info('*' * 80)
            test.log.step(f'*** Loop {i}/100')
            test.log.step(f"[i={i}] 5.1. Restart module.")
            test.dut.dstl_restart()
            if '^SSIM READY' not in test.dut.at1.last_response:
                test.expect(test.dut.at1.wait_for('\^SSIM READY', timeout=10))
            test.log.step(f"[i={i}] 5.2. Set unavailable RAT.")
            test.dut.at1.send_and_verify('at^sxrat=7,7')
            test.sleep(10)
            test.log.step(f"[i={i}] 5.3. Check cm list and wait for fallback urc.")
            test.dut.dstl_activate_cm_hidden_commands()
            exp_value = f'\^SUSMC: "ConMgr/Fallback/Timeout",{test.fallback_timeout},[1-59]'
            test.expect(re.search(exp_value, test.dut.at1.last_response))
            test.expect(test.dut.at1.wait_for('SUSMA: "ConMgr/Fallback",0,1',timeout=test.fallback_timeout))
            test.expect(test.dut.at1.wait_for('\^SSIM READY', timeout=30))
            test.expect(test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',expect='.*3.*OK.*'))
            exp_value='\^SUSMA: "LPA/Profiles/Info",0,1,"\d+",.*'
            test.expect(test.dut.at1.send_and_verify('at^susma?', expect=exp_value,timeout=30))
            test.log.step(f"[i={i}] 5.4. Check cm list and wait for local switch urc.")
            test.dut.dstl_activate_cm_hidden_commands()
            exp_value = f'\^SUSMC: "ConMgr/Fallback/LocalSwitchTimeout",{test.localswitch_timeout},[1-59]'
            test.expect(re.search(exp_value, test.dut.at1.last_response))
            test.expect(test.dut.at1.wait_for('SUSMA: "ConMgr/Fallback",2,2', timeout=test.localswitch_timeout))
            test.expect(test.dut.at1.wait_for('\^SSIM READY', timeout=30))
            test.expect(test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"', expect='.*3.*OK.*'))
            exp_value = '\^SUSMA: "LPA/Profiles/Info",2,1,"\d+",.*'
            test.expect(test.dut.at1.send_and_verify('at^susma?', expect=exp_value, timeout=30))
            test.dut.dstl_activate_cm_hidden_commands()
            exp_value = '\^SUSMC: "ConMgr/Fallback/RetryTimeout",3600,43200,86400,259200,604800,1814400,2592000,7776000,\d+,[12345678]'
            test.expect(re.search(exp_value,test.dut.at1.last_response))
            test.log.step(f"[i={i}] 5.5. Register netowrk and check.")
            test.expect(register_network(test))
            test.log.com('++++ WORKAROUND_SRV03_4181 - Start *****')
            test.expect(test.dut.at1.wait_for('\^SYSSTART', timeout=120))
            test.log.com('++++ WORKAROUND_SRV03_4181 - Start *****')
            test.expect(test.dut.at1.wait_for('\+CEREG: [15],.*', timeout=60))
            test.expect(test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"', expect='.*2.*OK.*'))
            test.log.info('*' * 80)

        test.log.step("6. Restore")
        test.dut.dstl_activate_cm_settings()
        test.expect(fallback_to_bootstrap_enalbed(test, step=4))
        return
    
    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        return
   







if "__main__" == __name__:
    unicorn.main()
