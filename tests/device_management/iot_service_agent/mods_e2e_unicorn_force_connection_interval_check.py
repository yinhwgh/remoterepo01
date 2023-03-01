# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-343
'''
Force Connection interval to be changed back to 1 job at server site is assumed to be running
Check this by restarting the client every hour. (e,g Unicorn 9B client has this restart value
for Con Interval at 60 sec).
Check that server forces client +each time+ back to 24 hours.
Target: *Understand if we can force an load reduction at Aidon without FW update*
of some 40K-150K devices especially after *Server maintenance updates*
Test
- Step x check the connection interval, it muts be the default value
- Step x download a subscription to the module
- Step x check the connection interval, must be set to 24h from the server
- step x restart the module, check the connection interval, must be set to 24h from the server
- loop start (run more the 24h)
    - Step x check the connection interval, must be set to 24h from the server
    - wait 1h
    - restart client

    NOTE: has to be adapted: get connection time from server
                            get setting from connection interval

'''

import unicorn
import re
import time
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
#KPI_NAME = 'esim_provisioning_with_instant_connect'
#KPI_TYPE = 'bin'
testkey = 'UNISIM01-343'
#requested_rat = ''
#requested_rat_name = ''
imei =''
ver = "1.0"
default_connection_interval = 86400
connection_time_after_restart = 86400


