# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-xxx
# Robustness: switch off the module in after different staates
# UNISIM01-xxx - Robustness: network lost in the middle of sequence -> during init after URC "CIEV: simstatus,4"
#   point 1: during init after URC "CIEV: simstatus,4"
# UNISIM01-xxx - Robustness: network lost in the middle of sequence -> 5 sec after MODS start
#   point 2: 5 sec after at^srvctl="MODS","start"
# UNISIM01-300 - Robustness: network lost in the middle of sequence -> after "Authenticate server done"
#   point 3: after "Authenticate server done"
# UNISIM01-302 - Robustness: network lost in the middle of sequence -> after "PPR conditions check done"
#   point 4: after "PPR conditions check done"
# UNISIM01-x - Robustness: network lost in the middle of sequence -> after at^snlwm2m=status/srv,<list>
#   point 5: after at^snlwm2m=status/srv,<list>
# UNISIM01-303 - Robustness: network lost in the middle of sequence -> after "Get Bound Profile Package done"
#   point 6: after "Get Bound Profile Package done"
# UNISIM01-304 - Robustness: network lost in the middle of sequence -> after "Load Bound Profile Package done -
#                Profile download successful"
#   point 7: after "Load Bound Profile Package done - Profile download successful"
# UNISIM01-305 - Robustness: network lost in the middle of sequence -> after "Send PIR notification to server done"
#   point 8: after "Send PIR notification to server done"
# UNISIM01-x - Robustness: network lost in the middle of sequence -> after "LPA/Profiles/Download",0x0000
#   point 9: after "LPA/Profiles/Download",0x0000
# point 10: after ^SRVACT: "MODS","update","finished"
# UNISIM01-x -
# point 11: after "CIEV: simstatus,5
# UNISIM01-297 - Robustness: network lost in the middle of sequence -> after "Activation code decoded"
#   point 12: after Activation code decoded
# UNISIM01-298 - Robustness: network lost in the middle of sequence -> after "Initiate authentication done"
#   point 13: after "Initiate authentication done"
# UNISIM01-299 - Robustness: network lost in the middle of sequence -> after "SM-DP+ address checking done"
#   point 14: after ,"SM-DP+ address checking done"
# UNISIM01-301 - Robustness: network lost in the middle of sequence -> after "Authenticate client done"
#   point 15: after ,"Authenticate client done"
# UNISIM01-306 Robustness: network lost in the middle of sequence -> after "Clear PIR notification done"
#   point 16: after "Clear PIR notification done"
# point : after


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
from dstl.auxiliary.devboard.devboard import *

import json
import datetime

# Global registration via https://confluence.gemalto.com/display/GMVTIB/data_download_checksum+KPI+definition needed
KPI_NAME = "esim_provisioning_with_instant_connect"
KPI_TYPE = "bin"
testkey = 'UNISIM01-297 UNISIM01-298 UNISIM01-299 UNISIM01-300 UNISIM01-301 UNISIM01-302 UNISIM01-303 UNISIM01-304 ' \
          'UNISIM01-305 UNISIM01-306'
