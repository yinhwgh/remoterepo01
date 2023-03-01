# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# test case: UNISIM01-296
'''
For Testcase description and the measurement point please look into the jira task
Global flow:
- setup module
- loop start
    - check MODs Server address of the module
    - set a wrong
        1) IP address and correct port of the MODS server
        2) port and correct IP address of the MODS server
        3) set correct IP and port of MODS Server
    - start module and subscription download -> MUST FAILED for 1&2, passed for 3
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
#KPI_NAME = 'esim_provisioning_with_instant_connect'
#KPI_TYPE = 'bin'
testkey = 'UNISIM01-296'
imei =''
ver = "1.0"


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

        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
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

        test.dut.at1.send_and_verify('at^SUSMA="LPA/Engine",1', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('at^SUSMA="LPA/Profiles/Info"', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid","UNICORN-POC"', wait_for='OK', timeout=10)
        test.dut.at1.send_and_verify('AT+creg=2')
        test.dut.at1.send_and_verify('AT+cgreg=2')
        test.dut.at1.send_and_verify('At&w')

    def run(test):
        stepline = '/n############################################################'

        test.log.info('Check device on MODS - Start')
        test.log.info("This is your IMEI: " + imei)
        dev_on_mods, device_id = test.dut.dstl_check_device_on_mods(imei)

        test.log.step('Step 1.0: Check current MODS Address' + stepline)
        test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address', wait_for="OK",
                                                 expect='partners-dgw.iot-suite.thalescloud.io:5684', timeout=10))

        for n in range (2,5):
            test.log.step ('Step ' + str(n) + '.0: Loop start' + stepline)

            test.log.step ('Step ' + str(n) + '.1: Stop Mods Server' + stepline)
            test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","stop"', wait_for="OK", timeout=20))
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,0', 'OK', timeout=10))
            if n == 2:
                # set wrong IP and correct port
                test.log.step ('Step ' + str(n) + '.2: set a wrong IP address and correct port of the MODS server')
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address,"coaps://doesnt-exist.emalto.com:5684"',
                                                              wait_for="OK",
                                                              expect='doesnt-exist.emalto.com:5684',
                                                              timeout=10))
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address', wait_for="OK",
                                                              expect='doesnt-exist.emalto.com:5684',
                                                              timeout=10))
            elif n == 3:
                # set correct IP and wrong port
                test.log.step ('Step ' + str(n) + '.2: set a wrong port and correct IP address of the MODS server')
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address,"coaps://partners-dgw.iot-suite.thalescloud.io:5000"',
                                                              wait_for="OK",
                                                              expect='partners-dgw.iot-suite.thalescloud.io:5000',
                                                              timeout=10))
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address', wait_for="OK",
                                                              expect='partners-dgw.iot-suite.thalescloud.io:5000',
                                                              timeout=10))
            else:
                # all other cases... correct IP and port
                test.log.step ('Step ' + str(n) + '.3: set a wrong port and correct IP address of the MODS server')
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address,"coaps://partners-dgw.iot-suite.thalescloud.io:5684"',
                                                              wait_for="OK",
                                                              expect='partners-dgw.iot-suite.thalescloud.io:5684',
                                                              timeout=10))
                test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address', wait_for="OK",
                                                              expect='partners-dgw.iot-suite.thalescloud.io:5684',
                                                              timeout=10))

            test.log.step('Step ' + str(n) + '.4: Prepare the download')
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/Engine/URC,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/EXT/URC",1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc=ConMgr/Fallback/Urc,99', '.*invalid index.*', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma=LPA/Engine,1', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', wait_for='OK', timeout=10))
            test.expect(test.dut.at1.wait_for('CREG: 5', timeout=600.0, greedy=False))

            test.log.step('Step ' + str(n) + '.5: Start mods')
            test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))
            test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","start"', wait_for='OK', timeout=30))

            test.log.step('Step ' + str(n) + '.6: wait for download failed')
            test.sleep(600)
            read_data = test.dut.at1.read(append=True)
            if 'SYSSTART AIRPLANE MODE' in read_data and n != 4:
                test.expect(False)
                test.log.info ('Error, "SYSSTART AIRPLANE MODE" received')
            elif 'SYSSTART AIRPLANE MODE' in read_data and n != 4:
                test.expect(True)
                test.log.info ('Good case.')
            else:
                test.expect(True)
                test.log.info('All fine, NO "SYSSTART AIRPLANE MODE" received')

            test.log.step('Step ' + str(n) + '.7: Switch MODS Server off and restart module')
            test.expect(test.dut.at1.send_and_verify('at^srvctl="MODS","stop"', wait_for="OK", timeout=20))
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify('at^susmc=LPA/profiles/download/URC,0', 'OK', timeout=10))
            test.expect(test.dut.dstl_restart())

            # for loop end

        # ende Test



    def cleanup(test):

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.info('collect Infos if something went wrong above')
        test.expect(test.dut.at1.send_and_verify('at^susmc?', 'OK', timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^susma?', 'OK', timeout=10))

        test.log.info('set correct MODS Server Adress')
        test.expect(
            test.dut.at1.send_and_verify('at^srvcfg=MODS,address,"coaps://partners-dgw.iot-suite.thalescloud.io:5684"',
                                         wait_for="OK",
                                         expect='partners-dgw.iot-suite.thalescloud.io:5684',
                                         timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^srvcfg=MODS,address', wait_for="OK",
                                                 expect='partners-dgw.iot-suite.thalescloud.io:5684', timeout=10))

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()