class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300

    def set_connection_interval(test, connection_time):
        result = False

        result = test.expect(test.dut.at1.send_and_verify('at^snlwm2m=cfg,MODS,/1/0/1,' + str(connection_time) + ';^snlwm2m=cfg/object,MODS,/1/0,new', 'OK', timeout=10))
        result = test.check_connection_interval(connection_time)

        return (result)

    def check_connection_interval(test, request_time=86400):
        connection_interval = 0
        result=False
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=cfg/object,MODS,/1', 'OK', timeout=10))
        res = test.dut.at1.last_response
        m = re.search('/1/0/1.*"', res)
        if m:
            found = m.group(0)
            [dummy1, dummy2] = found.split(',')
            connection_interval = int(re.sub('"', '', dummy2))
            if connection_interval ==  request_time:
                test.expect(True)
                test.log.info('Requested connection interval is:   >' + str(request_time) + '<')
                test.log.info('connection interval from module is: >' + str(connection_interval) + '<')
                result = True
            else:
                test.expect(False)
                test.log.info('Requested connection interval is:   >' + str(request_time) + '<')
                test.log.info('connection interval from module is: >' + str(connection_interval) + '<')
        else:
            test.log.info('no connection interval found in output')
        return (result)

    def set_urc(test):
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
        return(True)

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') Ver: ' + str(ver) + ' - Start *****')

        global requested_rat
        global requested_rat_name
        global imei
        global default_connection_interval
        global connection_time_after_restart

        test.rest_client = IotSuiteRESTClient()

        test.rat_original = test.rat
        test.dut.dstl_detect()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        #test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        # set default connection intervall for SW Versions if different from default
        test.dut.at1.send_and_verify('at^cicret=swn')
        res = test.dut.at1.last_response
        if '300_048E' in res:
            default_connection_interval=86400
        elif '300_048D' in res:
            default_connection_interval=8640
        elif '032_UNICORN9B' in res:
            default_connection_interval =60
            connection_time_after_restart = 60
        else:
            default_connection_interval = 0
        test.log.info ('set default connection time to: ' + str(default_connection_interval))


        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        # test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        # devices = get_devices().json()
        # device_id = get_device_id(devices, imei)
        # if not device_id:
        #     test.log.info("Device with your imei will be created")
        #     test.log.step("x. Create device on MODS")
        #     label = test.dut.dstl_get_device_label()
        #
        #     test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        #     response = create_device(imei, label)
        #     body = response.json()
        #     log_body(body)
        #     test.expect(response.status_code == 200)
        #     test.expect(body != [])
        #     device_id = body["id"]
        #
        #     test.sleep(60)
        # else:
        #     test.log.info("Device with your imei exist, nothing to do")
        #     # request = delete_device(device_id)
        #     # response = request.json()
        #     # log_body(response)

        test.log.step("Step 0.1. Create device on MODS")
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei)
        test.expect(result)

        test.sleep(10)


        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

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
        global connection_time_after_restart
        global default_connection_interval
        overall_result = True

        stepline = '\n===================================================='
        test.log.step ('Step 1: down a subscription to the module' + stepline)
        test.log.step ('Step 1.1: prepare the module' + stepline)
        test.log.info('Check device on MODS - Start')
        test.log.info("This is your IMEI: " + imei)
        dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,0', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,0', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","stop"', wait_for='OK', timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+cfun=1,1'))
        test.expect(test.dut.at1.wait_for(".*SYSSTART.*", timeout=120))

        test.log.step('Step 1.2: activate the URC' + stepline)
        test.expect(test.set_urc())
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
        test.expect(test.check_connection_interval(default_connection_interval))

        test.log.step('Step 1.3: set download mode 1' + stepline)
        # check connection interval als subfunction
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', wait_for='OK', timeout=10))
        overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result

        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))

        test.log.step('Step 1.4: start mods service' + stepline)
        test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","start"', wait_for='OK', timeout=30))
        overall_result = test.dut.at1.wait_for('Load Bound Profile Package done', timeout=900.0, greedy=False) and overall_result
        overall_result = test.dut.at1.wait_for('"LPA/Profiles/Download",0x0000', timeout=900.0, greedy=False) and overall_result
        overall_result = test.expect(test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*", timeout=600)) and overall_result
        overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result

        test.log.step('Step 1.5: module restart was done check IP' + stepline)
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        ip_server = test.dut.at1.last_response
        test.log.step('Step 6: Check the IP Adresses' + stepline)
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

        ################################################################

        one_hour_wait_time = 3600 # eigentlich 3600 sec
        server_job_repeat_time = 86400 # 86400

        if overall_result:
            test.log.step('Step 2: Until now evrything is ok, Loop Test can start' + stepline)
            test.expect(test.check_connection_interval(default_connection_interval))

            d = test.dut.dstl_get_last_connected_date()
            test.log.info(
                    'Server last connection date: >' + str(d) + '< ')


            outer_loop_count = 3 # test runs outer_loop_count * server_job_repeat_time
            for n in range (outer_loop_count):
                '''
                - connection interval auf 5 minuten setzen
                - warten
                - der server muß das connection interval auf 1 Tag setzen
                - device infos vom server lesen (stimmt alles?)
                - Module nach 1h neu starten
                - connnection interval check
                    - 9B hat wieder 60s
                    - alle anderen sollten weiterhin 1 Tag haben
                - check mit server settings
                '''

                test.log.info ('Loop ' + str(n) + ' of ' + str(outer_loop_count) )
                test.log.step('Step 3.' + str(n + 1) + ' start' + stepline)
                test.log.info ('set connection interval to 5 minuten (300 sec)' + stepline)
                overall_result = test.expect(test.set_connection_interval(300))

                test.log.info ('wait for the server job in background')
                test.log.info ('The server must set the interval back to ' + str(server_job_repeat_time) + ' sec)' + stepline)
                test.sleep(server_job_repeat_time)
                test.sleep(one_hour_wait_time)


                # to do: Zeit vom Server lesen - Johann?
                # test.log.info ('Read device infos from server, must 1 Day' + stepline)
                # d = test.dut.dstl_get_connection_time()
                # if d == 86400:
                #     test.log.info('Server has set back the connection interval on the server to 1 day')
                #     overall_result = overall_result + True
                # else:
                #     test.log.info('Server has NOT set back the connection interval on the server to 1 day')
                #     test.log.info('connection Interval from module is :>' + str(d) + '<')
                #     overall_result = overall_result + False


                test.log.info ('Read device infos from module, must 1 Day' + stepline)
                overall_result = test.expect(test.check_connection_interval(86400))
                test.log.info('wait 1 h and restart the module after that time' + stepline)

                test.dut.dstl_restart()
                test.sleep(60)
                overall_result = test.expect(test.check_connection_interval(default_connection_interval)) + overall_result

                test.log.info ('Read device infos from Server, must 1 Day' + stepline)
                d = test.dut.dstl_get_connection_time()
                if d == connection_time_after_restart:
                    test.log.info('Server has set back the connection interval to >' + str(connection_time_after_restart) + '< sec')
                    overall_result = overall_result + True
                else:
                    test.log.info('Server has NOT set back the connection interval to 1 day')
                    test.log.info('the requeste value shall be >' + str(connection_time_after_restart) + '< sec')
                    test.log.info('Server Interval from Server is :>' + str(d) + '<')
                    overall_result = overall_result + False

        else:
            test.log.info ('Test was not sucessful, no result timing are send to vision system')
            test.expect(False)

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