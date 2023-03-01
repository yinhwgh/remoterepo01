# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-222 - Error Case: Fallback with unkown fallback rule
# pre-condition: 1 SIMINN operational profile has to be installed before

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

testkey = "UNISIM01-222"

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

            # Get the current time - 1 hour to find the job
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
                'Step 3: Check state of bootstrap profile (=0) and operational profile (=1)', result)

            test.log.step('Step 4: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 4: Initialise all settings for MODS',
                                         test.dut.dstl_init_all_mods_settings())


            test.log.step('Step 5: Check network registration - Start')
            test.dut.dstl_collect_result('Step 5: Check network registration',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 6: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 6: Check registering on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.log.com('*** activate hidden susmc commands +++ secrect command !!! ***')
            test.dut.dstl_activate_cm_hidden_commands()

            test.log.com('*** set susmc parameters ***')
            test.fallback_timeout = 120
            test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout)

            test.log.com('*** Force network registration to unavailable network ***')
            test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=150)

            #test.dut.at1.wait_for_strict('.*CEREG: 4.*', timeout=150)

            wait_count = 1
            max_count = int(test.fallback_timeout / 30) + 2
            leave_loop = False
            current_timeout = test.dut.dstl_get_current_fb_timer_value()
            test.log.com('current_timeout: ' + str(current_timeout))
            result_urc_check = False
            result_check_change_current_fb_timer = False

            while ((current_timeout == 0) or (current_timeout >= 35)) and (wait_count < max_count) and (leave_loop == False):
                dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))
                current_timeout = test.dut.dstl_get_current_fb_timer_value()
                if (current_timeout < test.fallback_timeout) and (current_timeout != 0) and (current_timeout != -1):
                    result_check_change_current_fb_timer = True
                    test.log.com('"result_check_change_current_fb_timer" is set to True, because value <currentFbTimerValue> is running: ' + str(current_timeout))
                test.log.com('current_timeout: ' + str(current_timeout))
                test.sleep(30)
                read_data = test.dut.at1.read()
                test.log.com('last response of loop ' + str(wait_count) + ': ' + read_data)
                if 'SUSMA: "ConMgr/Fallback",0' in read_data:
                    leave_loop = True
                    result_urc_check = True
                    test.log.com('leave loop, because of ^SUSMA: "ConMgr/Fallback",0')

                wait_count = wait_count + 1

            #test.expect(test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",2', timeout=(fallback_timeout + 60)))
            if leave_loop != True:
                result_urc_check = test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Fallback",0', timeout=(test.fallback_timeout + 120))
            result_urc_check = test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",0', timeout=(test.fallback_timeout + 60)) and result_urc_check
            result_urc_check = test.dut.at1.wait_for_strict('.*SSIM READY', timeout=(test.fallback_timeout + 60)) and result_urc_check

            test.log.step('Step 6: Check URCs: "ConMgr/Fallback",0 - "ConMgr/Profile",0 and SSIM READY - Start')
            test.dut.dstl_collect_result('Step 6: Check URCs: "ConMgr/Fallback",0 - "ConMgr/Profile",0 and SSIM READY', result_urc_check)

            test.log.step('Step 7: Check value <currentFbTimerValue> - should changed and count down - Start')
            test.dut.dstl_collect_result('Step 7: Check value <currentFbTimerValue> - should changed and count down', result_check_change_current_fb_timer)


            #test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*', timeout=(fallback_timeout + 180))
            #test.dut.at1.verify_or_wait_for('.*simstatus,5.*', timeout=10)
            #test.dut.at1.verify_or_wait_for('.*SSIM READY.*', timeout=10)

            test.sleep(5)

            test.log.step('Step 7: Check if bootstrap profile is activated - Start')
            # Expect boostrap profile is activated
            _, profiles = test.dut.dstl_get_profile_info()
            bootstrap_profile = profiles[0]
            result = (bootstrap_profile['profile_state'] == '1')
            test.dut.dstl_collect_result(
                'Step 7: Check state of bootstrap profile (=1)', result)

            test.log.step('Step 8: Check downloadmode 3 - Start')
            test.dut.dstl_collect_result('Step 8: Check downloadmode 3',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))

            test.log.com('set sxrat settings back to default - automatic registration')
            test.dut.dstl_set_sxrat()
#            test.dut.at1.verify_or_wait_for('.*SYSSTART.*SUSMA: "ConMgr/Profile",0.*', timeout=120)
            test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*', timeout=120)
            test.log.step('Step 9: Check network registration after fallback - Start')
            test.dut.dstl_collect_result('Step 9: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 10: Check ping google - Start')
            test.dut.dstl_collect_result('Step 10: Check ping google',
                                         test.dut.dstl_check_google_ping())

            test.log.step('Step 11: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 11: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="JTM2M"))

            test.log.step('Step 12: Check that job fallbackConnectivityProvision is failed (Provisioning rule not assigned) - Start')
            test.dut.dstl_collect_result('Step 12: Check that job fallbackConnectivityProvision is failed (Provisioning rule not assigned)',
                                         test.dut.dstl_check_job_fallback_conn_provision_wo_rule(imei, time_before_test))



    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_stop_mods_agent()
        test.sleep(10)
        test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=1, apn="internet")
        #test.dut.dstl_stop_mods_agent()
        #test.sleep(10)
        test.dut.dstl_set_download_mode_wo_agent(download_mode=2)
        test.sleep(10)
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
