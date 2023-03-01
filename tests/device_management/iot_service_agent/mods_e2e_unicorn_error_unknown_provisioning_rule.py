# responsible: karsten.labuske@thalesgroup.com
# location: Berlin
# Test case: UNISIM01-133

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
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *
import json
import datetime

testkey = "UNISIM01-133"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 240

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()
        test.log.step("0. Get all rules, APN profiles and all subscriptions via REST Api")
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        if not device_id:
            test.log.info("Device with your imei will be created")
        else:
            request = delete_device(device_id)
            response = request.json()
            log_body(response)

        # test.log.info(f'{40 * "*"} Get all Rules {40 * "*"}')
        # rules = get_rules()
        # log_body(rules.json())
        # test.expect(rules.status_code == 200)
        #
        # test.log.info(f'{40 * "*"} Get all APN Profiles {40 * "*"}')
        # response = get_apn_profiles()
        # apn_profiles = response.json()
        # log_body(apn_profiles)
        # test.expect(response.status_code == 200)

        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()

        test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Engine",1', expect='^SUSMA: "LPA/Engine",2', retry=10,
                                           sleep=3, retry_expect='^SUSMA: "LPA/Engine",1')

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,0' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is deactive")
        else:
            test.log.error("Bootstrap is somehow active - Something went wrong")
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')

        test.sleep(5)

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is now active")
        else:
            test.log.error("Bootstrap is somehow NOT active - Something went wrong")

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.step("1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.dut.dstl_check_network_registration()

        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))

        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                              test.dut.at1.last_response))

        test.dut.dstl_get_imsi()
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if "JTM2M" in last_response:
            test.log.info("APN which you are looking occurs in response")
        else:
            test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        if '"APN_NAME","JTM2M"' in last_response and '"APN","JTM2M"' in last_response:
            test.log.info("APN which you are looking occurs in response")
        else:
            test.log.info("Required APN not found, test will be terminated")
            test.expect(False, critical=True)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.step("2. Create device on MODS")
        label = 'Unicorn E2E Tests'

        test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        response = create_device(imei, label)
        body = response.json()
        log_body(body)
        test.expect(response.status_code == 200)
        test.expect(body != [])
        device_id = body["id"]

        test.log.step("3. Set Provisioning Rule ID to something not existing in the MODS database")
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",IreallyDontExist', expect='.*OK.*'))

        test.log.step("4. Set Download Mode to 1")
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))

        test.sleep(5)

        test.dut.dstl_start_mods_agent()

        test.log.step("5. Check if Bootstrap state is active")
        test.expect(test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*'))

        # test.log.step("6. Restart module and start Engine")
        # test.dut.dstl_restart()
        # test.dut.at1.send_and_verify('at^susma="LPA/Engine",1', expect='.*OK.*')

        test.log.step("6. Enable URC's")
        test.dut.dstl_init_all_mods_settings()

        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.dut.dstl_check_network_registration()
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",7'))
        test.sleep(5)

        test.log.step(
            "7. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*')
        wait_count = 0
        while ",registered" not in test.dut.at1.last_response and wait_count < 30:
            # wait_count: 20 * 45 => 900 seconds => 15 minutes
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(45)
            wait_count = wait_count + 1

        test.log.step("8. Find the job and wait until it is finished")
        jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision', time=time_before_test).json()
        log_body(jobs)

        wait_count = 0
        while jobs['numberOfElements'] == 0 and wait_count < 30:
            jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision', time=time_before_test).json()
            log_body(jobs)
            test.sleep(10)
            wait_count = wait_count + 1

        test.log.info("A job was found. Checking its status ...")
        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        # Sometimes the status is suspended and gets succeeded after a while.
        wait_count = 0
        while job_status != 'failed' and wait_count < 30:
            test.expect(test.dut.at1.send_and_verify('at^smoni', wait_for='OK'))
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision', time=time_before_test).json()
            latest_job = jobs['content'][-1]
            job_status = latest_job["status"]
            log_body(jobs)
            test.sleep(30)
            wait_count = wait_count + 1

        test.log.info("The job failed as expected.")
        test.expect('failed' == latest_job["status"])
        test.expect(imei == latest_job["imei"])
        test.expect('Failed to book subscription' == latest_job["reason"])


        test.log.step('Step 9: Get all attributes from device - Start')
        result, dev_obj = test.dut.dstl_get_all_attributes_from_device(test.rest_client, imei)
        test.dut.dstl_collect_result('Step xx: Get all all attributes from device', result)

        # test.log.info(f'{40 * "*"} Get all attributes of your Device {40 * "*"}')
        # devices = get_devices().json()
        # device_id = get_device_id(devices, imei)
        # test.log.info(device_id)
        # device_obj = get_device_long(device_id).json()
        # log_body(device_obj)
        # test.expect(imei == device_obj['imei'])

    def cleanup(test):
        test.dut.dstl_deactivate_bootstrap()
        test.dut.dstl_stop_mods_agent()
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*'))

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
