# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-134 - obsolete, because new Pool/Project concept

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.identification import get_imei
import datetime
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary.write_json_result_file import *

testkey = "UNISIM01-134"

class Test(BaseTest):
    """
    Check subscription provisioning with a rule that is not active.
    Preconditions: mods_e2e_unicorn_init_new.py or mods_e2e_unicorn_init_new_cm.py executed before
    """
    rule_id = 'CI_DEACTIVATED'
    original_rule_id = 'UNICORN-POC'

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()

        test.activate_bootstrap_profile()

        test.sleep(10)
        test.dut.dstl_start_mods_agent()

        test.imei = test.dut.dstl_get_imei()
        _, test.device_id = test.dut.dstl_create_device_on_mods(test.imei)

        test.dut.dstl_init_all_mods_settings()

    def run(test):
        # 1. Assing rule to DUT
        # 3. Check if created rule is not active
        # 4. GET created job
        # 5. Expect created job failed

        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.dut.dstl_stop_mods_agent()

        test.dut.at1.send_and_verify(f'AT^SRVCFG="MODS","usm/prid",{test.rule_id}', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')

        test.sleep(20)

        test.dut.dstl_start_mods_agent()
        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.dut.dstl_check_network_registration()

        test.sleep(30)

        test.dut.dstl_check_registering_on_mods()

        test.check_job_status(time_before_test)

    def activate_bootstrap_profile(test):
        test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Engine",1', expect='^SUSMA: "LPA/Engine",2', retry=10,
                                           sleep=3, retry_expect='^SUSMA: "LPA/Engine",1')

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,0' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is deactive")
        else:
            test.log.error("Bootstrap is somehow active - Something went wrong")
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')

        test.sleep(5)

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is now active")
        else:
            test.log.error("Bootstrap is somehow NOT active - Something went wrong")

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

    def check_job_status(test, time_before_test):
        jobs = get_jobs_since_time(test.imei, job_type='initialConnectivityProvision', time=time_before_test).json()
        log_body(jobs)

        wait_count = 0
        while jobs['numberOfElements'] == 0 and wait_count < 10:
            jobs = get_jobs_since_time(test.imei, job_type='initialConnectivityProvision', time=time_before_test).json()
            log_body(jobs)
            test.sleep(10)
            wait_count = wait_count + 1
            test.log.info(wait_count)

        test.log.info("A job was found. Checking its status ...")
        latest_job = jobs['content'][-1]
        job_status = latest_job['status']

        test.expect('failed' in job_status)
        test.expect('Rule not activated yet' in latest_job['reason'])

    def cleanup(test):
        # 6. Unassign dummy rule from DUT
        test.dut.dstl_stop_mods_agent()

        test.dut.at1.send_and_verify(f'AT^SRVCFG="MODS","usm/prid",{test.original_rule_id}', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

        test.dut.dstl_deactivate_bootstrap()

        test.dut.dstl_start_mods_agent()

        test.dut.dstl_stop_mods_agent()

        test.dut.dstl_delete_device(test.device_id)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
