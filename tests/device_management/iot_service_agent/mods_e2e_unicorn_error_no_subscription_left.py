# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-135

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.identification import get_imei
import datetime
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary.write_json_result_file import *
testkey = "UNISIM01-135"

class Test(BaseTest):
    """
    Error Case: Subscription provisioning without available subscriptions
    note: PRID is set to TELENOR, where no subscriptions are available
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(10)

        test.dut.dstl_activate_lpa_engine()
        test.dut.dstl_activate_bootstrap_and_apns()

        # test.dut.dstl_start_mods_agent()

        test.log.info('*** Create/check device on MODS - ****')
        test.imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + test.imei)
        result, test.device_id = test.dut.dstl_create_device_on_mods(test.rest_client, test.imei, group_id=test.group_id)



        test.dut.dstl_init_all_mods_settings()

    def run(test):
        # Verify that there are no subscriptions available.
        # If there are subscriptions test will be aborted.
        #test.expect(test.no_subscriptions_available(), critical=True)

        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.dut.dstl_stop_mods_agent()

        test.dut.at1.send_and_verify(f'AT^SRVCFG="MODS","usm/prid","TELENOR"',
                                     expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='.*OK.*')

        test.sleep(10)

        test.dut.dstl_start_mods_agent()
        test.dut.dstl_check_network_registration()

        test.sleep(30)

        test.dut.dstl_check_registering_on_mods()

        test.check_job_status(time_before_test)

    def check_job_status(test, time_before_test):
        jobs = get_jobs_since_time(test.imei, job_type='initialConnectivityProvision',
                                   time=time_before_test).json()
        log_body(jobs)

        wait_count = 0
        while jobs['numberOfElements'] == 0 and wait_count < 10:
            jobs = get_jobs_since_time(test.imei, job_type='initialConnectivityProvision',
                                       time=time_before_test).json()
            log_body(jobs)
            test.sleep(10)
            wait_count = wait_count + 1
            test.log.info(wait_count)

        test.log.info("A job was found. Checking its status ...")
        latest_job = jobs['content'][-1]
        job_status = latest_job['status']
        job_reason = latest_job['reason']

        test.expect('failed' in job_status)
        #test.expect('No more subscription available' in job_reason)
        # because of MODSNG-3204 reason could also be: "reason": "Failed to book subscription"
        test.expect('No more subscription available' == latest_job["reason"] or
                     'Failed to book subscription' == latest_job["reason"])

    def no_subscriptions_available(test):
        get_subscriptions_resp = get_subscriptions()
        subscriptions = find_subscriptions_by_field(get_subscriptions_resp.json(),
                                                    field_name='status',
                                                    field_value='available')
        test.log.info(subscriptions)

        return test.expect(len(subscriptions) == 0)

    def cleanup(test):
        #test.dut.dstl_delete_device(test.device_id)
        test.dut.dstl_set_download_mode("0")
        test.dut.dstl_deactivate_bootstrap()
        test.dut.dstl_stop_mods_agent()
        # test.create_all_subscriptions(file_name="iccids_siminn.txt")

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()