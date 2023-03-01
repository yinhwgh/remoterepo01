# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-331
'''
For Testcase description and the measurement point please look into the jira task
Global flow:
- setup module
- start module and subscription download
- measurement the times for define point
- write the values into vison db

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
import datetime

import json


# Global registration via https://confluence.gemalto.com/display/GMVTIB/data_download_checksum+KPI+definition needed
KPI_NAME = 'esim_provisioning_with_instant_connect'
KPI_TYPE = 'bin'
testkey = 'UNISIM01-331'
requested_rat = ''
requested_rat_name = ''
imei =''
ver = "1.2"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300

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

    def run(test):
        # Get the current time - 1 hour to find the job
        overall_result = True
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

        test.log.step('4. Report times')
        esim_perf_prov_network_registration_time = time_first_registration - time_start
        esim_perf_conn_switch_profile_download_time = time_profile_download_done - time_mods_start
        esim_perf_prov_profile_install_time = time_download_done - time_profile_download_done
        esim_perf_prov_profile_activation_time = time_registration_after_update - time_download_done
        optimal_time = time_registration_after_update - time_start

        test.log.info ('Timer\n===========')
        test.log.info ('time_start                     ' + str(time_start))
        test.log.info ('time_first_registration        ' + str(time_first_registration))
        test.log.info ('time_profile_download_done     ' + str(time_profile_download_done))
        test.log.info ('time_mods_start                ' + str(time_mods_start))
        test.log.info ('time_download_done             ' + str(time_download_done))
        test.log.info ('time_mods_update_finished      ' + str(time_mods_update_finished))
        test.log.info ('time_restart_after_update      ' + str(time_restart_after_update))
        test.log.info ('time_registration_after_update ' + str(time_registration_after_update))
        test.log.info ('time_total                     ' + str(time_total))
        test.log.info ('===========')
        test.log.info ('Values for Vision')
        test.log.info ('Over all result is >>> ' + str(overall_result))
        test.log.info ('1.  network registration time  ' + str(esim_perf_prov_network_registration_time))
        test.log.info ('2.  profile download time      ' + str(esim_perf_conn_switch_profile_download_time))
        test.log.info ('3.  profile installation time  ' + str(esim_perf_prov_profile_install_time))
        test.log.info ('4.  profile activation time    ' + str(esim_perf_prov_profile_activation_time))
        test.log.info ('5.  optimal time               ' + str(optimal_time))
        test.log.info ('6.  total time overall         ' + str(time_total - time_start))
        test.log.info ('===========')

        test.log.info('Times from Server for check if there is a gap')
        test.log.info('    last_registration_time       ' + str(last_registration_time))
        test.log.info('    time_server                  ' + str(time_server))
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

        if overall_result:
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=100)

            dstl.kpi.store(name='esim_perf_prov_network_registration_time' + requested_rat_name, type='num', device=test.dut,
                           value=esim_perf_prov_network_registration_time)
            dstl.kpi.store(name='esim_perf_prov_optimal_time' + requested_rat_name, type='num', device=test.dut,
                           value=optimal_time)
            dstl.kpi.store(name='esim_perf_prov_profile_activation_time', type='num', device=test.dut,
                           value=esim_perf_prov_profile_activation_time)
            dstl.kpi.store(name='esim_perf_prov_profile_download_time' + requested_rat_name, type='num', device=test.dut,
                           value=esim_perf_conn_switch_profile_download_time)
            dstl.kpi.store(name='esim_perf_prov_profile_install_time', type='num', device=test.dut,
                           value=esim_perf_prov_profile_install_time)
        else:
            test.log.info ('Test was not sucessful, no result timing are send to vision system')
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='bin', device=test.dut,
                           value=overall_result)
            dstl.kpi.store(name='esim_perf_prov_measurement_test' + requested_rat_name, type='num', device=test.dut,
                           value=0)

        test.log.step('x. end')

    def cleanup(test):

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.info('collect Infos if something went wrong above')
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))

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