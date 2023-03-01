# responsible: baris.kildi@thalesgroup.com, katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-217 - Fallback during initial provisioning

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
from dstl.auxiliary.write_json_result_file import *

import json
import datetime

testkey = "UNISIM01-217"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 50
    #fallback_rule_name = "UNICORN-POC"

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

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

        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()

        test.log.step(
            "1. at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("2. Enable fallback and profile management, Fallback/Automode should be set to 0 else ConMgr"
                      "will trigger automatically download")
        test.dut.dstl_activate_cm_settings()

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "3. Bootstrap profile is shown per default Jersey Telecom. If instant connect sim is in use change it to EasyConnect elso do nothing")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if 'EasyConnect Provisioning' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^susmc="ConMgr/Profile/Table",0,"89000000000000000040","EasyConnect Provisioning",2,1,"JTM2M","","",0,0')
        else:
            test.log.info("ELISA sim is in use therefor do not need to change connection manager table")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.log.step("4. List all profiles in connection manager table")
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
            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*')
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

        test.log.step("5. Register to network and display the address of the active PDP context")
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

        test.log.step('Step 6: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS - Start')
        test.dut.dstl_collect_result('Step 6: APN in cgdcont and APN in AT^SNLWM2M=cfg/ext,MODS',
                                         test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"), test_abort=True)


        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.step("7. Create device on MODS")
        label = test.dut.dstl_get_device_label()

        test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        response = create_device(imei, label)
        body = response.json()
        log_body(body)
        test.expect(response.status_code == 200)
        test.expect(body != [])
        device_id = body["id"]

        test.sleep(60)
        
        #test.log.step('Step 8: Define fallback rule on MODS - Start')
        #assign_fallback_rule_resp = assign_fallback_rule(device_id, test.fallback_rule_name)
        #test.dut.dstl_collect_result('Step 8: Define fallback rule on MODS',
        #                             assign_fallback_rule_resp.status_code == 200)

        test.log.com('*** set susmc parameters ***')
        fallback_timeout = 120
        test.dut.dstl_activate_cm_settings(cm_fb_automode=1, cm_fb_timeout=fallback_timeout)

        test.log.step("9. Set Download Mode to 1")
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
            "10. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        max_count = 30
        while ",registered" not in test.dut.at1.last_response and wait_count < max_count:
            test.dut.at1.log.com("Loop " + str(wait_count) + "/" + str(max_count))
            test.expect(
                test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

       
        test.dut.at1.wait_for('"Load Bound Profile Package done - Profile download successful"',
                              timeout=test.systart_timeout)
        #        test.dut.at1.wait_for(".*SYSSTART AIRPLANE MODE.*SYSSTART.*", timeout=test.systart_timeout)
        #        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)


        test.log.com('*** Force network registration to unavailable network ***')
        test.dut.at1.send_and_verify('at+cops=1,2,26295', expect='CME ERROR', timeout=150)
        test.dut.at1.verify_or_wait_for('.*SUSMA: "ConMgr/Profile",0.*SSIM READY.*', timeout=(fallback_timeout + 60))

        test.log.step('Step 11: Check if bootstrap profile is activated - Start')
        # Expect boostrap profile is activated
        _, profiles = test.dut.dstl_get_profile_info()
        bootstrap_profile = profiles[0]
        result = (bootstrap_profile['profile_state'] == '1')
        test.dut.dstl_collect_result('Step 11: Check state of bootstrap profile (=1)', result)

        test.log.step('Step 12: Check downloadmode 3 - Start')
        test.dut.dstl_collect_result('Step 12: Check downloadmode 3',
        test.dut.at1.send_and_verify('at^srvcfg="MODS","usm/downloadMode"', expect='.*3.*OK.*'))

        rat = test.dut.dstl_get_rat()
        test.dut.at1.send_and_verify(f'at+cops=0,,,{rat}', expect='OK', timeout=150)
        test.log.step('Step 13: Check network registration after fallback - Start')
        test.dut.dstl_collect_result('Step 13: Check network registration after fallback',
                                         test.dut.dstl_check_network_registration())

        test.log.step('Step 14: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS - Start')
        test.dut.dstl_collect_result('Step 14: Check APNs in cgdcont? and at^snlwm2m=cfg/ext,MODS (=JTM2M)',
        test.dut.dstl_check_apn_and_mods_apns(apn="JTM2M"))

        test.dut.at1.verify_or_wait_for(".*SUSMA:.*ConMgr/Profile.*,2.*", timeout=300)

        test.dut.dstl_init_all_mods_settings()

        test.log.step(
            "15. at^susmc? throws per default only 2 parameters. To make missing parameter visible call following top secret command")
        test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', expect="CME ERROR")

        test.dut.at1.send_and_verify('at^susmc?', wait_for="OK", timeout=10)

        test.dut.dstl_check_network_registration()

        test.log.step('Step 16: Check ping google - Start')
        test.dut.dstl_collect_result('Step 16: Check ping google',
                                         test.dut.dstl_check_google_ping())

        test.log.step('Step 17: Check IP address and APN in <list> command - Start')
        test.dut.dstl_collect_result('Step 17: Check IP address and APN in <list> command',
                                         test.dut.dstl_check_ip_addr_and_apn_in_list_cmd(apn="internet"))

    def cleanup(test):

        test.dut.dstl_activate_cm_settings()
        test.dut.dstl_send_pending_notifications()
        test.dut.dstl_get_all_mods_settings()

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
