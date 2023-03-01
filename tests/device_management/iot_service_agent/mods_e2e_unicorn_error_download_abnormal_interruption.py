# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-283

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
testkey = "UNISIM01-283"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300
    kpi_name_registration_after_startup = ""

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.kpi_nw_registration_power_consumption = "none"
        test.mc_test4_available = False

        test.dut.dstl_detect()

        try:
            test.mctest_present = test.dut.devboard.send_and_verify("MC:VBATT", "OK")
            if test.mctest_present:
                test.dut.dstl_switch_off_at_echo(serial_ifc=0)
                test.dut.dstl_switch_off_at_echo(serial_ifc=1)
                if 'MC-Test4' in test.dut.dstl_get_dev_board_version():
                    test.mc_test4_available = True
        except Exception as e:
            test.mc_test4_available = False


        test.log.step("Step 0.1 Get all rules, APN profiles and all subscriptions via REST Api")
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

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()
#        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.kpi_name_registration_after_startup = test.dut.dstl_get_kpi_name_for_registration_time_after_startup()
        test.log.info("Start KPI timer: " + test.kpi_name_registration_after_startup)
        test.kpi.timer_start(test.kpi_name_registration_after_startup, device=test.dut)
        if test.mc_test4_available:
            test.kpi_name_registration_power_consumption = test.dut.dstl_get_kpi_name_for_registration_power_consumption()
            test.log.info(f'Start KPI NW scan power consumption: {test.kpi_name_registration_power_consumption}')
            test.dut_devboard.send_and_verify("mc:ccmeter=on", expect=".*OK.*")


        test.sleep(5)
        test.dut.dstl_stop_mods_agent()

        test.log.step(
            "Step 0.2. at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 0.3. Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "Step 0.4 Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 0.5. List all profiles in connection manager table")
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')

        test.dut.dstl_prepare_init_provsioning()


    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'
        test.rest_client = IotSuiteRESTClient()

        test.log.step("Step 1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        result = test.dut.dstl_check_network_registration()
        if result == True:
            test.log.info("Stop KPI timer: " + test.kpi_name_registration_after_startup)
            test.kpi.timer_stop(test.kpi_name_registration_after_startup)
            if test.mc_test4_available:
                test.log.info(f'Stop and save KPI NW scan power consumption: {test.kpi_name_registration_power_consumption}')
                test.dut_devboard.send_and_verify("mc:ccmeter=off", expect=".*OK.*")
                test.dut_devboard.send_and_verify("mc:ccmeter=read", expect=".*OK.*")
                power_value = re.findall(r'.*W= *(\d{1,4}\.\d{1,4})mAh.*',
                                     test.dut.devboard.last_response, re.I | re.S)
                if power_value and result:
                    dstl.test.kpi_store(name=test.kpi_name_registration_power_consumption, value=power_value[0], type='num', device=test.dut)


        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",[0379]'))

        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(
            re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                      test.dut.at1.last_response))

        test.dut.dstl_get_imsi()

        test.log.step('Step 2: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS - Start')
        test.dut.dstl_collect_result('Step xx: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)

        test.log.step('Step 3: Create/check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        test.dut.dstl_collect_result('Step 2: Create/check device on MODS', result)


        test.log.step("Step 4. Set Download Mode to 1")
        test.expect(
            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))

        test.sleep(15)

        test.dut.at1.send_and_verify('at^srvctl="MODS","status"')
        if "service is running" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0',
                                                           retry=15,
                                                           retry_expect="service start failed"))

        test.dut.at1.wait_for('"LPA/Profiles/Download",0x0000', timeout=900.0, greedy=False)
        test.dut.dstl_restart()
        overall_result = True
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
        test.dut.dstl_set_real_time_clock()
        test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', 'CME ERROR: operation temporary not allowed', timeout=10))
        # test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        # test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","start"', wait_for='OK', timeout=30))
        overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        ip_server = test.dut.at1.last_response
        test.log.step('3. Check the IP Adresses')
        wait_count = 0
        while wait_count < 30:
            test.log.info('Loop >' + str(wait_count) + '<')
            test.dut.at1.send_and_verify("at+cgpaddr")
            if 'CGPADDR: 1,' in test.dut.at1.last_response:
                wait_count = 100
                ip = re.findall(r'.*CGPADDR:.*,"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})".*',
                                test.dut.at1.last_response, re.I | re.S)
                if ip[0] in ip_server:
                    test.expect(True)
                else:
                    test.expect(False)
                    test.log.info('IP Adresses are not equal between snlwm and cgpaddr')
                    overall_result = overall_result and False
            else:
                test.sleep(5)
            wait_count = wait_count + 1
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*'))
        test.log.info('########################################################')
        if overall_result:
            test.expect(True)
            test.log.info('subscription download works fine after download abnormal interruption')
        else:
            test.expect(False)
            test.log.info('subscription download is NOT working after download abnormal interruption')
        test.log.info('########################################################')


    def cleanup(test):

        test.dut.dstl_print_results()

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))
        test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
                       type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