network_lost_at_point = 0
test_abort = False
imei=''

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300
    kpi_name_registration_after_startup = ""

    def network_sxrat(test,rat):
        return test.expect(test.dut.at1.send_and_verify('at^sxrat=' + str(rat) + ',' + str(rat), 'OK', timeout=10))

    def network_lost(test,current_point, timer=0.0):
        global network_lost_at_point
        global test_abort
        global imei
        test.log.info('network lost point at: >' + str(network_lost_at_point) + '< current point: >'+ str(current_point) + '< Timer: >' + str(timer) + '<')
        if network_lost_at_point == current_point:
            test.log.info('Wait time before network lost is: >' + str(timer) + '<')
            test.sleep(timer)
            test.log.info ('Network lost simulation via sxrat')
            result = test.network_sxrat(8)
            test.log.info ('wait 20 sec after Network off')
            test.sleep(20)
            test.log.info ('check if a subscription exist for these IMEI')
            iccids_before_restart = test.dut.dstl_get_all_iccids(test.rest_client,imei)
            if len (iccids_before_restart)>=1:
                test.log.info ('There is one or more subscription on the Server for these module, please check')
                test.log.info ('There is one or more subscription on the Server for these module, please check')
            else:
                test.log.info('No subscription on the Server for these module')
            test.sleep(1)
            result = test.expect(test.dut.dstl_turn_on_igt_via_dev_board()) and result
            result = test.network_sxrat(7)
            test.sleep(5)
            test_abort = True
            overall_result = True
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
            test.dut.dstl_set_real_time_clock()
            test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', wait_for='OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","start"', wait_for='OK', timeout=30))
            overall_result = test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False) and overall_result
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
            test.expect(test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*'))
            test.log.info ('########################################################')
            if overall_result:
                test.expect(True)
                test.log.info ('subscription download works fine after network lost')
            else:
                test.expect(False)
                test.log.info('subscription download is NOT working after network lost')
            test.log.info ('########################################################')
        else:
            result = False
        return(result)

    def module_start(test):
        return ()


    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        global network_lost_at_point
        global test_abort
        global imei
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        # read cmd-line parameter, but if local parameter is used, it's overrule
        if network_lost_at_point == 0:
            network_lost_at_point = test.network_lost_at_point
        if network_lost_at_point == 0 or network_lost_at_point>20:
            test.expect(False)
        test.log.info ('Run the Test and make the network lost break at step: >' + str(network_lost_at_point) + '<')
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

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

        if network_lost_at_point == 1:
            # for Step1 the device must create here
            # for all other cases later
            test.log.step('Step 0.1a: Create/check device on MODS (network lost1 extra)- Start')
            test.log.info("This is your IMEI: " + imei)
            result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
            test.dut.dstl_collect_result('Step 0.1b: Create/check device on MODS', result)

        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()

        test.sleep(10)
        test.dut.at1.send_and_verify('at+cclk?')
        test.dut.devboard.send_and_verify('mc:vbatt=3500')
        test.sleep(10)

        test.dut.at1.send_and_verify('at+cclk?')
        if ('CCLK: "80' in test.dut.at1.last_response):
            test.log.info ('CCLK ERROR: Time is reset after restart')
            test.expect(False)
            test.dut.dstl_set_real_time_clock()
        else:
            test.expect(True)

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

        # test.dut.dstl_prepare_init_provsioning()
        t1 = test.thread(test.dut.dstl_prepare_init_provsioning)
        t2 = test.thread(test.network_lost, 1, 3.10)  # network lost point 1
        t1.join()
        t2.join()

        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort ')

    def run(test):

        global network_lost_at_point
        global test_abort
        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        # read cmd-line parameter, but if local parameter is used, it's overrule
        if network_lost_at_point == 0:
            network_lost_at_point = test.network_lost_at_point
        if network_lost_at_point == 0 or network_lost_at_point>20:
            test.expect(False)
        test.log.info ('Run the Test and make the network lost at step: >' + str(network_lost_at_point) + '<')
        # test.expect(test.network_lost(1))


        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

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

        # test.log.step('Step 3: Create/check device on MODS - Start')
        # imei = test.dut.dstl_get_imei()
        # test.log.info("This is your IMEI: " + imei)
        # result, device_id = test.dut.dstl_create_device_on_mods(imei)
        # test.dut.dstl_collect_result('Step 2: Create/check device on MODS', result)
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
            # test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
            #                                                expect='^SRVCTL: "MODS","start",0',
            #                                                retry=15,
            #                                                retry_expect="service start failed"))
            t1 = test.thread(test.dut.at1.send_and_verify_retry, 'at^srvctl="MODS","start"',
                             expect='^SRVCTL: "MODS","start",0',retry=15,
                             retry_expect="service start failed")
            t2 = test.thread(test.network_lost, 2, 5) # network lost point 2
            t1.join()
            t2.join()
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')


        test.log.info("Start KPI timer: esim_provisioning_time_with_instant_connect")
        kpi_timer_name_inst_conn = test.dut.dstl_get_kpi_timer_name_for_rat_instant_connect()
        test.kpi.timer_start(kpi_timer_name_inst_conn, device=test.dut)

        test.log.step(
            "Step 5. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        test.dut.at1.wait_for('Activation code decoded', timeout=120.0,greedy=False)
        test.network_lost(12, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        test.dut.at1.wait_for('Initiate authentication done', timeout=120.0,greedy=False)
        test.network_lost(13, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        test.dut.at1.wait_for('SM-DP+ address checking done', timeout=120.0,greedy=False)
        test.network_lost(14, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        test.dut.at1.wait_for('Authenticate server done', timeout=120.0,greedy=False)
        test.network_lost(3, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        test.dut.at1.wait_for('Authenticate client done', timeout=120.0,greedy=False)
        test.network_lost(15, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        test.dut.at1.wait_for('PPR conditions check done', timeout=120.0,greedy=False)
        test.network_lost(4, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))

            test.network_lost(5, 10)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

            test.dut.at1.wait_for('Get Bound Profile Package done', timeout=30.0,greedy=False)
            test.network_lost(6, 0)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
            test.dut.at1.wait_for('Load Bound Profile Package done', timeout=30.0,greedy=False)
            test.network_lost(7, 0)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
            test.dut.at1.wait_for('Send PIR notification to server done', timeout=30.0,greedy=False)
            test.network_lost(8, 0)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
            test.dut.at1.wait_for('Clear PIR notification done', timeout=30.0,greedy=False)
            test.network_lost(16, 0)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
            test.dut.at1.wait_for('LPA/Profiles/Download",0x0000', timeout=30.0,greedy=False)
            test.network_lost(9, 0)
            if test_abort:  # is set in network_lost
                # abort full testcase, no cleanup etc.
                raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
            #test.sleep(30)
            # repeat status read, because the first response is not in the response anymore
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
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

        test.dut.at1.wait_for('SRVACT: "MODS","update","finished"', timeout=test.systart_timeout)
        test.network_lost(10, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')
        test.dut.at1.wait_for(".*SYSSTART AIRPLANE.*", timeout=test.systart_timeout)
        test.dut.at1.wait_for(".*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)
        test.expect(test.dut.at1.send_and_verify('at^sind=simstatus,1', expect='.*OK.*'))
        test.dut.at1.wait_for('CIEV: simstatus,5', timeout=test.systart_timeout)
        test.network_lost(11, 0)
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            test.sleep(120)
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
                else:
                    test.sleep(5)
                wait_count = wait_count + 1

            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')

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
        max_count = 30
        wait_count = 0
        while job_status != 'succeeded' and wait_count < max_count:
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
                                                       sleep=30,
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


        test.log.step("Step 12. Check if downloadmode is set to 2")
        test.expect(
            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='^SRVCFG: "MODS","usm/downloadMode","2"'))


        test.log.step('Step 13: Send pending notifications again - Start')
        # test.dut.dstl_collect_result('Step xx: Send pending notifications again',
        #                              test.dut.dstl_send_pending_notifications())

########
        t1 = test.thread(test.dut.dstl_collect_result, 'Step xx: Send pending notifications again',
                                     test.dut.dstl_send_pending_notifications)
        t2 = test.thread(test.network_lost, 12, 25)  # network lost point 12
        t1.join()
        t2.join()
        if test_abort:  # is set in network_lost
            # abort full testcase, no cleanup etc.
            raise Exception('network lost was done for point ' + str(network_lost_at_point) + ' - Test abort')


        test.log.step('Step 14: Check ping google - Start')
        test.dut.dstl_collect_result('Step xx: Check ping google',
                                         test.dut.dstl_check_google_ping())

        test.log.step('Step 15: Check IP address and APN in <list> command - Start')
        test.dut.dstl_collect_result('Step xx: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

        test.log.step('Step 16: Get all attributes from device - Start')
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

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.info("Reset module.")
        # test.dut.dstl_restart()
        # test.log.info ('wait 5 sec. for RTC reinitialize ')
        # test.sleep(5)
        # test.log.info ('set correct time')
        # test.dut.dstl_set_real_time_clock()
        # test.log.info ('set donwload mode 1 like aidon')
        # test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1'))
        # test.log.info ('wait x Minutes, if the module start subscription')
        # test.sleep(5)
        # iccids = test.dut.dstl_get_all_iccids(test.dut.dstl_get_imei())
        # count_iccids = len (iccids)
        # if len (iccids)>=1:
        #     test.log.info ('There is one subscription on the Server for these module, please check')
        # else:
        #     test.log.info('No subscription on the Server for these module')
        # test.sleep(120)
        # iccids = test.dut.dstl_get_all_iccids(test.dut.dstl_get_imei())
        # count_iccids = len (iccids)
        #
        # if count_iccids > 1:
        #     test.expect(False)
        #     test.log.info ('Found more the one subscription for these IMEI - ERROR')
        # else:
        #     test.expect(True)
        #     test.log.info('Found only one subscription for these IMEI, ok')

        test.dut.dstl_print_results()

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))
        # test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
        #                type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        test.log.com(' ')

if "__main__" == __name__:
    unicorn.main()

