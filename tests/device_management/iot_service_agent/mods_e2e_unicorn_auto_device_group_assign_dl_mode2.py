# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-354 - IoT Suite registration with download mode 2 and auto assignment of device group matching PRID
#            Pre-condition: operational profile has to be available

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

testkey = "UNISIM01-354"

class Test(BaseTest):
    """
    Test Case: IoT Suite registration with download mode 2 and auto assignment of device group matching PRID
    """


    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'
        test.project_name = 'UNICORN-POC'

        test.dut.dstl_detect()
        test.dut.dstl_get_imsi()



    def run(test):

        test.log.step('Step 1: Check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

        if dev_on_mods == True:
            test.dut.dstl_collect_result('Step 1: Check device on MODS - device is available - will be deleted', True)
            test.log.step('Step 1.1: Delete device on MODS server - Start')
            test.dut.dstl_collect_result('Step 1.1: Delete device on MODS server', test.dut.dstl_delete_device(device_id))
        else:
            test.dut.dstl_collect_result('Step 1: Check device on MODS - device not available - OK', True)

        test.sleep(5)
        test.log.step('Step 2: Stop MODS agent - Start')
        test.dut.dstl_collect_result('Step 2: Stop MODS agent',
                                     test.dut.dstl_stop_mods_agent())

        test.log.info(
            "at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.info("Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        # test.log.step('Step 3: Enable bootstrap and JTM2M apns - Start')
        # test.dut.dstl_collect_result('Step 3: Enable bootstrap and JTM2M apns',
        #                              test.dut.dstl_activate_bootstrap_and_apns())

        test.log.step('Step 4: Check network registration - Start')
        test.dut.dstl_collect_result('Step 4: Check network registration',
                                         test.dut.dstl_check_network_registration())


        test.log.step('Step 5: Create/check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        #result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei)
        test.dut.dstl_collect_result('Step 5: Create/check device on MODS', result)

        test.sleep(30)

        test.log.step('Step 5.1: Check device on MODS has no group assigned - Start')
        group_ids = test.dut.dstl_get_device_group_ids_of_device(test.rest_client, device_id)
        test.log.info("group_ids: >" + str(group_ids) + "<")
        if len(group_ids) == 0:
            test.log.info('Group_ids is empty => no devicegroup assigned  -> OK ')
            result = True
        else:
            test.log.info('Group_ids is NOT empty => devicegroup assigned -> ERROR ')
            result = False
        test.dut.dstl_collect_result('Step 5.1: Check device on MODS has no devicegroup assigned', result)

        # test.log.step("Step 6: Set Download Mode to 2 - Start")
        # result = test.expect(test.dut.at1.send_and_verify_retry('AT^SRVCFG="MODS","usm/downloadMode",2',
        #                                  expect='.*OK.*', retry=5,
        #                                  sleep=30, retry_expect='.*CME ERROR.*'))
        # test.dut.dstl_collect_result('Step 6: Set Download Mode to 2', result)

        test.log.step("Step 6: Check Download Mode 2 - Start")
        result = test.expect(test.dut.at1.send_and_verify_retry('AT^SRVCFG="MODS","usm/downloadMode",2',
                                         expect='.*2.*OK.*', retry=2,
                                         sleep=5, retry_expect='.*CME ERROR.*'))
        test.dut.dstl_collect_result('Step 6: Check Download Mode 2', result)

        # test.log.step('Step 7: Set PRID - project name - Start')
        # test.dut.dstl_collect_result('Step 7: Set PRID - project name',
        #                              test.dut.dstl_set_prid_wo_agent(prid_name=test.project_name))

        test.log.step('Step 7: Check PRID - project name - Start')
        test.dut.dstl_collect_result('Step 7: Set PRID - project name',
                                     test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid"',
                                            expect='.*"UNICORN-POC".*OK.*') and result)


        test.sleep(5)
        test.log.step('Step 8: Start MODS agent - Start')
        test.dut.dstl_collect_result('Step 8: Start MODS agent',
                                     test.dut.dstl_start_mods_agent())


        test.log.step('Step 9: Check registering on MODS - Start')
        test.dut.dstl_collect_result('Step 9: Check registering on MODS',
                                     test.dut.dstl_check_registering_on_mods())

        test.sleep(30)

        test.log.step('Step 9.1: Check device on MODS has group assigned (' + test.project_name + ')- Start')
        project_id, _ = test.rest_client.find_project_by_name(test.project_name)
        test.log.info("project_id: >" + project_id + "<" + " of project: >" + test.project_name + "<")
        group_ids = test.dut.dstl_get_device_group_ids_of_device(test.rest_client, device_id)
        test.log.info("group_ids: >" + str(group_ids) + "<")
        if len(group_ids) == 0:
            test.log.info('Group_ids is empty => no devicegroup assigned  -> ERROR ')
            result = False
            test.dut.dstl_collect_result('Step 9.1: Check device on MODS has group assigned -> Error: no devicegroup assigned', result)
        else:
            test.log.info('Group_ids is NOT empty => devicegroup assigned -> OK ')
            group_id_in_project = test.dut.dstl_device_group_in_project(test.rest_client, group_ids[0], project_id)
            test.log.info("group_id_in_project: >" + str(group_id_in_project) + "<")
            test.dut.dstl_collect_result(
                'Step 9.1: Check device on MODS has group assigned (of project: >' + test.project_name + '<)',
                group_id_in_project)


        test.log.step('Step 10: Get all attributes from device - Start')
        result, dev_obj = test.dut.dstl_get_all_attributes_from_device(test.rest_client, imei)
        test.dut.dstl_collect_result('Step 10: Get all all attributes from device', result)


    def cleanup(test):

        test.dut.dstl_get_all_mods_settings()
        # test.dut.dstl_stop_mods_agent()
        # test.dut.dstl_set_prid_wo_agent(prid_name='""')
        # test.dut.dstl_set_download_mode_wo_agent(download_mode=0)
        #
        # test.dut.dstl_activate_lpa_engine()
        # test.dut.dstl_deactivate_bootstrap()
        # test.dut.dstl_set_apns()
        # test.dut.dstl_delete_cm_table()

        # test.log.info('Check device on MODS - Start')
        # imei = test.dut.dstl_get_imei()
        # test.log.info("This is your IMEI: " + imei)
        # dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)
        #
        # if dev_on_mods == True:
        #     test.log.info('Delete device on MODS server')
        #     test.dut.dstl_delete_device(device_id)

        # test.sleep(10)

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
