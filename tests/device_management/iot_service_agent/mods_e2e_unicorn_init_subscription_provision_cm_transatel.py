# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-215: Use Case: Transatel profile download

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
testkey = "UNISIM01-215"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect over 2G
    """
    systart_timeout = 300
    apn_transatel = "mbb"

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        test.dut.dstl_detect()
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_stop_mods_agent()

        test.log.step(
            "Step 0.1. at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 0.2. Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "Step 0.3. Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 0.4. List all profiles in connection manager table")
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')

        test.dut.dstl_prepare_init_provsioning(prid="TRANSATEL")


    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.step("Step 1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        test.dut.dstl_check_network_registration()
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",[0379]'))

        # test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        # test.expect(
        #     re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
        #               test.dut.at1.last_response))

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

        test.log.step('Step 2: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS = JTM2M - Start')
        test.dut.dstl_collect_result('Step 5: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS = JTM2M',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)

        test.log.step('Step 3: Create/check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        test.dut.dstl_collect_result('Step 6: Create/check device on MODS', result)


        # imei = test.dut.dstl_get_imei()
        # test.log.info("This is your IMEI: " + imei)
        #
        # test.log.step("2. Create device on MODS")
        # label = test.dut.dstl_get_device_label()
        #
        # test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        # response = create_device(imei, label)
        # body = response.json()
        # log_body(body)
        # test.expect(response.status_code == 200)
        # test.expect(body != [])
        # device_id = body["id"]
        #
        # test.sleep(60)

        test.log.step("Step 4. Set Download Mode to 1")
        test.expect(test.dut.at1.send_and_verify_retry('AT^SRVCFG="MODS","usm/downloadMode",1',
                                         expect='.*OK.*', retry=5,
                                         sleep=30, retry_expect='.*CME ERROR.*'))
        #test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))

        test.sleep(15)

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
            "Step 5. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

        test.log.step("Step 6. Find the job and wait until it is finished")
        jobs = get_jobs_since_time(imei, job_type='initialConnectivityProvision',
                                   time=time_before_test).json()
        log_body(jobs)

        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        if job_status == 'failed':
            test.log.info("==> initialConnectivityProvision job failed - test will be aborted !!! ")
            test.expect(False, critical=True)

        test.dut.at1.wait_for(".*SYSSTART.*CIEV: prov,0,.*|.*SYSSTART.*SSIM READY.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)
        test.sleep(5)

        test.log.step("Step 7. at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 8. Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_init_all_mods_settings_after_switch()


        # Sometimes module does not register after SYSSTART
        # test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        # test.dut.dstl_set_sxrat()
        # test.sleep(3)
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
        max_count = 30
        while job_status != 'succeeded' and job_status != 'failed' and wait_count < max_count:
            dstl.log.com("Loop " + str(wait_count) + "/" + str(max_count))
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

        # test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        # test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3, retry_expect="CME ERROR"))
        test.sleep(5)

        test.log.step("Step 9. Check via at^susma? if Bootstrap profile is deactive and operational profile is active")
        test.expect(test.dut.at1.send_and_verify_retry('at^susma?', expect='.*OK.*', retry=15,
                                                       wait_after_send=3,
                                                       retry_expect="CME ERROR"))

        lpa_profiles = re.findall("LPA/Profiles/Info.,(\d),1,(.*)", test.dut.at1.last_response)

        for lp in lpa_profiles:

            print("Found active subscription with index " + lp[0] + " " + lp[1])

            if lp[0] == "0":
                print("Bootstrap profile is active which should not be the case " + lp[1])

        test.log.step("Step 10. Check via at^susmc? if Bootstrap profile is deactive and operational profile is active")
        test.expect(test.dut.at1.send_and_verify_retry('at^susmc?', expect='.*OK.*', retry=15,
                                                       wait_after_send=3,
                                                       retry_expect="CME ERROR"))
        last_response = test.dut.at1.last_response
        for line in last_response.splitlines():
            line_arr = line.split(",")
            if len(line_arr) > 5:
                if "ConMgr/Profile/Table" in line:
                    if line_arr[2] == "1":
                        test.log.info(
                            "Found active subscription with index " + line_arr[1] + " " + line)
                        if line_arr[1] == "0":
                            test.log.error(
                                "Bootstrap profile is active which should not be the case " + line)

        test.log.step(
            "Step 11. Check if APN of subscription occurs in response of 'at+cgdcont?' and 'AT^SNLWM2M=cfg/ext,MODS'")
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if test.apn_transatel in last_response:
            test.log.info("Your current APN is: " + test.apn_transatel)
            test.expect(True)
        else:
            test.log.info(
                "APN: " + test.apn_transatel + " of your subscription does not occur, anything went wrong")
            test.expect(False)

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        mods_apn_name = '"APN_NAME","' + test.apn_transatel + '"'
        mods_apn = '"APN","' + test.apn_transatel + '"'
        if mods_apn_name in last_response and mods_apn in last_response:
            test.log.info("Required APN: " + test.apn_transatel + " occurs in response")
            test.expect(True)
        else:
            test.log.info("Required APN: " + test.apn_transatel + " not found")
            test.expect(False)

        test.log.step(f'Step 12: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS = {test.apn_transatel} - Start')
        test.dut.dstl_collect_result(f'Step 12: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS = {test.apn_transatel}',
                                     test.dut.dstl_check_apn_and_mods_apns(apn=test.apn_transatel))

        test.log.step('Step 13: Check downloadmode 2 - Start')
        test.dut.dstl_collect_result('Step 13: Check downloadmode 2',
                                     test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                  expect='.*2.*OK.*'))

        test.log.step('Step 14: Check ping google - Start')
        test.dut.dstl_collect_result('Step 14: Check ping google',
                                         test.dut.dstl_check_google_ping())

        test.log.step(f'Step 15: Check IP address and APN in <list> command ({test.apn_transatel}) - Start')
        test.dut.dstl_collect_result(f'Step 15: Check IP address and APN in <list> command ({test.apn_transatel})',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn=test.apn_transatel))


        test.log.info(f'{40 * "*"} Get all attributes of your Device {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        test.log.info(device_id)
        device_obj = get_device_long(device_id).json()
        log_body(device_obj)
        test.expect(imei == device_obj['imei'])

    def cleanup(test):

        test.dut.dstl_print_results()

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
