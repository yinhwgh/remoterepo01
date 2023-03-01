# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-340 - Validation of Improve Fallback procedure: Connectivity supervision: 60 days limit - Persistent timer
# pre-condition: 2 SIMINN operational profiles
# duration of test: appr. 25 minutes

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

testkey = "UNISIM01-340"

class Test(BaseTest):

    fallback_rule_name = "UNICORN-POC"

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        devices = get_devices().json()
        test.device_id = get_device_id(devices, test.imei)
        read_mode_set = test.dut.dstl_assign_parameter_read_mode(test.rest_client, test.device_id, 'standard')

        test.dut.dstl_set_default_fb_timer_values()

        test.sleep(5)

        test.dut.dstl_activate_cm_hidden_commands()


    def run(test):

        test.log.step('Step 1: Check all available profiles - Start')
        _, profiles = test.dut.dstl_get_profile_info()
        log_body(profiles)
        if len(profiles) <= 2:
            test.log.info(
                "Only bootstrap and one operational profile was found, does not make sense to continue !!!")
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - not enough profiles found - should be 2 ', False)
        else:

            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than two profile found', True)

            operational_profile_2 = profiles[2]
            if operational_profile_2['profile_state'] == '0':
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

            test.log.step('Step 5: Check max value of fallback timer - Start')
            test.dut.dstl_collect_result('Step 5: Check max value of fallback timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/Timeout",31536000', expect='OK', timeout=5))

            test.log.step('Step 6: Check max value of localswitch timer - Start')
            test.dut.dstl_collect_result('Step 6: Check max value of localswitch timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/LocalSwitchTimeout",31536000', expect='OK', timeout=5))

            test.log.step('Step 7: Check max value of retry timer - Start')
            test.dut.dstl_collect_result('Step 7: Check max value of retry timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/RetryTimeout","31536000,31536000,31536000,31536000,31536000,31536000,31536000,31536000"', expect='OK', timeout=5))

            test.log.step('Step 8: Check max+1 value of fallback timer - Start')
            test.dut.dstl_collect_result('Step 8: Check max+1 value of fallback timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/Timeout",31536001', expect='ERROR', timeout=5))

            test.log.step('Step 9: Check max+1 value of localswitch timer - Start')
            test.dut.dstl_collect_result('Step 9: Check max+1 value of localswitch timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/LocalSwitchTimeout",31536001', expect='ERROR', timeout=5))

            test.log.step('Step 10: Check+1 max value of retry timer - Start')
            test.dut.dstl_collect_result('Step 10: Check max+1 value of retry timer',
                                         test.dut.at1.send_and_verify('at^susmc="ConMgr/Fallback/RetryTimeout","31536001,31536000,31536000,31536000,31536000,31536000,31536000,31536000"', expect='ERROR', timeout=5))


            test.log.info('********** Check persistency of fallback timer after restart - Start **********')

            test.fallback_timeout = 86400
            test.log.info('*** set fallback timer to ' + str(test.fallback_timeout) + ' ***')
            test.dut.dstl_activate_cm_settings(cm_fb_automode=0, cm_fb_timeout=test.fallback_timeout)

            test.log.step('Step 11: Force network to an unavailable network and check URCs - Start')
            test.dut.dstl_collect_result('Step 11: Force network to an unavailable network and check URCs',
                                         test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=200))

            sleep_time = 90
            test.log.info('*** sleep ' + str(sleep_time) + ' seconds ***')
            test.sleep(sleep_time)

            test.log.step('Step 12: Check current fallback timer BEFORE restart of module - Start')
            current_timeout_before_restart = test.dut.dstl_get_current_fb_timer_value()
            test.log.com('current_timeout_before_restart: ' + str(current_timeout_before_restart))

            if (current_timeout_before_restart < test.fallback_timeout) and (current_timeout_before_restart > (test.fallback_timeout - (sleep_time + 10))):
                result = True
            else:
                result = False

            test.dut.dstl_collect_result('Step 12: Check current fallback timer BEFORE restart of module: current=' + str(current_timeout_before_restart)
                                         + ' - fallbacktimer=' + str(test.fallback_timeout), result)
            time_start = time.time()
            test.dut.dstl_restart()
            test.sleep(5)
            test.dut.dstl_init_all_mods_settings()
            test.dut.dstl_activate_cm_hidden_commands()
            duration = round(time.time() - time_start)
            test.log.com('duration: ' + str(duration))

            test.log.step('Step 13: Check current fallback timer AFTER restart of module - Start')
            current_timeout = test.dut.dstl_get_current_fb_timer_value()
            test.log.com('current_timeout: ' + str(current_timeout))

            if (current_timeout < current_timeout_before_restart):
                test.log.com('current_timeout: ' + str(current_timeout) + ' is lower than current_timeout_before_restart: ' + str(current_timeout_before_restart) + ' ==> OK')
                result = True
                if current_timeout > (current_timeout_before_restart - (duration + 10)):
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> OK')
                    test.log.com('duration of restart and wait time was: ' + str(duration))
                    result = True
                else:
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> error')
                    test.log.com('duration of restart and wait time was: ' + str(duration))
                    result = False

            else:
                test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT lower than current_timeout_before_restart: ' + str(
                    current_timeout_before_restart) + ' ==> error')
                result = False

            test.dut.dstl_collect_result('Step 13: Check current fallback timer AFTER restart of module: current=' + str(current_timeout)
                                         + ' - fallbacktimer=' + str(test.fallback_timeout), result)

            test.log.com('set sxrat settings back to default - automatic registration')
            test.dut.dstl_set_sxrat()
            #test.dut.at1.send_and_verify('at^sxrat=7,7', expect='OK', timeout=150)

            test.log.step('Step 14: Check network registration after persistent fallback timer test - Start')
            test.dut.dstl_collect_result('Step 14: Check network registration after persistent fallback timer test',
                                         test.dut.dstl_check_network_registration())

            test.sleep(5)
            test.dut.dstl_send_pending_notifications()

            test.log.step('Step 15: Check downloadmode should be 2 due to registration - Start')
            test.dut.dstl_collect_result('Step 15: Check downloadmode should be 2 due to registration',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))


            test.log.info('********** Check persistency of fallback timer after restart - End **********')


            test.log.info('********** Check persistency of localswitch timer after restart - Start **********')

            test.fallback_timeout = 90
            test.localswitch_timeout = 3600
            test.log.info('*** set localswitch_timeout timer to ' + str(test.localswitch_timeout) + ' ***')
            test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout, cm_fb_local_sw_timer=test.localswitch_timeout)

            test.log.step('Step 16: Force network to an unavailable network and check URCs - Start')
            test.dut.dstl_collect_result('Step 16: Force network to an unavailable network and check URCs',
                                         test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=200))

            sleep_time = 40
            test.log.info('*** sleep ' + str(sleep_time) + ' seconds before fallback to profile 1***')
            test.sleep(sleep_time)

            current_timeout_before_restart = test.dut.dstl_get_current_fb_timer_value()
            result_urc_check = test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Fallback",1,1.*', timeout=300)
            result_urc_check = test.dut.at1.wait_for('.*SUSMA: "ConMgr/Profile",1.*', append=True, timeout=20) and result_urc_check

            sleep_time = 180
            test.log.info('*** sleep ' + str(sleep_time) + ' seconds after fallback to profile 1 ***')
            test.sleep(sleep_time)

            test.log.step('Step 17: Check current localswitch timer BEFORE restart of module - Start')
            current_timeout_before_restart = test.dut.dstl_get_current_local_switch_timer_value()
            test.log.com('current_timeout_before_restart: ' + str(current_timeout_before_restart))

            if (current_timeout_before_restart < test.localswitch_timeout) and (current_timeout_before_restart > (test.localswitch_timeout - (sleep_time + 10))):
                result = True
            else:
                result = False

            test.dut.dstl_collect_result('Step 17: Check current localswitch timer BEFORE restart of module: current=' + str(current_timeout_before_restart)
                                         + ' - localswitch timer=' + str(test.localswitch_timeout), result)
            time_start = time.time()
            test.dut.dstl_restart()
            test.sleep(5)
            test.dut.dstl_init_all_mods_settings()
            test.dut.dstl_activate_cm_hidden_commands()
            duration = round(time.time() - time_start)
            test.log.com('duration: ' + str(duration))

            test.log.step('Step 18: Check current localswitch timer AFTER restart of module - Start')
            current_timeout = test.dut.dstl_get_current_local_switch_timer_value()
            test.log.com('current_timeout: ' + str(current_timeout))

            if (current_timeout < current_timeout_before_restart):
                test.log.com('current_timeout: ' + str(current_timeout) + ' is lower than current_timeout_before_restart: ' + str(current_timeout_before_restart) + ' ==> OK')
                result = True
                if current_timeout > (current_timeout_before_restart - (duration + 10)):
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> OK')
                    test.log.com('duration of restart and wait time was: ' + str(duration))
                    result = True
                else:
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> error')
                    test.log.com('duration of restart and wait time was: ' + str(duration))
                    result = False

            else:
                test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT lower than current_timeout_before_restart: ' + str(
                    current_timeout_before_restart) + ' ==> error')
                result = False

            test.dut.dstl_collect_result('Step 18: Check current localswitch timer AFTER restart of module: current=' + str(current_timeout)
                                         + ' - localswitch timer=' + str(test.localswitch_timeout), result)

            test.log.com('set sxrat settings back to default - automatic registration')
            test.dut.dstl_set_sxrat()
            #test.dut.at1.send_and_verify('at^sxrat=7,7', expect='OK', timeout=150)

            test.log.step('Step 19: Check network registration after persistent localswitch timer test - Start')
            test.dut.dstl_collect_result('Step 19: Check network registration after persistent localswitch timer test',
                                         test.dut.dstl_check_network_registration())

            test.sleep(5)
            test.dut.dstl_send_pending_notifications()

            dstl.log.info('*** check activated profile: 2 ***')
            test.dut.at1.send_and_verify('at^susma?', expect='.*"LPA/Profiles/Info",1,1,.*OK.*')

            test.log.step('Step 20: Check downloadmode should be 2 due to registration - Start')
            test.dut.dstl_collect_result('Step 20: Check downloadmode should be 2 due to registration',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))

            test.log.info('********** Check persistency of localswitch timer after restart - End **********')


            test.log.info('********** Check persistency of retry timer after restart - Start **********')

            test.dut.dstl_activate_cm_hidden_commands()
            test.fallback_timeout = 120
            test.localswitch_timeout = 100
            #test.retry_timeout = '"300,43200,86400,259200,604800,1814400,2592000,7776000"'
            test.retry_timeout_list = [3600,43200,86400,259200,604800,1814400,2592000,7776000]
            test.retry_timeout = '"' + str(test.retry_timeout_list[0]) + ','\
                                         + str(test.retry_timeout_list[1]) + ','\
                                         + str(test.retry_timeout_list[2]) + ','\
                                         + str(test.retry_timeout_list[3]) + ','\
                                         + str(test.retry_timeout_list[4]) + ','\
                                         + str(test.retry_timeout_list[5]) + ','\
                                         + str(test.retry_timeout_list[6]) + ','\
                                         + str(test.retry_timeout_list[7]) + '"'

            test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout,
                                                       cm_fb_local_sw_timer=test.localswitch_timeout,
                                                       cm_fb_retry_timer=test.retry_timeout)

            # test.log.info('*** set localswitch_timeout timer to ' + str(test.localswitch_timeout) + ' ***')
            # test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=test.fallback_timeout, cm_fb_local_sw_timer=test.localswitch_timeout)


            dstl.log.info('*** read susma? ***')
            test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')

            test.log.step('Step 21: Force network to an unavailable network and check URCs - Start')
            test.dut.dstl_collect_result('Step 21: Force network to an unavailable network and check URCs',
                                         test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=200))

            # sleep_time = 40
            # test.log.info('*** sleep ' + str(sleep_time) + ' seconds before fallback to profile 1 ***')
            # test.sleep(sleep_time)

            #current_timeout_before_restart = test.dut.dstl_get_current_fb_timer_value()
            # result_urc_check = test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Fallback",2,3.*', timeout=600)
            # result_urc_check = test.dut.at1.wait_for('.*SUSMA: "ConMgr/Profile",2.*', append=True, timeout=20) and result_urc_check

            max_count = 30
            wait_count = 0
            leave_loop = False
            bootstrap_urc = False
            while leave_loop == False and wait_count < max_count:
                dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))

                retry_idx, current_timeout = test.dut.dstl_get_current_retry_timer_values()
                test.log.com('current_timeout (now): ' + str(current_timeout))
                test.log.com('retry_idx: ' + str(retry_idx) + ' (expected: 1)')

                test.sleep(30)
                #read_data = test.dut.at1.last_response
                read_data = test.dut.at1.read(append=True)

                test.log.com('last response of loop ' + str(wait_count) + ': ' + read_data)
                if '"ConMgr/Fallback",0,2' in read_data:
                    bootstrap_urc = True
                    #result_urc_check = True
                    test.log.com('bootstrap_urc = True, because of ^SUSMA: "ConMgr/Fallback",0,2')
                else:
                    test.log.com('no "ConMgr/Fallback",0,2 occurs')

                if '"ConMgr/Fallback",1,2' in read_data:
                    test.log.com('^SUSMA: "ConMgr/Fallback",1,2 occured')
                    if bootstrap_urc == True:
                        leave_loop = True
                        test.log.com('leave loop, because of ^SUSMA: "ConMgr/Fallback",1,2 and bootstrap was available before')
                else:
                    test.log.com('no "ConMgr/Fallback",1,2 occurs')

                dstl.log.info('*** read susma? in loop ***')
                test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')

                wait_count = wait_count + 1
                dstl.log.com("wait_count: " + str(wait_count))


            sleep_time = 180
            test.log.info('*** sleep ' + str(sleep_time) + ' seconds after fallback to profile 1 ***')
            test.sleep(sleep_time)

            test.log.step('Step 22: Check current retry timer BEFORE restart of module - Start')
            retry_idx, current_timeout_before_restart = test.dut.dstl_get_current_retry_timer_values()
            if retry_idx == 1:

                test.log.com('current_timeout_before_restart: ' + str(current_timeout_before_restart))

                if (current_timeout_before_restart < test.retry_timeout_list[0]):
