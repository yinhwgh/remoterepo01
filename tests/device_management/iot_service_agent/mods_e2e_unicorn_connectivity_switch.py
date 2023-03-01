# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# Test case: UNISIM01-94

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.identification import get_imei
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
testkey = "UNISIM01-94"


class Test(BaseTest):
    sysstart_timeout = 300

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        # test.dut.dstl_restart()
        # test.sleep(30)

    def run(test):
        # Target device properties.
        imei = test.dut.dstl_get_imei()

        # Properties for connectivity switch job.
        name = f"Automation Connectivity Switch ({imei})"
        description = "Test REST api"
        target_issuer = {
            "countryCode": "354",
            "issuerCode": "01"
        }

        # Job schedule properties.
        current_time = test.dut.dstl_get_mods_time(format=False)
        schedule_from = f'{(current_time + datetime.timedelta(seconds=30)).isoformat()}Z'
        schedule_to = f'{(current_time + datetime.timedelta(minutes=10)).isoformat()}Z'

        test.log.step("Step 1. Enable URC's")
        test.dut.dstl_init_all_mods_settings()

        test.log.step(f'Step 2. Check number of profiles')
        number_of_profiles_before = len(test.get_profiles())
        test.log.info(f'Number of profiles: {number_of_profiles_before}')

        test.log.step(f'Step 3. Create connectivity switch')
        job_resp = create_connectivity_switch(name, description, target_issuer)
        log_body(job_resp.json())
        test.expect(job_resp.status_code == 200)

        test.log.info("Start KPI timer: esim_provisioning_time_connectivity_switch")
        kpi_timer_name_conn_switch = test.dut.dstl_get_kpi_timer_name_for_rat_conn_switch()
        test.kpi.timer_start(kpi_timer_name_conn_switch, device=test.dut)

        test.log.step(f'Step 4. Get target device')
        target_resp = get_device_with_imei(imei)
        log_body(target_resp.json())
        test.expect(target_resp.status_code == 200)

        test.log.step(f'Step 5. Create job target')
        job_id = job_resp.json()['id']
        target_id = target_resp.json()['id']
        job_resp = create_job_target(job_id, target_id)
        log_body(job_resp.json())
        test.expect(job_resp.status_code == 200)

        test.log.step(f'Step 6. Schedule job')
        job_resp = schedule_job(job_id, schedule_from, schedule_to)
        log_body(job_resp.json())
        test.expect(job_resp.status_code == 200)

        test.log.step(f'Step 7. Get job until its status is running')
        wait_count = 0
        while (job_resp.json()['status'] == 'scheduled') and wait_count < 30:
            job_resp = get_job(job_id)
            test.log.info(f"Job status: {job_resp.json()['status']}")
            test.sleep(10)
            wait_count = wait_count + 1

        log_body(job_resp.json())
        test.expect(job_resp.json()['status'] == 'running')

        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*CIEV: prov,0,.*",
                              timeout=test.sysstart_timeout)

        test.log.step("Step 8. Enable URCs after SYSSTART")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")
        test.sleep(3)
        test.dut.dstl_init_all_mods_settings_after_switch()

        test.dut.dstl_check_network_registration()

        # test.log.step('Step xx: Check IP address and APN in <list> command - Start')
        # test.dut.dstl_collect_result('Step xx: Check IP address and APN in <list> command',
        #                                  test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

        test.sleep(5)

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
        while (job_resp.json()['status'] == 'running') and wait_count < max_count:
            test.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            job_resp = get_job(job_id)
            test.log.info(f"Job status: {job_resp.json()['status']}")
            test.sleep(10)
            wait_count = wait_count + 1

        log_body(job_resp.json())
        test.expect(job_resp.json()['status'] == 'ended')

        test.log.step(f'Step 10. Check if job succeeded')
        targets = get_job_targets(job_id)
        log_body(targets.json())
        test.expect(targets.status_code == 200)

        target_resp = find_job_target(targets.json(), target_id)
        log_body(target_resp)
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

        test.log.step('Step 13: Check IP address and APN in <list> command - Start')
        test.dut.dstl_collect_result('Step 13: Check IP address and APN in <list> command',
                                     test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

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
