# responsible: baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-349 - Local fallback: Feature test

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

import json
import datetime



class Test(BaseTest):

    fallback_rule_name = "UNICORN-POC"

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (SRV03-3631/3804) - Start *****')

        test.dut.dstl_detect()
        test.imei = test.dut.dstl_get_imei()
        test.log.com('*** set susmc parameters ***')
        fallback_timeout = 180
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=fallback_timeout)
        test.sleep(10)

        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

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
            imei = test.dut.dstl_get_imei()
            test.log.info("This is your IMEI: " + imei)
            dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

            test.dut.dstl_collect_result(
                'Step 1: Check state of all available profiles - more than one profile found', True)

            # Get the current time - 1 hour to find the job
            time_before_test = test.dut.dstl_get_mods_time(format=True)



            test.log.step('Step 2: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 2: Initialise all settings for MODS',
                                         test.dut.dstl_init_all_mods_settings())


            test.log.step('Step 3: Check network registration - Start')
            test.dut.dstl_collect_result('Step 3: Check network registration',
                                         test.dut.dstl_check_network_registration())

            test.log.step('Step 4: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 4: Check registering on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.dut.dstl_send_pending_notifications()



            #test.log.step('Step 5: Define fallback rule on MODS - Start')
            #assign_fallback_rule_resp = assign_fallback_rule(device_id, test.fallback_rule_name)
            #test.dut.dstl_collect_result('Step 5: Define fallback rule on MODS',
            #                             assign_fallback_rule_resp.status_code == 200)

            test.log.step('Step 6: Force network to an unavailable network and check URCs')
            test.dut.at1.send_and_verify('at^sxrat=8,8', expect='OK', timeout=200)
            fallback_timeout = 240
            #test.expect(test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",2', timeout=(fallback_timeout + 60)))
            test.expect(test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Fallback",1', timeout=(fallback_timeout + 60)))
            test.expect(test.dut.at1.wait_for_strict('.*SUSMA: "ConMgr/Profile",1', timeout=(fallback_timeout + 60)))
            test.expect(test.dut.at1.wait_for_strict('.*SSIM READY', timeout=(fallback_timeout + 60)))


            test.log.step('Step 7: Check downloadmode should be 3 at this step - Start')
            test.dut.dstl_collect_result('Step 7: Check downloadmode should be 3 at this step',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*3.*OK.*'))


            test.dut.at1.send_and_verify('at^sxrat=7,7', expect='OK', timeout=150)


            test.log.step('Step 7: Check if operational profile 1 is activated - Start')
            # Expect boostrap profile is activated
            _, profiles = test.dut.dstl_get_profile_info()
            bootstrap_profile = profiles[1]
            result = (bootstrap_profile['profile_state'] == '1')
            test.dut.dstl_collect_result(
                'Step 7: Check state of operational profile 1 is (=1)', result)

            test.log.step('Step 8: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS - Start')
            test.dut.dstl_collect_result('Step 8: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS (=internet)',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="internet"))



            test.log.step('Step 9: Check network registration after fallback - Start')
            test.dut.dstl_collect_result('Step 9: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

            test.sleep(15)
            test.dut.dstl_send_pending_notifications()

            test.log.step('Step 10: Check downloadmode should be 2 due to registration - Start')
            test.dut.dstl_collect_result('Step 10: Check downloadmode should be 2 due to registration',
                                         test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                      expect='.*2.*OK.*'))

            test.log.step('Step 11: Check ping google - Start')
            test.dut.dstl_collect_result('Step 11: Check ping google',
                                         test.dut.dstl_check_google_ping())

            test.sleep(80)

            test.log.step('Step 12: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 12: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))


    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()

        test.dut.dstl_print_results()

        test.log.com('***** Testcase: ' + test.test_file + ' (SRV03-3631/3804) - End *****')


if "__main__" == __name__:
    unicorn.main()
