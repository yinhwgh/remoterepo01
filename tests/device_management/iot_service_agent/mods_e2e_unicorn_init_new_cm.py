# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# Test case: UNISIM01-212: E2E tests needs to be started from a well configured device (with connection manager),
#                          module is configured with factory settings

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

KPI_NAME = "esim_provisioning_delete_subscription"
KPI_TYPE = "bin"
testkey = "UNISIM01-212"

class Test(BaseTest):
    """
    Init
    """
    iccid_results_list = []

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.dut.dstl_set_real_time_clock()
        test.sleep(5)
        test.dut.dstl_start_mods_agent()

        test.apn_profile_name = test.dut.dstl_get_apn_profile_name()
        test.log.com('apn_profile_name: case: ' + test.apn_profile_name)

        if test.apn_profile_name == 'ELISA':
            test.apn_name = 'ELISA'
            test.prid = 'ELISA'
        else:
            test.apn_name = 'Siminn'
            test.prid = 'UNICORN-POC'

        test.dut.dstl_show_cm_table()

    def run(test):
        profile_list = []

        test.log.step('Step 1: Check all available profiles - Start')
        result, profile_list = test.dut.dstl_get_profile_info()
        if len(profile_list) == 1:
            test.log.info(
                "Only one profile found - no operational profile should be deleted, Steps from deleting operational profile are not executed !!!")
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - only one profile found', True)

            # test.log.info('Check device on MODS - Start')
            # imei = test.dut.dstl_get_imei()
            # test.log.info("This is your IMEI: " + imei)
            # dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)
            #
            # if dev_on_mods == True:
            #     test.log.step('Step 2: Delete device on MODS server - Start')
            #     test.dut.dstl_collect_result('Step 2: Delete device on MODS server',
            #                                  test.dut.dstl_delete_device(device_id))

        else:
            test.dut.dstl_collect_result(
                'Step 1: Check all available profiles - more than one profile found', True)

            test.log.step('Step 2: Initialise all settings for MODS - Start')
            test.dut.dstl_collect_result('Step 2: Initialise all settings for MODS',
                                         test.dut.dstl_init_all_mods_settings())

            test.log.step('Step 3: Stop MODS agent - Start')
            test.dut.dstl_collect_result('Step 3: Stop MODS agent', test.dut.dstl_stop_mods_agent())

            test.log.step('Step 4: Set download mode to 11 - Start')
            test.dut.dstl_collect_result('Step 4: Set download mode to 11',
                                         test.dut.dstl_set_download_mode_wo_agent(download_mode=11))

            test.log.step('Step 5: Activate LPA engine - Start')
            test.dut.dstl_collect_result('Step 5: Activate LPA engine',
                                         test.dut.dstl_activate_lpa_engine())

            test.log.step('Step 6: Enable bootstrap and JTM2M apns - Start')
            test.dut.dstl_collect_result('Step 6: Enable bootstrap and JTM2M apns',
                                         test.dut.dstl_activate_bootstrap_and_apns())

            test.log.step('Step 7: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS - Start')
            test.dut.dstl_collect_result('Step xx: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)

            # test.log.step('Step 8: Check network registration - Start')
            # test.dut.dstl_collect_result('Step 8: Check network registration',
            #                              test.dut.dstl_force_network_registration())

            test.log.step('Step 8: Check network registration - Start')
            result = test.dut.dstl_check_network_registration()
            if result == False:
                test.log.com('++++ WORKAROUND restart - Start *****')
                test.dut.dstl_restart()
                test.sleep(10)
                test.dut.dstl_init_all_mods_settings()
                test.log.warn(' second attempt to register !!!')
                test.dut.dstl_collect_result('Step 8: Check network registration - 2nd attempt !!!',
                                             test.dut.dstl_check_network_registration())
                test.log.com('++++ WORKAROUND restart - End *****')
            else:
                test.dut.dstl_collect_result('Step 8: Check network registration',
                                         test.dut.dstl_check_network_registration())

            test.dut.at1.send_and_verify_retry("at+creg?", expect=".*O.*")
            test.dut.at1.send_and_verify_retry("at+cereg?", expect=".*O.*")

            test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",[0379]')
            test.sleep(5)

            test.log.step('Step 9: Delete all subscription on module - Start')
            test.dut.dstl_collect_result('Step 9: Delete all subscription on module',
                                         test.dut.dstl_delete_all_subscriptions_on_module(
                                             profile_list))

            test.log.step('Step 10: Start MODS agent - Start')
            test.dut.dstl_collect_result('Step 10: Start MODS agent',
                                         test.dut.dstl_start_mods_agent())

            # test.log.com('++++ WORKAROUND SRV03-3163 - Start *****')
            # test.dut.dstl_restart()
            # test.sleep(10)
            # test.dut.dstl_init_all_mods_settings()
            # test.dut.dstl_activate_lpa_engine()
            # # test.dut.dstl_force_network_registration()
            # test.dut.dstl_check_network_registration()
            # test.log.com('++++ WORKAROUND SRV03-3163 - End *****')

            test.log.step('Step 11: Create/check device on MODS - Start')
            imei = test.dut.dstl_get_imei()
            test.log.info("This is your IMEI: " + imei)
            result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
            test.dut.dstl_collect_result('Step 11: Create/check device on MODS', result)

            test.log.step('Step 12: Check registering on MODS - Start')
            test.dut.dstl_collect_result('Step 12: Check registering on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.log.step('Step 13: Send pending notifications - Start')
            test.dut.dstl_collect_result('Step 13: Send pending notifications',
                                         test.dut.dstl_send_pending_notifications())

            test.log.step(
                'Step 14: Get all subscriptions IDs which belong to your IMEI and delete all subscriptions - Start')
            iccids = test.dut.dstl_get_all_iccids(test.rest_client, imei)
            subscription_ids = test.dut.dstl_get_all_subscription_ids(test.rest_client, imei)
            subscriptions = test.dut.dstl_get_all_subscriptions(test.rest_client, imei)

            test.log.info(
                "We have decided to use drop function instead of delete to delete all ICCIDs from MODS server")
            result = test.dut.dstl_drop_all_subscriptions(test.rest_client, subscription_ids, iccids)
            # for subscription_id in subscription_ids:
            #     test.delete_subscription(subscription_id)
            #     test.activate_oper_prof_manually()
            #     test.sleep(10)

            test.dut.dstl_collect_result(
                'Step 14: Get all subscriptions IDs which belong to your IMEI and delete all subscriptions',
                result)

            test.log.step('Step 15: Send pending notifications again - Start')
            test.dut.dstl_collect_result('Step 15: Send pending notifications again',
                                         test.dut.dstl_send_pending_notifications())

            # test.log.step('Step 15: Delete device on MODS server - Start')
            # test.dut.dstl_collect_result('Step 15: Delete device on MODS server',
            #                              test.dut.dstl_delete_device(device_id))

            # test.log.info(f'{20 * "*"} Delete device {20 * "*"}')
            # test.delete_device(device_id)

            test.log.step('Step 16: Create already deleted subscriptions back on MODS - Start')

            result, test.iccid_results_list = test.dut.dstl_create_all_subscriptions(test.rest_client, subscriptions)
            test.dut.dstl_collect_result(
                'Step 16: Create already deleted subscriptions back on MODS', result)

            test.log.step('Step 17: Check status of module - Start')
            result = True
            # result = test.dut.dstl_force_network_registration() and result
            test.dut.at1.send_and_verify('at+cops?', expect='.*OK.*')
            result = test.dut.dstl_check_network_registration() and result
            # result = test.dut.dstl_stop_mods_agent() and result
            result = test.dut.dstl_get_all_mods_settings() and result
            test.dut.dstl_collect_result('Step 17: Check status of module', result)


    def cleanup(test):

        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_set_prid_wo_agent(prid_name='""')
        test.dut.dstl_set_download_mode_wo_agent(download_mode=0)
#        test.dut.dstl_start_mods_agent()
#        test.dut.dstl_stop_mods_agent()

#        if test.dut.dstl_check_deactivated_lpa_engine():
        test.dut.dstl_activate_lpa_engine()
        test.dut.dstl_deactivate_bootstrap()
        test.dut.dstl_set_apns()
        test.dut.dstl_delete_cm_table()

        # test.log.info('Check device on MODS - Start')
        # imei = test.dut.dstl_get_imei()
        # test.log.info("This is your IMEI: " + imei)
        # dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)
        #
        # if dev_on_mods == True:
        #     test.log.info('Delete device on MODS server')
        #     test.dut.dstl_delete_device(device_id)

        test.sleep(10)

        test.dut.dstl_print_results()

        test.log.com('****************************')
        test.log.com('Additional result info of Step 16: ')
        test.log.com('ICCID:                  created:   message: ')
        for i in range(len(test.iccid_results_list)):
            test.log.com(str(test.iccid_results_list[i][0]) + '  -  ' + str(
                test.iccid_results_list[i][1]) + '  -  ' +
                         test.iccid_results_list[i][2])
        test.log.com('****************************')

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)

        # delete test result list
        del test.iccid_results_list[:]

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type="bin", total=test.verdicts_counter_total, device=test.dut)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
