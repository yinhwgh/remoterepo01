# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-218 - fallback with faallback automode=1
#                           since pool/project concept no fallback rule is available anymore
#                           old: fallback with defined fallback rule

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

    systart_timeout = 300
    fallback_rule_name = "UNICORN-POC"

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
            imei = test.dut.dstl_get_imei()
            test.log.info("This is your IMEI: " + imei)
            dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than one profile found', True)

            # Get the current time - 1 hour to find the job
            time_before_test = test.dut.dstl_get_mods_time(format=True)

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


            # test.log.step('Step 6: Define fallback rule on MODS - Start')
            # assign_fallback_rule_resp = assign_fallback_rule(device_id, test.fallback_rule_name)
            # test.dut.dstl_collect_result('Step 6: Define fallback rule on MODS',
            #                              assign_fallback_rule_resp.status_code == 200)

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

            test.log.step('Step 7: Check downloadmode 3 - Start')
            test.dut.dstl_collect_result('Step 7: Check downloadmode 3',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))

            rat = test.dut.dstl_get_rat()
            test.dut.at1.send_and_verify(f'at+cops=0,,,{rat}', expect='OK', timeout=150)

            test.dut.at1.wait_for('.*SYSSTART.*"ConMgr/Profile",2.*', timeout=test.systart_timeout)

            test.dut.dstl_init_all_mods_settings_after_switch()

            test.log.step('Step 8: Check network registration after fallback - Start')
            test.dut.dstl_collect_result('Step 8: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 9: Find the job fallbackConnectivityProvision is started and finished successfully - Start')
            test.dut.dstl_collect_result('Step 9: Find the job fallbackConnectivityProvision is started and finished successfully',
                                        test.dut.dstl_check_job_fallback_conn_provision_with_rule(imei, time_before_test))

            # test.log.step("8. Find the job and wait until it is finished")
            # jobs = get_jobs_since_time(imei, job_type='fallbackConnectivityProvision',
            #                            time=time_before_test).json()
            # log_body(jobs)
            # max_count = 30
            # wait_count = 0
            # while jobs['numberOfElements'] == 0 and wait_count < max_count:
            #     dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            #     jobs = get_jobs_since_time(imei, job_type='fallbackConnectivityProvision',
            #                                time=time_before_test).json()
            #     log_body(jobs)
            #     test.sleep(10)
            #     wait_count = wait_count + 1
            #     test.log.info("wait_count:" + str(wait_count))
            #
            # test.log.info("A job was found. Checking its status ...")
            # latest_job = jobs['content'][-1]
            # job_status = latest_job["status"]
            # # Sometimes the status is suspended and gets succeeded after a while.
            # wait_count = 0
            # while job_status != 'succeeded' and wait_count < 30:
            #     test.dut.at1.send_and_verify_retry("at^smoni", expect="OK", retry=5, wait_after_send=3,
            #                                        retry_expect="CME ERROR")
            #     test.expect(
            #         test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            #     jobs = get_jobs_since_time(imei, job_type='fallbackConnectivityProvision',
            #                                time=time_before_test).json()
            #     latest_job = jobs['content'][-1]
            #     job_status = latest_job["status"]
            #     log_body(jobs)
            #     test.sleep(30)
            #     wait_count = wait_count + 1
            #
            # if job_status == 'succeeded':
            #     test.log.info("The job succeeded.")
            #
            # else:
            #     test.log.info("The job NOT succeeded.")

            test.sleep(15)

            test.log.step('Step 10: Check ping google - Start')
            test.dut.dstl_collect_result('Step 10: Check ping google',
                                         test.dut.dstl_check_google_ping())

            test.log.step('Step 11: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 11: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

            test.log.step('Step 12: Check downloadmode 2 after fallback - Start')
            test.dut.dstl_collect_result('Step 12: Check downloadmode 2 after fallback',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))


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