#                if (current_timeout_before_restart < test.retry_timeout_list[0]) and (current_timeout_before_restart > (test.retry_timeout_list[0] - (sleep_time + 10))):

                    result = True
                else:
                    result = False

                test.dut.dstl_collect_result('Step 22: Check current retry timer BEFORE restart of module: current=' + str(current_timeout_before_restart)
                                         + ' - retry timer=' + str(test.retry_timeout_list[0]), result)
            else:
                test.dut.dstl_collect_result('Step 22: Check current retry timer BEFORE restart of module: ERROR -> wrong index: ' + str(retry_idx) + ' , expected: 1', False)

            time_start = time.time()
            test.dut.dstl_restart()
            test.sleep(5)
            test.dut.dstl_init_all_mods_settings()
            test.dut.dstl_activate_cm_hidden_commands()
            test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
            duration = round(time.time() - time_start)
            test.log.com('duration: ' + str(duration))

            test.log.step('Step 23: Check current retry timer AFTER restart of module - Start')
            # current_timeout = test.dut.dstl_get_current_local_switch_timer_value()
            retry_idx, current_timeout = test.dut.dstl_get_current_retry_timer_values()

            test.log.com('current_timeout: ' + str(current_timeout))

            if retry_idx == 1:
                if (current_timeout < current_timeout_before_restart):
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is lower than current_timeout_before_restart: ' + str(current_timeout_before_restart) + ' ==> OK')
                    result = True
                    if current_timeout > (current_timeout_before_restart - (duration + 10)):
                        test.log.com('current_timeout: ' + str(current_timeout) + ' is larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> OK')
                        test.log.com('duration of restart and wait time was: ' + str(duration))
                        result = True
                    else:
                        test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT larger than current_timeout_before_restart-(duration+10) seconds: ' + str(
                            current_timeout_before_restart - (duration + 10)) + ' ==> error')
                        test.log.com('duration of restart and wait time was: ' + str(duration))
                        result = False

                else:
                    test.log.com('current_timeout: ' + str(current_timeout) + ' is NOT lower than current_timeout_before_restart: ' + str(
                        current_timeout_before_restart) + ' ==> error')
                    result = False

                test.dut.dstl_collect_result('Step 23: Check current retry timer AFTER restart of module: current=' + str(current_timeout)
                                         + ' - retry timer=' + str(test.retry_timeout_list[0]), result)

            else:
                test.dut.dstl_collect_result(
                    'Step 23: Check current retry timer AFTER restart of module: ERROR -> wrong index: ' + str(retry_idx) + ' , expected: 1', False)


            test.log.com('set sxrat settings back to default - automatic registration')
            test.dut.dstl_set_sxrat()
            #test.dut.at1.send_and_verify('at^sxrat=7,7', expect='OK', timeout=150)

            test.log.step('Step 24: Check network registration after persistent localswitch timer test - Start')
            test.dut.dstl_collect_result('Step 24: Check network registration after persistent localswitch timer test',
                                         test.dut.dstl_check_network_registration())

            test.sleep(5)
            test.dut.dstl_send_pending_notifications()

            dstl.log.info('*** check activated profile: 2 ***')
            test.dut.at1.send_and_verify('at^susma?', expect='.*"LPA/Profiles/Info",1,1,.*OK.*')

            test.log.step('Step 25: Check downloadmode should be 2 due to registration - Start')
            test.dut.dstl_collect_result('Step 25: Check downloadmode should be 2 due to registration',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))

            test.log.info('********** Check persistency of retry timer after restart - End **********')




    def cleanup(test):
        test.dut.dstl_set_sxrat()
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_set_default_fb_timer_values()
        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=2, apn="internet")
        test.sleep(5)
        test.dut.dstl_check_network_registration()
        test.dut.dstl_start_mods_agent()
        test.sleep(5)
        test.dut.dstl_check_registering_on_mods()
        #read_mode_set = test.dut.dstl_assign_parameter_read_mode(test.device_id, 'maximum')
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
