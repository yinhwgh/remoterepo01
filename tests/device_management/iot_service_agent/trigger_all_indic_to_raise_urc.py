# responsible: baris.kildi@thalesgroup.com
# location: Berlin
# test case: SRV03-4772 - LW-M2M client: Trigger all indications to raise this URC


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
import datetime
import re
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *

# Global registration via https://confluence.gemalto.com/display/GMVTIB/data_download_checksum+KPI+definition needed
KPI_NAME = "esim_connectivity_switch"
KPI_TYPE = "bin"
testkey = "SRV03-4772"


class Test(BaseTest):
    sysstart_timeout = 300

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.log.com('***** Testcase: ' + test.test_file + ' (SRV03-4772) - Start *****')

        test.require_parameter('target_country_code', default='354')
        test.require_parameter('target_issuer_code', default='01')

        test.rest_client = IotSuiteRESTClient()
        test.device_group_name = test.get('iot_suite_group_name')
        test.factory_assignment_pool_name = test.get('iot_suite_factory_assignment_pool')
        test.field_assignment_pool_name = test.get('iot_suite_field_assignment_pool')

        test.dut.dstl_detect()

    def run(test):
        # Target device properties.
        imei = test.dut.dstl_get_imei()

        # Properties for connectivity switch job.
        name = f"Automation Connectivity Switch ({imei})"
        description = "Test REST api"
        target_pool_id, target_pool = test.rest_client.find_pool_by_name(test.field_assignment_pool_name)
        test.expect(target_pool_id, critical=True, msg="Target pool not found")

        # Job schedule properties.
        current_time = test.dut.dstl_get_mods_time(format=False)
        schedule_from = f'{(current_time + datetime.timedelta(seconds=30)).isoformat()}Z'
        schedule_to = f'{(current_time + datetime.timedelta(minutes=10)).isoformat()}Z'

        test.log.step("Step 1. Enable URC's")
        test.dut.dstl_init_all_mods_settings()
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC= "LPA/Procedure/URC",1', wait_for="OK", timeout=10))

        test.log.step(f'Step 2. Check number of profiles')
        number_of_profiles_before = len(test.get_profiles())
        test.log.info(f'Number of profiles: {number_of_profiles_before}')

        test.log.step(f'Step 3. Create connectivity switch')
        job_resp = test.rest_client.create_connectivity_switch(name, description,
                                                               target_pool_id=target_pool_id, to_json=True)
        test.expect(job_resp)

        test.log.info("Start KPI timer: esim_provisioning_time_connectivity_switch")
        kpi_timer_name_conn_switch = test.dut.dstl_get_kpi_timer_name_for_rat_conn_switch()
        test.kpi.timer_start(kpi_timer_name_conn_switch, device=test.dut)

        test.log.step(f'Step 4. Get target device')
        target_resp = test.rest_client.get_device_with_imei(imei, to_json=True)
        test.expect(target_resp)

        test.log.step(f'Step 5. Create job target')
        job_id = job_resp['id']
        target_id = target_resp['id']
        job_resp = test.rest_client.create_job_target(job_id, target_id, to_json=True)
        test.expect(job_resp)

        test.log.step(f'Step 6. Schedule job')
        job_resp = test.rest_client.schedule_job(job_id, schedule_from, schedule_to, to_json=True)
        test.expect(job_resp)

        test.log.info('*** workaround for connection interval set to 1 day - Start ***')
        test.dut.dstl_stop_mods_agent()
        test.sleep(10)
        test.dut.dstl_start_mods_agent()
        test.log.info('*** workaround for connection interval set to 1 day - End ***')

        test.log.step(f'Step 7. Get job until its status is running')
        wait_count = 0
        while (job_resp['status'] == 'scheduled') and wait_count < 30:
            job_resp = test.rest_client.get_job(job_id, to_json=True)
            test.log.info(f"Job status: {job_resp['status']}")
            test.sleep(10)
            wait_count = wait_count + 1

        test.expect(job_resp['status'] == 'running')

        test.expect(test.dut.at1.wait_for_strict('^SUSMA: "LPA/Procedure/URC",1,0,1000',
                                                 timeout=test.sysstart_timeout))

        test.expect(test.dut.at1.wait_for_strict('^SUSMA: "LPA/Procedure/URC",2,0,2000',
                                                 timeout=test.sysstart_timeout))

        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*CIEV: prov,0,.*",
                              timeout=test.sysstart_timeout)

        test.log.step("Step 8. Enable URCs after SYSSTART")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")
        test.sleep(3)
        test.dut.dstl_init_all_mods_settings_after_switch()

        test.expect(test.dut.at1.send_and_verify('AT^SUSMC= "LPA/Procedure/URC",1', wait_for="OK", timeout=10))

        test.dut.dstl_check_network_registration()

        # test.log.step('Step xx: Check IP address and APN in <list> command - Start')
        # test.dut.dstl_collect_result('Step xx: Check IP address and APN in <list> command',
        #                                  test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

        test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*')
        wait_count = 0
        while ("deregistered" in test.dut.at1.last_response or
               "registering" in test.dut.at1.last_response) and wait_count < 20:
            test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*')
            test.sleep(45)
            wait_count = wait_count + 1

        test.log.step(f'Step 9. Get job until its status is ended')
        wait_count = 0
        max_count = 30
        while (job_resp['status'] == 'running') and wait_count < max_count:
            test.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            job_resp = test.rest_client.get_job(job_id, to_json=True)
            test.log.info(f"Job status: {job_resp['status']}")
            test.sleep(10)
            wait_count = wait_count + 1

        test.expect(job_resp['status'] == 'ended')

        test.log.step(f'Step 10. Check if job succeeded')
        targets = test.rest_client.get_job_targets(job_id, to_json=True)
        test.expect(targets)

        target_resp = test.rest_client.find_job_target(targets, target_id)
        test.expect(target_resp['status'] == 'succeeded')
        if target_resp['status'] == 'succeeded':
            test.log.info("Stop KPI timer: esim_provisioning_time_connectivity_switch")
            test.kpi.timer_stop(kpi_timer_name_conn_switch)

        test.log.step(f'Step 11. Check if number of profiles have been increased by one')
        if len(test.get_profiles()) > 0:
            number_of_profiles_after = len(test.get_profiles())
            test.log.info(f'Number of profiles: {number_of_profiles_after}')
            test.expect(number_of_profiles_before + 1 == number_of_profiles_after)
        else:
            test.log.info(f'Number of profiles: could not be found')
            test.expect(False)

        test.log.step('Step 12: Check registration on MODS - Start')
        test.dut.dstl_collect_result('Step 12: Check registration on MODS',
                                     test.dut.dstl_check_registering_on_mods())

        test.dut.dstl_show_cm_table()

        test.log.step('Step 13: Check IP address and APN in <list> command - Start')
        test.dut.dstl_collect_result('Step 13: Check IP address and APN in <list> command',
                                     test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet", list_retry=2))

        test.log.step('Step 14: Get iccid which you want to delete in next step')
        test.dut.at1.send_and_verify('at^susma="LPA/Profiles/Info"', expect='.*OK.*')
        all_profiles = test.dut.at1.last_response
        all_profiles = all_profiles.split("^SUSMA: ")
        get_needed_profile = all_profiles[2]
        iccid = get_needed_profile.split("\"")
        iccid = iccid[3]

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        #iccids = test.dut.dstl_get_all_iccids(test.rest_client, imei)
        subscription_ids = test.dut.dstl_get_all_subscription_ids(test.rest_client, imei)

        test.log.info(subscription_ids)
        delete_disab_sub = (subscription_ids[1])

        test.log.step('Step 15: Add workaround due to connection interval 24h value')
        test.dut.dstl_stop_mods_agent()

        test.dut.dstl_delete_subscription_only_on_mods(subscription_id=delete_disab_sub, iccid=iccid)

        test.dut.dstl_start_mods_agent()

        test.expect(test.dut.at1.wait_for_strict('^SUSMA: "LPA/Procedure/URC",3,0,3000',
                                                 timeout=180))

        test.expect(test.dut.at1.wait_for_strict('Read pending notifications',
                                                 timeout=180))

        test.sleep(60)

        # test.dut.at1.send_and_verify_retry('at^susma="LPA/Profiles/Delete",2', expect="OK")



        test.log.step('Step 15: Check if all notifications have been sen')
        test.dut.dstl_collect_result('Step 15: Send pending notifications',
                                     test.dut.dstl_send_pending_notifications())

        test.log.step('Step 16: Create already deleted subscription back on MODS - Start')
        test.dut.dstl_collect_result('Step 16: Create already deleted subscriptions back on MODS',
                                     test.dut.dstl_create_single_subscription(test.rest_client, iccid,
                                                                              pool_id = "5b706ec4-75f7-460d-a702-97dafeb522e3"))

        test.dut.dstl_show_cm_table()


    def get_profiles(test):
        # Wait before sending SUSMA to make sure module does not return empty strings.
        # test.sleep(30)
        result = test.dut.at1.send_and_verify_retry('at^susma?',
                                                    expect='.*SUSMA:.*"LPA/Engine",2.*OK.*',
                                                    retry=5,
                                                    sleep=60, retry_expect='.*OK.*|.*ERROR.*')
        if result:
            return [sub for sub in test.dut.at1.last_response.splitlines()
                    if "LPA/Profiles/Info" in sub]
        else:
            return 0

    def cleanup(test):

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.dut.dstl_print_results()

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()