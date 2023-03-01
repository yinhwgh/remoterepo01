# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-93

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

# Global registration via https://confluence.gemalto.com/display/GMVTIB/data_download_checksum+KPI+definition needed
KPI_NAME = "esim_provisioning_with_instant_connect"
KPI_TYPE = "bin"
testkey = "UNISIM01-93"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

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


        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_stop_mods_agent()

        test.dut.dstl_prepare_init_provsioning()

    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.step("Step 1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        test.dut.dstl_check_network_registration()
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",[0379]'))

        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(
            re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                      test.dut.at1.last_response))

        test.dut.dstl_get_imsi()
        
        # test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        # last_response = test.dut.at1.last_response
        # if "JTM2M" in last_response:
        #     test.log.info("APN which you are looking occurs in response")
        # else:
        #     test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))
        #
        # test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        # last_response = test.dut.at1.last_response
        # if '"APN_NAME","JTM2M"' in last_response and '"APN","JTM2M"' in last_response:
        #     test.log.info("APN which you are looking occurs in response")
        # else:
        #     test.log.info("Required APN not found, test will be terminated")
        #     test.expect(False, critical=True)

        test.log.step('Step 2: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS - Start')
        test.dut.dstl_collect_result('Step xx: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)


        test.log.step('Step 3: Create/check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        test.dut.dstl_collect_result('Step 2: Create/check device on MODS', result)

        #
        # test.log.step("Step 3. Create device on MODS")
        # label = test.dut.dstl_get_device_label()
        #
        # test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        # response = create_device(imei, label)
        # body = response.json()
        # log_body(body)
        # test.expect(response.status_code == 200)
        # test.expect(body != [])
        # device_id = body["id"]

        test.sleep(60)

        test.log.step("Step 4. Set Download Mode to 1")
        test.expect(
            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))

        test.sleep(15)

        test.log.step("Step 5. Enable URC's")
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/Ext/URC",1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))
        test.expect(test.dut.at1.send_and_verify('at^sind=simstatus,1', ".*SIND: simstatus,1,5",
                                                 wait_for="OK"))
        test.expect(
            test.dut.at1.send_and_verify('at^sind=simdata,1', ".*SIND: simdata,1", wait_for="OK"))
        test.expect(
            test.dut.at1.send_and_verify('at^sind=iccid,1', ".*SIND: iccid,1,.*", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at^sind=euiccid,1', ".*SIND: euiccid,1,""",
                                                 wait_for="OK"))
        test.expect(
            test.dut.at1.send_and_verify('AT^SIND=imsi,1', ".*SIND: imsi,1,.*", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at+cgerep=2,0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1',
                                                 expect='^SUSMC: "LPA/Engine/URC",1'))

        test.dut.at1.send_and_verify('at^srvctl="MODS","status"')
        if "service is running" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0',
                                                           retry=15,
                                                           retry_expect="service start failed"))

        test.log.info("Start KPI timer: esim_provisioning_time_with_instant_connect")
        kpi_timer_name_inst_conn = test.dut.dstl_get_kpi_timer_name_for_rat_instant_connect()
        test.kpi.timer_start(kpi_timer_name_inst_conn, device=test.dut)

        test.log.step(
            "Step 6. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

        test.log.step("Step 7. Find the job and wait until it is finished")
        jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision',
                                   time=time_before_test).json()
        log_body(jobs)

        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        if job_status == 'failed':
            test.log.info("==> initialConnectivityProvision job failed - test will be aborted !!! ")
            test.expect(False, critical=True)

        test.dut.at1.wait_for(".*SYSSTART.*CIEV: prov,0,.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)
        test.sleep(5)
        # Sometimes module does not register after SYSSTART
        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.sleep(3)
        
        test.dut.dstl_check_network_registration()
        
        test.sleep(15)

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
            test.log.info("Stop KPI timer: esim_provisioning_time_with_instant_connect")
            test.kpi.timer_stop(kpi_timer_name_inst_conn)
        else:
            test.log.info("The job NOT succeeded.")

        # test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10)))
        # test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3, retry_expect="CME ERROR"))
        test.sleep(5)

        test.log.step("Step 8. Check if Bootstrap state is deactive and subscription is active")
        test.expect(test.dut.at1.send_and_verify_retry('at^susma?', expect='.*OK.*', retry=15,
                                                       wait_after_send=3,
                                                       retry_expect="CME ERROR"))
        last_response = test.dut.at1.last_response
        for line in last_response.splitlines():
            line_arr = line.split(",")
            if len(line_arr) > 5:
                if "LPA/Profiles/Info" in line:
                    if line_arr[2] == "1":
                        test.log.info(
                            "Found active subscription with index " + line_arr[1] + " " + line)
                        if line_arr[1] == "0":
                            test.log.error(
                                "Bootstrap profile is active which should not be the case " + line)

        test.log.step(
            "Step 9. Check if APN of subscription occurs in response of 'at+cgdcont?' and 'AT^SNLWM2M=cfg/ext,MODS'")
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if "internet" in last_response:
            test.log.info("Your current APN is internet")
        else:
            test.log.info(
                "APN of your subscription does not occur, anything went wrong and test will be terminated")
            test.expect(False, critical=True)

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        if '"APN_NAME","internet"' in last_response and '"APN","internet"' in last_response:
            test.log.info("Required APN occurs in response")
        else:
            test.log.info("Required APN not found, test will be terminated")
            test.expect(False, critical=True)

        test.log.step(
            "10. Check if assigned IP address shown in at+cgpddr and at^snlwm2m=status/srv,<list> is equal")
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(
            re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                      test.dut.at1.last_response))

        test.log.step("Step 11. Call ping if internet connection is established via operational profile")
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', ".*OK.*"))
        test.sleep(20)
        test.expect(
            test.dut.at1.send_and_verify('AT^SISX=Ping,1,"www.google.com",5', expect='.*OK.*'))

        test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*')
        wait_count = 0
        max_count = 30
        while ((",registered" not in test.dut.at1.last_response) and wait_count < max_count):
            dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            # wait_count: 20 * 45 => 900 seconds => 15 minutes
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(45)
            wait_count = wait_count + 1
            dstl.log.com("wait_count: " + str(wait_count))


        test.log.step('Step xx: Get all attributes from device - Start')
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

        print("passed: " + str(test.verdicts_counter_passed))
        print("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
