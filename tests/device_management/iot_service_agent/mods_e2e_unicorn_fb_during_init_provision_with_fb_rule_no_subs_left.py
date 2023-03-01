# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-223 - Error Case: Fallback without matching subscription available

import unicorn
import re
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
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

testkey = "UNISIM01-223"


class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.rest_client = IotSuiteRESTClient()
        test.device_group_name = test.get('iot_suite_group_name')
        test.factory_assignment_pool_name = test.get('iot_suite_factory_assignment_pool')
        #test.field_assignment_pool_name = test.get('iot_suite_field_assignment_pool')
        test.field_assignment_pool_name = "NO-Telenor AS-UNISIM01-223"
        test.log.info("field_assignment_pool_name" + test.field_assignment_pool_name )

        test.log.step("Step 0.1 Prepare device")
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        device = test.rest_client.get_device_with_imei(imei, to_json=True)
        if not device:
            test.log.info("Device with your imei will be created")
        else:
            request = test.rest_client.delete_device(device['id'])
            test.expect(request)

        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()

        test.log.step('Step 0.2 find device group and pools')
        test.group_id, _ = test.rest_client.find_device_group_by_name(test.device_group_name)
        test.expect(test.group_id, critical=True, msg="Group not found")

        test.factory_assignment_pool_id, _ = test.rest_client.find_pool_by_name(test.factory_assignment_pool_name)
        test.expect(test.factory_assignment_pool_id, critical=True, msg="Factory assignment pool not found")

        test.field_assignment_pool_id, _ = test.rest_client.find_pool_by_name(test.field_assignment_pool_name)
        test.expect(test.field_assignment_pool_id, critical=True, msg="Field assignment pool not found")

        test.log.step('Step 0.3 create test project')
        test.project_name = f'TEST_{testkey}'
        device_group = {
            'id': test.group_id
        }
        factory_assignment = [{
            'type': 'SINGLE',
            'pools': [
                {
                    'id': test.factory_assignment_pool_id
                }
            ]
        }]
        on_field_assignment = [{
            'type': 'SINGLE',
            'pools': [
                {
                    'id': test.field_assignment_pool_id
                }
            ]
        }]
        test.project = test.rest_client.create_project(name=test.project_name, device_group=device_group, to_json=True,
                                                       log_level=LogLevel.FULL,
                                                       factoryAssignment=factory_assignment,
                                                       onFieldAssignment=on_field_assignment)
        test.expect(test.project, critical=True, msg='Could not create project')

        test.log.step(
            "Step 0.2 at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step(
            "Step 0.3 Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
            "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "Step 0.4 Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify(
                'at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("Step 0.5 List all profiles in connection manager table")
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')

        test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Engine",1',
                                           expect='^SUSMA: "LPA/Engine",2', retry=10,
                                           sleep=3, retry_expect='.*^SUSMA: "LPA/Engine",1.*|.*ERROR.*')

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,0' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is deactive")
        else:
            test.log.error("Bootstrap is somehow active - Something went wrong")

        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify(f'AT^SRVCFG="MODS","usm/prid",{test.project_name}', expect='.*OK.*')
        else:
            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",ELISA', expect='.*OK.*')

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')

        test.sleep(5)

        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
            test.log.info("Looks fine your bootstrap profile is now active")
        else:
            test.log.error("Bootstrap is somehow NOT active - Something went wrong")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

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

        test.log.step('Step 2: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS - Start')
        test.dut.dstl_collect_result('Step xx: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS',
                                     test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.step("Step 3. Create device on MODS")
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        test.expect(result)

        test.sleep(10)

        test.log.com('*** set susmc parameters ***')
        fallback_timeout = 120
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=fallback_timeout)

        test.log.step("Step 5. Set Download Mode to 1")
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

        test.dut.at1.wait_for(".*SYSSTART.*CIEV: prov,0,.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)
        test.sleep(5)

        test.log.com('*** Force network registration to unavailable network ***')
        #test.dut.at1.send_and_verify('at+cops=1,2,26295', expect='CME ERROR', timeout=150)
        test.dut.at1.send_and_verify_retry('at+cops=1,2,26295',
                                         expect='.*CME ERROR.*', retry=5,
                                         sleep=30, retry_expect='.*SIM busy.*', timeout=150)

        test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*SSIM READY.*', timeout=(fallback_timeout + 60))

        test.log.step('Step 7: Check if bootstrap profile is activated - Start')
        # Expect boostrap profile is activated
        _, profiles = test.dut.dstl_get_profile_info()
        bootstrap_profile = profiles[0]
        result = (bootstrap_profile['profile_state'] == '1')
        test.dut.dstl_collect_result('Step 7: Check state of bootstrap profile (=1)', result)

        test.log.step('Step 8: Check APNs in cgdcont? - Start')
        test.dut.dstl_collect_result('Step 8: Check APNs in cgdcont? (=JTM2M)',
                                     test.dut.at1.send_and_verify('at+cgdcont?',
                                                                  expect='.*JTM2M.*OK.*'))

        test.log.step('Step 9: Check downloadmode 3 - Start')
        test.dut.dstl_collect_result('Step 9: Check downloadmode 3',
                                     test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"',
                                                                  expect='.*3.*OK.*'))

        rat = test.dut.dstl_get_rat()
        test.dut.at1.send_and_verify(f'at+cops=0,,,{rat}', expect='OK', timeout=150)
        test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*', timeout=120)

        test.log.step(
            'Step 10: Check if FallbackConnectivityProvision job has failed/ended (No more subscription available/failedTarget=1) - Start')
        test.dut.dstl_collect_result(
            'Step 10: Check if FallbackConnectivityProvision job has failed/ended (No more subscription available/failedTarget=1)',
            test.dut.dstl_check_job_fallback_no_more_subscription_available(test.rest_client, imei, time_before_test))

    def cleanup(test):
        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_activate_operational_profile_and_apns_with_cm(op_prof_id=1, apn="internet")
        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_set_download_mode_wo_agent(download_mode=2)
        test.dut.dstl_start_mods_agent()
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()
        test.rest_client.delete_project(test.project['id'], True)

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
