# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-218

import unicorn
import re
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *

import json
import datetime

testkey = "UNISIM01-218"

class Test(BaseTest):
    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        test.dut.dstl_restart()
        test.sleep(10)


    def run(test):

        test.log.step('Step 1: Check all available profiles - Start')
        _, profiles = test.dut.dstl_get_profile_info()
        log_body(profiles)
        if len(profiles) <= 1:
            test.log.info(
                "Only one profile found - no operational profile could be found, other test steps are not executed !!!")
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - more than one profile found', False)
        else:
            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than one profile found', True)

            test.log.step('Step 2: Check state of bootstrap profile (=0) and operational profile (=1) - Start')
            bootstrap_profile = profiles[0]
            operational_profile = [profile for profile in profiles if profile['profile_state'] == '1'][0]
            result = (bootstrap_profile['profile_state'] == '0') and (operational_profile['profile_state'] == '1')

            test.dut.dstl_collect_result(
                'Step 2: Check state of bootstrap profile (=0) and operational profile (=1)', result)

            test.log.step('Step 3: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 3: Initialise all settings for MODS',
                                         test.dut.dstl_init_all_mods_settings())


            test.log.step('Step 4: Check network registration - Start')
            test.dut.dstl_collect_result('Step 4: Check network registration',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 5: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 5: Check registering on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.log.com('*** activate hidden susmc commands +++ secrect command !!! ***')
            test.dut.dstl_activate_cm_hidden_commands()

            test.log.com('*** set susmc parameters ***')
            fallback_timeout = 120
            test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=fallback_timeout)

            test.log.com('*** Force network registration to unavailable network ***')
            test.dut.at1.send_and_verify('at+cops=1,2,26295', expect='CME ERROR', timeout=150)

            test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*SSIM READY.*', timeout=(fallback_timeout + 60))

            test.log.step('Step 6: Check if bootstrap profile is activated - Start')
            # Expect boostrap profile is activated
            _, profiles = test.dut.dstl_get_profile_info()
            bootstrap_profile = profiles[0]
            result = (bootstrap_profile['profile_state'] == '1')
            test.dut.dstl_collect_result(
                'Step 6: Check state of bootstrap profile (=1)', result)

            test.log.step('Step 7: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS - Start')
            test.dut.dstl_collect_result('Step 7: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS (=JTM2M)',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"))

            test.log.step('Step 8: Check downloadmode 3 - Start')
            test.dut.dstl_collect_result('Step 8: Check downloadmode 3',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))

            test.dut.at1.send_and_verify('at+cops=0,,,7', expect='OK', timeout=150)
            test.log.step('Step 9: Check network registration after fallback - Start')
            test.dut.dstl_collect_result('Step 9: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 10: Check ping google - Start')
            test.dut.dstl_collect_result('Step 10: Check ping google',
                                         test.dut.dstl_check_google_ping())

            test.log.step('Step 11: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 11: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="JTM2M"))


    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
