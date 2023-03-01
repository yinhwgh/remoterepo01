# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-318 - Local fallback from operational profile 2 to 1
# pre-condition: 2 SIMINN operational profiles

import unicorn
import re
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
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

testkey = "UNISIM01-318"

class Test(BaseTest):

    fallback_rule_name = "UNICORN-POC"

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        test.log.com('*** set susmc parameters ***')
        test.fallback_timeout = 120
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout)
        test.sleep(10)

        test.dut.dstl_activate_cm_hidden_commands()


    def run(test):

        test.log.step('Step 1: Check all available profiles - Start')
        _, profiles = test.dut.dstl_get_profile_info()
        log_body(profiles)
        if len(profiles) <= 2:
            test.log.info(
                "Only bootstrap and one operational profile was found, does not make sense to continue !!!")
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - more than 2 profile found', False)
        else:

            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than one profile found', True)

            operational_profile_1 = profiles[1]
            operational_profile_2 = profiles[2]
            if operational_profile_2['profile_state'] != '1':
                test.dut.dstl_stop_mods_agent()
                test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=2, apn="internet")
                test.dut.dstl_start_mods_agent()

            imei = test.dut.dstl_get_imei()
            test.log.info("This is your IMEI: " + imei)
            dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

            # Get the current time - 1 hour to find the job
            #time_before_test = test.dut.dstl_get_mods_time(format=True)

            test.log.step('Step 2: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 2: Initialise all settings for MODS',
                                         test.dut.dstl_init_all_mods_settings())


            test.log.step('Step 3: Check network registration - Start')
            test.dut.dstl_collect_result('Step 3: Check network registration',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 4: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 4: Check registering on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.sleep(5)
            test.dut.dstl_send_pending_notifications()

            # test.log.step('Step 5: Define fallback rule on MODS - Start')
            # assign_fallback_rule_resp = assign_fallback_rule(device_id, test.fallback_rule_name)
            # test.dut.dstl_collect_result('Step 5: Define fallback rule on MODS',
            #                              assign_fallback_rule_resp.status_code == 200)

            test.log.step('Step 5: Force network to an unavailable network and check URCs - Start')

            test.dut.dstl_collect_result('Step 5: Force network to an unavailable network and check URCs',
                                         test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=200))

            #test.fallback_timeout = 240

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
                if 'SUSMA: "ConMgr/Fallback",1' in read_data:
                    leave_loop = True
                    result_urc_check = True
                    test.log.com('leave loop, because of ^SUSMA: "ConMgr/Fallback",1')

                wait_count = wait_count + 1

            #test.expect(test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",2', timeout=(fallback_timeout + 60)))
            if leave_loop != True:
                result_urc_check = test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Fallback",1', timeout=(test.fallback_timeout + 120))
            if 'SUSMA: "ConMgr/Profile",1' not in read_data:
                result_urc_check = test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",1', timeout=(test.fallback_timeout + 60)) and result_urc_check
            if 'SSIM READY' not in read_data:
                result_urc_check = test.dut.at1.wait_for_strict('.*SSIM READY', timeout=(test.fallback_timeout + 60)) and result_urc_check

            test.log.step('Step 6: Check URCs: "ConMgr/Fallback",1 - "ConMgr/Profile",1 and SSIM READY - Start')
            test.dut.dstl_collect_result('Step 6: Check URCs: "ConMgr/Fallback",1 - "ConMgr/Profile",1 and SSIM READY', result_urc_check)

            test.log.step('Step 7: Check value <currentFbTimerValue> - should changed and count down - Start')
            test.dut.dstl_collect_result('Step 7: Check value <currentFbTimerValue> - should changed and count down', result_check_change_current_fb_timer)

            test.log.step('Step 8: Check downloadmode should be 3 at this step - Start')
            test.dut.dstl_collect_result('Step 8: Check downloadmode should be 3 at this step',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))

            test.log.com('set sxrat settings back to default - automatic registration')
            test.dut.dstl_set_sxrat()
            #test.dut.at1.send_and_verify('at^sxrat=7,7', expect='OK', timeout=150)

            test.log.step('Step 9: Check if operational profile 1 is activated - Start')
            _, profiles = test.dut.dstl_get_profile_info()
            operational_profile_1 = profiles[1]
            result = (operational_profile_1['profile_state'] == '1')
            iccid_id = operational_profile_1['iccid']
            test.log.com('iccid_id: ' + iccid_id)

            test.dut.dstl_collect_result(
                'Step 9: Check state of operational profile 1 is (=1)', result)

            test.log.step('Step 10: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS - Start')
            test.dut.dstl_collect_result('Step 10: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS (=internet)',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="internet"))

            test.log.step('Step 11: Check network registration after fallback - Start')
            test.dut.dstl_collect_result('Step 11: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

            test.sleep(15)
            test.dut.dstl_send_pending_notifications()

            test.log.step('Step 12: Check downloadmode should be 2 due to registration - Start')
            test.dut.dstl_collect_result('Step 12: Check downloadmode should be 2 due to registration',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))

            test.log.step('Step 13: Check ping google - Start')
            test.dut.dstl_collect_result('Step 13: Check ping google',
                                         test.dut.dstl_check_google_ping())

            test.log.step('Step 14: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 14: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

            test.log.info('*** wait 80 seconds for update data on IoT Suite ***')
            test.sleep(80)

            test.log.step('Step 15: Get all attributes from device - Start')
            result, dev_obj = test.dut.dstl_get_all_attributes_from_device(test.rest_client, imei)
            test.dut.dstl_collect_result('Step 15: Get all all attributes from device', result)


            test.log.step('Step 16: Check active ICCID on IoT Suite - Start')
            active_iccid = dev_obj['shadow']['reportedState']['instances']['33096']['0']['1']
            test.log.com('active_iccid on IoT Suite: ' + active_iccid + ' compared to ICCID of profile 1:' + iccid_id)

            if active_iccid in iccid_id:
                result = True
            else:
                result = False
            test.dut.dstl_collect_result('Step 16: Check active ICCID on IoT Suite', result)


    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_set_default_fb_timer_values()
        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=2, apn="internet")
        test.sleep(10)
        test.dut.dstl_check_network_registration()
        test.dut.dstl_start_mods_agent()
        test.sleep(5)
        test.dut.dstl_check_registering_on_mods()
        test.sleep(5)
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
