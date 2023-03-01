# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com, katrin.kubald@thalesgroup.com
# location: Berlin

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

KPI_NAME ="esim_provisioning_delete_subscription"
KPI_NAME_NUM="time_to_first_fix"
KPI_TYPE = "bin"


class Test(BaseTest):
    """
    Init
    """
    iccid_results_list = []

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_set_real_time_clock()
        test.sleep(5)


    def run(test):
        profile_list = []

        test.log.step('Step 1: Check all available profiles - Start')
        result, profile_list = test.dut.dstl_get_profile_info()
        if len(profile_list) == 1:
            test.log.info("Only one profile found - no operational profile should be deleted, Steps 2 - 10 are not executed !!!")
            test.dut.dstl_collect_result('Step 1: Check all available profiles - only one profile found', True)
        else:
            test.dut.dstl_collect_result('Step 1: Check all available profiles - more than one profile found', True)

            test.log.step('Step 2: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 2: Initialise all settings for MODS', test.dut.dstl_init_all_mods_settings())

            test.log.step('Step 3: Start MODS agent - Start')
            test.dut.dstl_collect_result('Step 3: Start MODS agent', test.dut.dstl_start_mods_agent())

            test.log.step('Step 4: Check network registration - Start')
            test.dut.dstl_collect_result('Step 4: Check network registration',
                                         test.dut.dstl_force_network_registration())
            test.dut.at1.send_and_verify_retry("at+creg?", expect="OK", wait_for="CREG: [012],5", retry=15, timeout=5)

            test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",7')
            test.sleep(5)

            test.log.step('Step 5: Create/check device on MODS - Start')
            imei = test.dut.dstl_get_imei()
            test.log.info("This is your IMEI: " + imei)
            result, device_id = test.dut.dstl_create_device_on_mods(imei)
            test.dut.dstl_collect_result('Step 5: Create/check device on MODS', result)

            test.log.step('Step 6: Set download mode to 11 - Start')
            test.dut.dstl_collect_result('Step 6: Set download mode to 11', test.dut.dstl_set_download_mode(download_mode=11))

            test.log.step('Step 7: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 7: Check registering on MODS', test.dut.dstl_check_registering_on_mods())

            # test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            # wait_count = 0
            # while ("deregistered" in test.dut.at1.last_response or "registering" in test.dut.at1.last_response or "error" in
            #        test.dut.at1.last_response) and wait_count < 30:
            #     # wait_count: 30 * 30 => 900 seconds => 15 minutes
            #     test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            #     test.sleep(30)
            #     wait_count = wait_count + 1

            test.log.step(
                'Step 8: Get all subscriptions IDs which belong to your IMEI and delete all subscriptions - Start')
            iccids = test.dut.dstl_get_all_iccids(imei)
            subscription_ids = test.dut.get_all_subscription_ids(imei)

            result = test.dut.dstl_delete_all_subscriptions(subscription_ids)
            # for subscription_id in subscription_ids:
            #     test.delete_subscription(subscription_id)
            #     test.activate_oper_prof_manually()
            #     test.sleep(10)

            test.dut.dstl_collect_result('Step 8: Get all ICCIDs which belong to your IMEI', result)

            test.log.step('Step 9: Check if values after deletion of all subscriptions are correct (bootstrap) - Start')
            test.dut.dstl_collect_result(
                'Step 9: Check if values after deletion of all subscriptions are correct (bootstrap)',
                test.dut.dstl_check_bootstrap_after_delete_subscription(), test_abort=True)

            test.log.step('Step 10: Delete device on MODS server - Start')
            test.dut.dstl_collect_result('Step 10: Delete device on MODS server', test.dut.dstl_delete_device(device_id))

            # test.log.info(f'{20 * "*"} Delete device {20 * "*"}')
            # test.delete_device(device_id)

            test.log.step('Step 11: Create already deleted subscriptions back on MODS - Start')
            result, test.iccid_results_list = test.dut.dstl_create_all_subscriptions(iccids)
            test.dut.dstl_collect_result('Step 11: Create already deleted subscriptions back on MODS', result)

            # test.log.info(f'{20 * "*"} Create already deleted subscriptions back on MODS {20 * "*"}')
            # for iccid in iccids:
            #     test.create_subscription(iccid)
            #     test.sleep(5)

            # test.expect(test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/0/0/10","APN_NAME","JTM2M"', expect='.*OK.*'))
            # test.expect(test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/","APN","JTM2M"', expect='.*OK.*'))
            # test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))

            test.log.step('Step 12: Check status of module - Start')
            result = True
            result = test.dut.dstl_force_network_registration() and result
            # result = test.dut.dstl_stop_mods_agent() and result
            result = test.dut.dstl_get_all_mods_settings() and result
            #        result = test.dut.at1.send_and_verify('at^susma="LPA/Profiles/Disable",0', expect='.*OK.*') and result
            #        result = test.dut.at1.send_and_verify('at^susma="LPA/Profiles/Info"', expect='.* "LPA/Profiles/Info",0,0,.*OK.*') and result
            test.dut.dstl_collect_result('Step 12: Check status of module', result)




    def cleanup(test):

        test.dut.dstl_stop_mods_agent()
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

        test.dut.dstl_deactivate_bootstrap()
        test.sleep(10)

        test.dut.dstl_print_results()

        test.log.com('****************************')
        test.log.com('Additional result info of Step 11: ')
        test.log.com('ICCID:                  created:   message: ')
        for i in range(len(test.iccid_results_list)):
            test.log.com(str(test.iccid_results_list[i][0]) + '  -  ' + str(test.iccid_results_list[i][1]) + '  -  ' +
                         test.iccid_results_list[i][2])
        test.log.com('****************************')

        # delete test result list
        del test.iccid_results_list[:]

        print("passed: " + str(test.verdicts_counter_passed))
        print("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type="bin", total=test.verdicts_counter_total, device=test.dut)

        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
