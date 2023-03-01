# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-332
# E2E Performance: connectivity switch
'''
#############################################################
Idea is to have a script purely based on URCs to check how long the provisioning time really is.
KPI definition will be added when finally discussed.
KPI's have to be created per RAT (2G, CatM, NB-IoT)

For Testcase description and the measurement point please look into the jira task
Global flow:
- setup module
- start module and subscription download
- if finish creat a switch job on server
- restart the mods server for trigger job start from server
- measurement the times for define points
- write the values into vison db

- The Testcase use for the first subscription download the TC
  mods_e2e_unicorn_init_subscription_provision_measurement.py and report the kpi values for the normal subscription
  download

The TC can be used with a Parameter, if no parameter was set the defautl value "catm1" is used:
--requested_rat=<rat>
allowed rat values are:
2g catm1 nbiot
'''

import unicorn
import re
import time
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.miscellaneous.mods_e2e_unicorn_support import dstl_get_last_connected_date
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
import datetime

import json


# Global registration via https://confluence.gemalto.com/display/GMVTIB/data_download_checksum+KPI+definition needed
KPI_NAME = 'todo_esim_provisioning_with_instant_connect'
KPI_TYPE = 'bin'
testkey = 'UNISIM01-332'
requested_rat = ''
requested_rat_name = ''
imei =''
ver = "1.0"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300


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

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') Ver: ' + str(ver) + ' - Start *****')

        global requested_rat
        global requested_rat_name
        global imei

        test.rat_original = test.rat
        test.require_parameter('requested_rat', default = 'catm1')
        requested_rat = test.requested_rat
        test.log.info('Requested RAT via parameter is >' + str(requested_rat) + '<')
        test.log.info('original RAT via parameter is  >' + str(test.rat_original) + '<')
        if requested_rat == "":
            test.log.info('no requested RAT, use default value catm1')
            test.log.inof('Allowed values are "catm1" "2g" "nbiot" ')
            requested_rat = 'catm1'

        if 'catm1' in requested_rat:
            test.rat = 'catm1'
            requested_rat_name = '_cat_m1'
        if '2g' in requested_rat:
            test.rat = '2G'
            requested_rat_name = '_2g'
        if 'nbiot' in requested_rat:
            test.rat = 'nbiot'
            requested_rat_name = '_nb_iot'

        test.dut.dstl_detect()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()

        test.log.step("0.1 Get all rules, APN profiles and all subscriptions via REST Api")
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        if not device_id:
            test.log.info("Device with your imei will be created")
            test.log.step("x. Create device on MODS")
            label = test.dut.dstl_get_device_label()

            test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
            response = create_device(imei, label)
            body = response.json()
            log_body(body)
            test.expect(response.status_code == 200)
            test.expect(body != [])
            device_id = body["id"]

            test.sleep(60)
        else:
            test.log.info("Device with your imei exist, nothing to do")
            # request = delete_device(device_id)
            # response = request.json()
            # log_body(response)

        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()

        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_stop_mods_agent()

        test.log.step(
            "0.2 at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("0.3 Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "0.4 Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("0.5 List all profiles in connection manager table")
        test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table"')

        #test.dut.dstl_prepare_init_provsioning() # cg set to mutch so we make it step by step
        test.dut.at1.send_and_verify('at^SUSMA="LPA/Engine",1', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('at^SUSMA="LPA/Profiles/Info"', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid","UNICORN-POC"', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('AT+creg=2')
        test.dut.at1.send_and_verify('AT+cgreg=2')
        test.dut.at1.send_and_verify('At&w')

        test.log.step('0.6 Step some settings for connectivity switch')
        test.rest_client = IotSuiteRESTClient()
        test.device_group_name = test.get('iot_suite_group_name')
        test.factory_assignment_pool_name = test.get('iot_suite_factory_assignment_pool')
        test.field_assignment_pool_name = test.get('iot_suite_field_assignment_pool')

    def run(test):
        # Get the current time - 1 hour to find the job
        overall_result = True
        global imei
        #time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.info('Check device on MODS - Start')
        test.log.info("This is your IMEI: " + imei)
        dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

        # time measurement for network registration make no senece if the module restart every time
        test.log.step('1. Measure the network registration time')
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,0', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,0', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","stop"', wait_for='OK', timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+cfun=1,1'))
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=120))
        time_start = time.time()
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', wait_for='OK', timeout=10))

        overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result
        time_first_registration = time.time()
        time_server = test.dut.dstl_get_mods_time(format=True)
        #first_registration_time = test.dut.dstl_get_last_connected_date(device_id)

        test.log.step('2. Measure the time for download')
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
        time_mods_start = time.time()
        #time1a = test.dut.dstl_get_last_connected_date(device_id)
        test.dut.at1.send_and_verify('at^srvctl="MODS","start"', wait_for='OK', timeout=30)

        overall_result = test.dut.at1.wait_for('Load Bound Profile Package done', timeout=900.0, greedy=False) and overall_result
        time_profile_download_done = time.time()

        overall_result = test.dut.at1.wait_for('"LPA/Profiles/Download",0x0000', timeout=900.0, greedy=False) and overall_result
        time_download_done = time.time()
        # 9b overall_result = test.dut.at1.wait_for('"MODS","update","finished"', timeout=300.0, greedy=False) and overall_result
        time_mods_update_finished = time.time()
        overall_result = test.expect(test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*", timeout=600)) and overall_result
        # 9b overall_result = test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=600)) and overall_result
        time_restart_after_update = time.time()
        overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result
        time_registration_after_update = time.time()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        ip_server = test.dut.at1.last_response
        test.log.step('3. Check the IP Adresses')

        wait_count=0
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
        time_total = time.time()

        last_registration_time = test.dut.dstl_get_last_connected_date(device_id)

        test.log.step('4. Report times for the subscription download')
        esim_perf_prov_network_registration_time = time_first_registration - time_start
        esim_perf_conn_switch_profile_download_time = time_profile_download_done - time_mods_start
        esim_perf_prov_profile_install_time = time_download_done - time_profile_download_done
        esim_perf_prov_profile_activation_time = time_registration_after_update - time_download_done
        optimal_time = time_registration_after_update - time_start

        #first_registration_time_obj = datetime.datetime.strptime(first_registration_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        last_registration_time_obj = datetime.datetime.strptime(last_registration_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        time_server_obj = datetime.datetime.strptime(time_server, '%Y-%m-%dT%H:%M:%S.%fZ')

        delta_modstime2 = last_registration_time_obj - time_server_obj
        if 'day' in str(delta_modstime2):
            test.log.info('Delta time is more then a day, not valid')
        else:
            time_list = str(delta_modstime2).split(':')
            dif = int(time_list[0]) * 60 * 60 + int(time_list[1]) * 60 + float(time_list[2])
            test.log.info('    optimal time server 2        ' + str(delta_modstime2))
            test.log.info('    optimal time server 2        ' + str(dif))
            check_dif_time = time_total - time_first_registration
            test.log.info('    optima time from script      ' + str(check_dif_time))
        test.log.info('===========')

        ###############################################################################
        if overall_result:
            # now can the conectivity switch start
            test.log.step('5. Start the connectivity switch time measurement')
            # Target device properties.
            imei = test.dut.dstl_get_imei()

            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
            test.expect(
                test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))

            # Properties for connectivity switch job.
            name = f"Automation Connectivity Switch ({imei})"
            description = "Test REST api"
            target_pool_id, target_pool = test.rest_client.find_pool_by_name(test.field_assignment_pool_name)
            test.expect(target_pool_id, critical=True, msg="Target pool not found")

            # Job schedule properties.
            current_time = test.dut.dstl_get_mods_time(format=False)
            schedule_from = f'{(current_time + datetime.timedelta(seconds=30)).isoformat()}Z'
            schedule_to = f'{(current_time + datetime.timedelta(minutes=10)).isoformat()}Z'

            test.log.step("Step 6. Enable URC's")
            # test.dut.dstl_init_all_mods_settings()

            test.log.step(f'Step 7. Check number of profiles')
            number_of_profiles_before = len(test.get_profiles())
            test.log.info(f'Number of profiles: {number_of_profiles_before}')

            test.log.step(f'Step 8. Create connectivity switch')
            job_resp = test.rest_client.create_connectivity_switch(name, description,
                                                                   target_pool_id=target_pool_id, to_json=True)
            test.expect(job_resp)

            test.log.info("Start KPI timer: esim_provisioning_time_connectivity_switch")
            kpi_timer_name_conn_switch = test.dut.dstl_get_kpi_timer_name_for_rat_conn_switch()
            test.kpi.timer_start(kpi_timer_name_conn_switch, device=test.dut)

            test.log.step(f'Step 9. Get target device')
            target_resp = test.rest_client.get_device_with_imei(imei, to_json=True)
            test.expect(target_resp)

            test.log.step(f'Step 10. Create job target')
            job_id = job_resp['id']
            target_id = target_resp['id']
            job_resp = test.rest_client.create_job_target(job_id, target_id, to_json=True)
            test.expect(job_resp)

            test.log.step(f'Step 11. Schedule job')
            job_resp = test.rest_client.schedule_job(job_id, schedule_from, schedule_to, to_json=True)
            test.expect(job_resp)

            test.log.info('*** workaround for connection interval set to 1 day - Start ***')
            test.dut.dstl_stop_mods_agent()
            test.sleep(10)
            test.dut.dstl_start_mods_agent()
            test.log.info('*** workaround for connection interval set to 1 day - End ***')
            time_cs_start = time.time()

            test.log.step(f'Step 12. Get job until its status is running')
            wait_count = 0
            while (job_resp['status'] == 'scheduled') and wait_count < 30:
                job_resp = test.rest_client.get_job(job_id, to_json=True)
                test.log.info(f"Job status: {job_resp['status']}")
                test.sleep(10)
                wait_count = wait_count + 1
            test.expect(job_resp['status'] == 'running')

            #############################################################################
            overall_result_cs = test.dut.at1.wait_for('Load Bound Profile Package done', timeout=900.0,
                                                   greedy=False) and overall_result
            time_cs_profile_download_done = time.time()

            overall_result_cs = test.dut.at1.wait_for('"LPA/Profiles/Download",0x0000', timeout=900.0,
                                                   greedy=False) and overall_result
            time_cs_download_done = time.time()
            # 9b overall_result = test.dut.at1.wait_for('"MODS","update","finished"', timeout=300.0, greedy=False) and overall_result
            time_cs_mods_update_finished = time.time()
            overall_result_cs = test.expect(
                test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*", timeout=600)) and overall_result
            # 9b overall_result = test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=600)) and overall_result
            time_cs_restart_after_update = time.time()
            overall_result_cs = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result
            time_cs_registration_after_update = time.time()
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            ip_server = test.dut.at1.last_response
            test.log.step('13. Check the IP Adresses')

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
                        overall_result_cs = overall_result and False
                else:
                    test.sleep(5)
                wait_count = wait_count + 1
            time_cs_total = time.time()

            last_registration_time = test.dut.dstl_get_last_connected_date(device_id)
            #############################################################################

            test.log.step('14. Report times connectivity switch')
            esim_perf_cs_conn_switch_profile_download_time = time_cs_profile_download_done - time_cs_start
            esim_perf_cs_prov_profile_install_time = time_cs_download_done - time_cs_profile_download_done
            esim_perf_cs_prov_profile_activation_time = time_cs_registration_after_update - time_cs_download_done
            optimal_time_cs = time_cs_registration_after_update - time_cs_start

            test.log.step(f'Step 15. Get job until its status is ended')
            wait_count = 0
            max_count = 30
            while (job_resp['status'] == 'running') and wait_count < max_count:
                test.log.com("Loop " + str(wait_count) + "/" + str(max_count))
                job_resp = test.rest_client.get_job(job_id, to_json=True)
                test.log.info(f"Job status: {job_resp['status']}")
                test.sleep(10)
                wait_count = wait_count + 1

            test.expect(job_resp['status'] == 'ended')

            test.log.step(f'Step 16. Check if job succeeded')
            targets = test.rest_client.get_job_targets(job_id, to_json=True)
            test.expect(targets)

            target_resp = test.rest_client.find_job_target(targets, target_id)
            test.expect(target_resp['status'] == 'succeeded')
            if target_resp['status'] == 'succeeded':
                test.log.info("Stop KPI timer: esim_provisioning_time_connectivity_switch")
                test.kpi.timer_stop(kpi_timer_name_conn_switch)

            test.log.step(f'Step 17. Check if number of profiles have been increased by one')
            if len(test.get_profiles()) > 0:
                number_of_profiles_after = len(test.get_profiles())
                test.log.info(f'Number of profiles: {number_of_profiles_after}')
                test.expect(number_of_profiles_before + 1 == number_of_profiles_after)
            else:
                test.log.info(f'Number of profiles: could not be found')
                test.expect(False)

            test.log.step('Step 18: Check registration on MODS - Start')
            test.dut.dstl_collect_result('Step 19: Check registration on MODS',
                                         test.dut.dstl_check_registering_on_mods())

            test.log.step('Step 19: Check IP address and APN in <list> command - Start')
            test.dut.dstl_collect_result('Step 19: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet", list_retry=2))

            test.dut.dstl_show_cm_table()

        test.log.step('print all timing result')
        test.log.step('Step 20: Print all timing results and transfer to KPI system')
        if overall_result:
            test.log.info('timing of the normal subscription download')
            test.log.info('Timer\n===========')
            test.log.info('time_start                     ' + str(time_start))
            test.log.info('time_first_registration        ' + str(time_first_registration))
            test.log.info('time_profile_download_done     ' + str(time_profile_download_done))
            test.log.info('time_mods_start                ' + str(time_mods_start))
            test.log.info('time_download_done             ' + str(time_download_done))
            test.log.info('time_mods_update_finished      ' + str(time_mods_update_finished))
            test.log.info('time_restart_after_update      ' + str(time_restart_after_update))
            test.log.info('time_registration_after_update ' + str(time_registration_after_update))
            test.log.info('time_total                     ' + str(time_total))
            test.log.info('===========')
            test.log.info('Values for Vision')
            test.log.info('Over all result is >>> ' + str(overall_result))
            test.log.info('1.  network registration time  ' + str(esim_perf_prov_network_registration_time))
            test.log.info('2.  profile download time      ' + str(esim_perf_conn_switch_profile_download_time))
            test.log.info('3.  profile installation time  ' + str(esim_perf_prov_profile_install_time))
            test.log.info('4.  profile activation time    ' + str(esim_perf_prov_profile_activation_time))
            test.log.info('5.  optimal time               ' + str(optimal_time))
            test.log.info('6.  total time overall         ' + str(time_total - time_start))
            test.log.info('===========')

            test.log.info('Times from Server for check if there is a gap')
            test.log.info('    last_registration_time       ' + str(last_registration_time))
            test.log.info('    time_server                  ' + str(time_server))
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=100)
            dstl.kpi.store(name='esim_perf_prov_network_registration_time' + requested_rat_name, type='num',
                           device=test.dut,
                           value=esim_perf_prov_network_registration_time)
            dstl.kpi.store(name='esim_perf_prov_optimal_time' + requested_rat_name, type='num', device=test.dut,
                           value=optimal_time)
            dstl.kpi.store(name='esim_perf_prov_profile_activation_time', type='num', device=test.dut,
                           value=esim_perf_prov_profile_activation_time)
            dstl.kpi.store(name='esim_perf_prov_profile_download_time' + requested_rat_name, type='num',
                           device=test.dut,
                           value=esim_perf_conn_switch_profile_download_time)
            dstl.kpi.store(name='esim_perf_prov_profile_install_time', type='num', device=test.dut,
                           value=esim_perf_prov_profile_install_time)
        else:
            test.log.info('Test of normal subscription downlaod was not sucessful, no result timing are send to vision system')
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=0)

        test.log.step('Step 21: Print all timing results for connectivity switch and transfer to KPI system')
        if overall_result_cs:
            test.log.info('timing of the subscription switch')
            test.log.info('Timer\n=======================================================')
            test.log.info('time_cs_profile_download_done     ' + str(time_cs_profile_download_done))
            test.log.info('A: time_cs_mods_start                ' + str(time_cs_start))
            test.log.info('   time_cs_download_done             ' + str(time_cs_download_done))
            test.log.info('B: time_cs_mods_update_finished      ' + str(time_cs_mods_update_finished))
            test.log.info('C: time_cs_restart_after_update      ' + str(time_cs_restart_after_update))
            test.log.info('D: time_cs_registration_after_update ' + str(time_cs_registration_after_update))
            test.log.info('E: time_cs_total                     ' + str(time_cs_total))
            test.log.info('===========')
            test.log.info('Values for Vision')
            test.log.info('Over all result is >>> ' + str(overall_result))
            test.log.info('2.  profile cs download time      ' + str(esim_perf_cs_conn_switch_profile_download_time))
            test.log.info('3.  profile cs installation time  ' + str(esim_perf_cs_prov_profile_install_time))
            test.log.info('4.  profile cs activation time    ' + str(esim_perf_cs_prov_profile_activation_time))
            test.log.info('5.  optimal cs time               ' + str(optimal_time_cs))
            test.log.info('6.  total time cs overall         ' + str(time_cs_total - time_cs_start))
            test.log.info('===========')
            ####################################################################################

            test.log.info('esim_perf_conn_switch_measurement_test' + requested_rat_name +  ' ' + str(overall_result))
            test.log.info('esim_perf_conn_switch_measurement_test' + requested_rat_name + ' 100')
            test.log.info('esim_perf_conn_switch_optimal_time' + requested_rat_name + ' ' +str(optimal_time))
            test.log.info('esim_perf_conn_switch_profile_activation_time ' + str(esim_perf_cs_prov_profile_activation_time))
            test.log.info('esim_perf_conn_switch_profile_download_time' + requested_rat_name + ' '  + str(esim_perf_cs_conn_switch_profile_download_time))
            test.log.info('esim_perf_conn_switch_profile_install_time' + str(esim_perf_cs_prov_profile_install_time))

            dstl.kpi.store(name='esim_perf_conn_switch_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_conn_switch_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=100)
            dstl.kpi.store(name='esim_perf_conn_switch_optimal_time' + requested_rat_name, type='num', device=test.dut,
                           value=optimal_time)
            dstl.kpi.store(name='esim_perf_conn_switch_profile_activation_time', type='num', device=test.dut,
                           value=esim_perf_cs_prov_profile_activation_time)
            dstl.kpi.store(name='esim_perf_conn_switch_profile_download_time' + requested_rat_name, type='num',
                           device=test.dut,
                           value=esim_perf_cs_conn_switch_profile_download_time)
            dstl.kpi.store(name='esim_perf_conn_switch_profile_install_time', type='num', device=test.dut,
                           value=esim_perf_cs_prov_profile_install_time)
        else:
            test.log.info('Test of connection switch was not sucessful, no result timing are send to vision system')
            dstl.kpi.store(name='esim_perf_conn_switch_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_conn_switch_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=0)

        test.log.step('x. end')

    def cleanup(test):

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.info('collect Infos if something went wrong above')
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))

        test.log.info('chage RAT value if needed')
        if test.rat != test.rat_original:
            test.rat = test.rat_original
            test.log.info('set rat back to original rat: >' + test.rat + '<')
            test.dut.dstl_set_radio_band_settings()
            test.dut.dstl_restart()
            test.sleep(10)
        else:
            test.log.info('RAT value not change and is >' + test.rat_original + '<')

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()