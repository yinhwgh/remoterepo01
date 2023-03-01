# responsible: baris.kildi@thalesgroup.com
# location: Berlin
# test case: SRV03-3498

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
    """
    MODS: Manual Provide memory measurement test case 
    """
    systart_timeout = 300

    def setup(test):

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)


        test.log.step("Step 0.1: Create device on MODS and set read mode to maximum")
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        result, device_id = test.dut.dstl_create_device_on_mods(imei)
        test.dut.dstl_collect_result('Step 0.1: Create device on MODS and set read mode to maximum', result)

        test.sleep(10)

        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_stop_mods_agent()

        test.log.step(
            "Step 0.2: at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.dstl_show_cm_table()


        test.log.step(
            "Step 0.3: Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use which fits")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.dut.dstl_prepare_init_provsioning()

        test.dut.dstl_start_mods_agent()

        test.log.step(
            "Step 0.4: Wait until device is registered on MODS")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        test.sleep(30)

        test.log.info(f'{40 * "*"} Get all attributes of your Device and read from IoT Suite free and total memory size {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        test.log.info(device_id)
        device_obj = get_device_long(device_id).json()
        log_body(device_obj)
        test.log.step('Step 0.5: Check if IMEI occurs in REST Api response before operational profile dl - Start')
        test.expect(imei == device_obj['imei'])

        test.log.step('Step 0.6: Check free memory size before operational profile download via REST Api - Start')
        test.expect(1052 == device_obj['shadow']['reportedState']['instances']['3']['0']['10'])

        test.log.step('Step 0.7: Check total memory size before operational profile download via REST Api - Start')
        test.expect(1892 == device_obj['shadow']['reportedState']['instances']['3']['0']['21'])

        test.dut.dstl_stop_mods_agent()


    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.step("Step 1. Check if module is registered")
        test.dut.dstl_check_network_registration()
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",[0379]'))

        test.log.step('Step 2: Set Download Mode to 1 to download an operational profile - Start')
        test.dut.dstl_collect_result('Step 2: Set Download Mode to 1 to download an operational profile',
                                     test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1',
                                                                  expect='.*OK.*'))

        test.log.step("Step 3. Enable all URCs")
        test.dut.dstl_init_all_mods_settings_after_switch()

        test.dut.at1.send_and_verify('at^srvctl="MODS","status"')
        if "service is running" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0',
                                                           retry=15,
                                                           retry_expect="service start failed"))

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        test.sleep(30)
        test.log.step("Step 4. Find the job and wait until it is finished")
        jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision',
                                   time=time_before_test).json()
        log_body(jobs)

        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        if job_status == 'failed':
            test.log.info("==> initialConnectivityProvision job failed - test will be aborted !!! ")
            test.expect(False, critical=True)

        test.dut.at1.wait_for(".*SYSSTART.*CIEV: prov,0,.*", timeout=test.systart_timeout)

        test.sleep(5)


        max_count = 30
        wait_count = 0
        while jobs['numberOfElements'] == 0 and wait_count < max_count:
            dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision',
                                       time=time_before_test).json()
            log_body(jobs)
            test.sleep(10)
            wait_count = wait_count + 1
            test.log.info("wait_count:" + str(wait_count))

        test.log.info("A job was found. Checking its status ...")
        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        # Sometimes the status is suspended and gets succeeded after a while.
        wait_count = 0
        while job_status != 'succeeded' and wait_count < 30:
            test.dut.at1.send_and_verify_retry("at^smoni", expect="OK", retry=5, wait_after_send=3,
                                               retry_expect="CME ERROR")
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision',
                                       time=time_before_test).json()
            latest_job = jobs['content'][-1]
            job_status = latest_job["status"]
            log_body(jobs)
            test.sleep(30)
            wait_count = wait_count + 1

        if job_status == 'succeeded':
            test.log.info("The job succeeded.")
        else:
            test.log.info("The job NOT succeeded.")


        test.sleep(5)


        test.log.step('Step 5: Check IP address and APN in <list> command - Start')
        test.dut.dstl_collect_result('Step 5: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

        test.log.step('Step 6: Check ping google - Start')
        test.dut.dstl_collect_result('Step 6: Check ping google',
                                         test.dut.dstl_check_google_ping())


        test.log.step(
            "Step 7: Wait until device is registered on MODS")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)


        test.log.info(f'{40 * "*"} Get all attributes of your Device and read from IoT Suite free and total memory size {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        test.log.info(device_id)
        device_obj = get_device_long(device_id).json()
        log_body(device_obj)
        test.log.step('Step 8: Check if IMEI occurs in REST Api response after op prof dl - Start')
        test.expect(imei == device_obj['imei'])

        test.log.step('Step 9: Check free memory size after operational profile download via REST Api - Start')
        test.expect(1052 == device_obj['shadow']['reportedState']['instances']['3']['0']['10'])

        test.log.step('Step 10: Check total memory size after operational profile download via REST Api - Start')
        test.expect(1892 == device_obj['shadow']['reportedState']['instances']['3']['0']['21'])

    def cleanup(test):

        test.dut.dstl_print_results()

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))

        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
