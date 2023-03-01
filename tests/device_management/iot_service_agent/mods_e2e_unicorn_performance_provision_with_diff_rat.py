# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# test case:
# Debug version:SERVAL_300_032_UNICORN9B & MODS_Staging_V3.1.0_432

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
        setup_for_provision_or_swich(test)
        test.log.step('[Setup]-End.Fallback to bootstrap enabled')
        fallback_to_bootstrap_enalbed(test, step='[Setup]-End')
        return

    def run(test):
        test.log.info('*' * 80)
        test.log.step(f'Connectivity provision with RAT={test.rat}.')
        test.log.info('*' * 80)
        test.connectivity_provision_with_different_rat()
        return

    def connectivity_provision_with_different_rat(test):
        
        for i in range(1, 51):
            test.log.info('*' * 80)
            test.log.step(f'*** Loop {i}/100')
            test.dut.at1.send_and_verify('at^sctm?', 'OK')
            test.log.info('*' * 80)
            test.log.step(f"[i={i}] 1. Configure module before connectivity provision.")
            test.expect(connectivity_provision_module_configure(test, step=1))
            test.log.step(f"[i={i}] 2. Register to network, rat={test.rat}")
            test.expect(register_network(test))
            test.log.step(f"[i={i}] 3. Record time consumption during connectivity provision")
            test.expect(record_time_consumption(test,test.time_consumption_dict,i))
            test.expect(record_iccid(test,test.iccids,i))
            test.log.step(f"[i={i}] 4. Fall back to bootstrap enabled and repeat step 1-3")
            test.expect(fallback_to_bootstrap_enalbed(test, step=4))
            print_time_consumption_report(test, 'Connectivity_Provision', test.iccids, test.time_consumption_dict)
        return
    
    def cleanup(test):
        print_time_consumption_report(test, 'Connectivity_Provision', test.iccids, test.time_consumption_dict)
        test.log.info('Drop all broken subscriptions and create them again.')
        cleanup_broken_iccids(test)
        return
   







if "__main__" == __name__:
    unicorn.main()
