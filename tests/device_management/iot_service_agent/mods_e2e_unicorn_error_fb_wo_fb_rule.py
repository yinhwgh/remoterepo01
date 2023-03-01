# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-220 - Error Case: Fallback without announced fallback rule

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

testkey = "UNISIM01-220"

class Test(BaseTest):
    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(10)


    def run(test):

        test.log.step('Step 1: Check all available profiles - Start')
        _, profiles = test.dut.dstl_get_profile_info()
        log_body(profiles)
        if len(profiles) <= 1:
            test.log.info(
                "Only bootstrap profile is shown - no operational profile could be found, other test steps are not executed !!!")
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - more than one profile found', False)
        else:
            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than one profile found', True)

        time_before_test = test.dut.dstl_get_mods_time(format=True)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

        test.log.step('Step 2: Check if fallback rule is assgined - Start')
        fb_rule_available, fb_rule = test.dut.dstl_check_fallback_provisioning_rule_is_assigned(device_id, "UNICORN-POC")
        if fb_rule_available:
            test.log.info("Following fallback rule is assigned, but should not - device will be deleted and created again :" + fb_rule)
            test.log.step('Step 2.1: Delete device on MODS server - Start')
            test.dut.dstl_collect_result('Step 2.1: Delete device on MODS server', test.dut.dstl_delete_device(device_id))
            test.log.step('Step 2.2: Create device on MODS - Start')
            result, device_id = test.dut.dstl_create_device_on_mods(imei)
            test.dut.dstl_collect_result('Step 2.2: Create device on MODS', result)
        else:
            test.dut.dstl_collect_result('Step 2: Check if fallback rule is assgined (should not)', True)

        test.log.step('Step 3: Check state of bootstrap profile (=0) and operational profile (=1) - Start')
        bootstrap_profile = profiles[0]
        operational_profile = [profile for profile in profiles if profile['profile_state'] == '1'][0]
        result = (bootstrap_profile['profile_state'] == '0') and (operational_profile['profile_state'] == '1')

        test.dut.dstl_collect_result(
                'Step 2: Check state of bootstrap profile (=0) and operational profile (=1)', result)

        test.log.step('Step 4: Initialise all settings for MODS - Start')
        test.dut.dstl_collect_result('Step 4: Initialise all settings for MODS',
                                        test.dut.dstl_init_all_mods_settings())

        test.log.step('Step 5: Check network registration - Start')
        test.dut.dstl_collect_result('Step 4: Check network registration',
                                        test.dut.dstl_check_network_registration())

        test.log.step('Step 6: Check registering on MODS - Start')
        test.dut.dstl_collect_result('Step 5: Check registering on MODS',
                                        test.dut.dstl_check_registering_on_mods())

        test.log.com('*** activate hidden susmc commands +++ secrect command !!! ***')
        test.dut.dstl_activate_cm_hidden_commands()

        test.log.com('*** set susmc parameters ***')
        fallback_timeout = 120
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=fallback_timeout)

        test.log.com('*** Force network registration to an unavailable network ***')
        test.dut.at1.send_and_verify('at+cops=1,2,26295,7', expect='CME ERROR', timeout=150)

        test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*SSIM READY.*', timeout=(fallback_timeout + 60))

        test.sleep(5)

        test.log.step('Step 7: Check if bootstrap profile is activated - Start')
        # Expect boostrap profile is activated
        _, profiles = test.dut.dstl_get_profile_info()
        bootstrap_profile = profiles[0]
        result = (bootstrap_profile['profile_state'] == '1')
        test.dut.dstl_collect_result(
                'Step 7: Check state of bootstrap profile (=1)', result)

        test.log.step('Step 8: Check if downloadmode is set to 3 - Start')
        test.dut.dstl_collect_result('Step 8: Check downloadmode 3',
                                        test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))

        rat = test.dut.dstl_get_rat()
        test.dut.at1.send_and_verify(f'at+cops=0,,,{rat}', expect='OK', timeout=180)
        test.dut.at1.verify_or_wait_for('.*^SYSSTART.*SUSMA: "ConMgr/Profile",0.*', timeout=120)

        test.log.step('Step 9: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS call - Start')
        test.dut.dstl_collect_result('Step 9: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS call (=JTM2M)',
                                        test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"))

        test.log.step('Step 10: Check if fallbackConnectivityProvision job has failed (Provisioning rule not assigned) - Start')
        test.dut.dstl_collect_result('Step 10: Check if fallbackConnectivityProvision job has failed (Provisioning rule not assigned)',
                                        test.dut.dstl_check_job_fallback_conn_provision_wo_rule(imei, time_before_test))



    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=1, apn="internet")
        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_set_download_mode_wo_agent(download_mode=2)
        test.dut.dstl_start_mods_agent()
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
