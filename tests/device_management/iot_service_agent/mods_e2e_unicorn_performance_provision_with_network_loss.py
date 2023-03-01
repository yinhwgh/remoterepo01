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
from dstl.auxiliary.write_json_result_file import *

import json
import datetime

testkey = "UNISIM01-257"

class Test(BaseTest):
    """
    Use Case:
    """

    #stage_index: too indicate loss network in which stage.
    # 0--network loss during register device.
    # 1--network loss during download prfole.
    # 2--network loss during trigger restart.
    # 3--one loop is finished
    stage_index=0#init value 0
    time_to_sleep=3#init value 3
    def setup(test):
        setup_for_provision_or_swich(test)
        test.log.step('[Setup]-End.Fallback to bootstrap enabled')
        fallback_to_bootstrap_enalbed(test, step='[Setup]-End')
        return
    
    def run(test):
        test.log.info('*' * 80)
        test.log.step(f'Network loss test during connectivity provision.')
        test.log.info('*' * 80)
        test.connectivity_provision_with_different_rat()
        return
    
    def connectivity_provision_with_different_rat(test):
        i = 1
        while True:
            test.log.info('*' * 80)
            test.log.step(f'*** i={i}')
            test.log.step("Step 1. Configure module before connectivity provision.")
            test.expect(connectivity_provision_module_configure(test, step=1))
            test.log.step(f"Step 2. Register to network, rat={test.rat}")
            test.expect(register_network(test))
            test.log.step(f"Step 3. Network loss during connectivity provision and continue.")
            test.expect(abnormal_condition_during_connectivity_activation(test, step=3, condition='network_loss'))
            test.log.step("Step 4.Fallback to bootstrap enabled and repeat step 1-3")
            test.expect(fallback_to_bootstrap_enalbed(test, step=4))
            i += 1
            if test.stage_index == 3:
                return
            test.log.com('++++ WORKAROUND for sim busy issue during network loss test. - Start *****')
            test.dut.dstl_restart()
            test.dut.at1.wait_for('\+CIEV: prov,0,"fallb3gpp"', timeout=10)
            test.log.com('++++ WORKAROUND for sim busy issue during network loss test. - End *****')


    
    def cleanup(test):
        test.log.info('Drop all broken subscriptions and create them again.')
        cleanup_broken_iccids(test)
        return


if "__main__" == __name__:
    unicorn.main()
