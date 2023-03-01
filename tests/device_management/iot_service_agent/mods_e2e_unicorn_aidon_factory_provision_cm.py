# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-347/UNISIM01-348

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
testkey = "UNISIM01-347/UNISIM01-348"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300
    kpi_name_registration_after_startup = ""

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        # TEMPORARY solution. Should not be hardcoded. Group id of MigrationGroup
        test.group_id = '91b33a23-27c1-4b02-9f93-dc2f41c8fd85'

        # test.kpi_nw_registration_power_consumption = "none"
        # test.mc_test4_available = False

        test.dut.dstl_detect()

        # try:
        #     test.mctest_present = test.dut.devboard.send_and_verify("MC:VBATT", "OK")
        #     if test.mctest_present:
        #         test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        #         test.dut.dstl_switch_off_at_echo(serial_ifc=1)
        #         test.dut.dstl_set_urc(urc_str="off")
        #         if 'MC-Test4' in test.dut.dstl_get_dev_board_version():
        #             label = test.dut.dstl_get_device_label()
        #             # workaround: problems with CI
        #             if 'blnlnx5.gemalto' in label:
        #                 test.log.com('***** workaround: problems with CI - do not perform power consumption measurement - computer name: ' + label)
        #             else:
        #                 test.log.com('***** "MC-Test4" found - power consumption measurement will be started later *****')
        #                 test.mc_test4_available = True
        #
        # except Exception as e:
        #     test.mc_test4_available = False


        test.log.step('Step 1: Create/check device on MODS - Start')
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        result, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, imei, group_id=test.group_id)
        test.dut.dstl_collect_result('Step 1: Create/check device on MODS', result)




    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.log.step("Step 1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        # result = test.dut.dstl_check_network_registration()
        # if result == True:
        #     test.log.info("Stop KPI timer: " + test.kpi_name_registration_after_startup)
        #     test.kpi.timer_stop(test.kpi_name_registration_after_startup)
        #     if test.mc_test4_available:
        #         test.log.info(f'Stop and save KPI NW scan power consumption: {test.kpi_name_registration_power_consumption}')
        #         test.dut_devboard.send_and_verify("mc:ccmeter=off", expect=".*OK.*")
        #         test.dut_devboard.send_and_verify("mc:ccmeter=read", expect=".*OK.*")
        #         power_value = re.findall(r'.*W= *(\d{1,4}\.\d{1,4})mAh.*',
        #                              test.dut.devboard.last_response, re.I | re.S)
        #         if power_value and result:
        #             dstl.test.kpi_store(name=test.kpi_name_registration_power_consumption, value=power_value[0], type='num', device=test.dut)
        # else:
        #     if test.mc_test4_available:
        #         test.log.info('McTest4 available, but no network registration - stop power consumption measurement => NO KPI')
        #         test.dut_devboard.send_and_verify("mc:ccmeter=off", expect=".*OK.*")
        #         test.dut_devboard.send_and_verify("mc:ccmeter=read", expect=".*OK.*")

        test.dut.dstl_restart()
        test.sleep(5)

        test.log.step('Step 1: Set all URCs - Start')

        result = True
        result = test.dut.at1.send_and_verify('AT+CGMM', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT\Q3', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('ATI1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SSET=1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND="CEER",1,99', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=euiccid,1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=ICCID,2', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=ICCID,1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=simstatus,1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=simdata,1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=eons,1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatM","80000","0"', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SXRAT=7,7', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SUSMC="LPA/Ext/URC",1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT+CEREG=1', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT+CGREG=2', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT^SIND=simstatus,2', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('AT+CGSN', expect='.*OK.*') and result
        result = test.dut.at1.send_and_verify('at^scid', expect='.*OK.*') and result

        result = test.dut.at1.send_and_verify_retry('AT^SUSMA="LPA/Engine",1',
                                                  expect='.*"LPA/Engine",2.*OK.*',
                                                  retry=5,
                                                  sleep=10, retry_expect='.*OK.*|.*ERROR.*')
        #result = test.dut.at1.send_and_verify('AT^SUSMA="LPA/Engine",1', expect='.*OK.*') and result

        test.dut.dstl_collect_result('Step 1: Set all URCs', result)


        test.log.step('Step 2: Set downloadmode to 1 - Start')
        test.dut.dstl_collect_result('Step 2: Set downloadmode to 1', test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))

        test.sleep(3)


        test.log.step('Step 3: Wait for registration - Start')
        #result = test.dut.at1.send_and_verify('at+cereg?', expect='.*OK.*') and True
        result = test.dut.at1.send_and_verify_retry('at+cereg?',
                                                  expect='.*CEREG: 1,5.*OK.*',
                                                  retry=60,
                                                  sleep=1, retry_expect='.*OK.*|.*ERROR.*')

        test.dut.dstl_collect_result('Step 3: Wait for registration', result)

        test.log.step('Step 4: Check at+cops? -> 7 - Start')
        test.dut.dstl_collect_result('Step 4: Check at+cops? -> 7', test.dut.at1.send_and_verify('at+cops?', expect='.*COPS:.*,.*,.*,7.*OK.*'))

        test.log.step('Step 5: Check at^smoni -> 262 - Start')
        test.log.warn("*** check cell MCC and MNC - has to be done more suitable" )
        test.dut.dstl_collect_result('Step 5: Check at^smoni -> 262', test.dut.at1.send_and_verify('at^smoni', expect='.*,262,.*OK.*'))

        test.log.step('Step 6: Check downloadmode=1 ? - Start')
        test.dut.dstl_collect_result('Step 6: Check downloadmode=1 ?',
                        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='.*"MODS","usm/downloadMode","1".*OK.*'))

        test.log.info("*** AIDON checks some device infos - approx. 30 seconds ***")
        test.sleep(30)

        test.log.step('Step 7: Check cgdcont = "JTM2M" ? - Start')
        test.dut.dstl_collect_result('Step 7: Check cgdcont = "JTM2M" ?',
                        test.dut.at1.send_and_verify('AT+CGDCONT?', expect='.*CGDCONT: 1,.*,"JTM2M".*OK.*'))

        test.log.step('Step 8: Set PRID to "UNICORN-POC" - Start')
        test.dut.dstl_collect_result('Step 8: Set PRID to "UNICORN-POC"',
                                     test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid","UNICORN-POC"',
                                                                expect='.*OK.*'))

        test.log.step('Step 9: Start MODS agent - Start')
        test.dut.dstl_collect_result('Step 9: Start MODS agent',
                                     test.dut.at1.send_and_verify('AT^SRVCTL="MODS","start"',
                                                                expect='.*OK.*'))

        test.log.info("*** AIDON checks some device infos - approx. 30 seconds ***")
        test.sleep(30)

        test.dut.at1.send_and_verify('at+cereg?', expect='.*OK.*')
        if 'CEREG: 1,5' in test.dut.at1.last_response:
            test.log.info("+CEREG: 1,5 found -> Module is registered ")
        else:
            test.log.info("+CEREG: 1,5 NOT found -> Module is NOT registered ")


        test.log.step('Step 10: Set AT+COPS=2 - Start')
        test.dut.dstl_collect_result('Step 10: Set AT+COPS=2',
                                     test.dut.at1.send_and_verify('AT+COPS=2', expect='.*OK.*'))

        test.log.step('Step 11: Set AT+COPS=0,,,7 - Start')
        test.dut.dstl_collect_result('Step 11: AT+COPS=0,,,7',
                                     test.dut.at1.send_and_verify('AT+COPS=0,,,7', expect='.*OK.*', timeout=120))


        # test.log.step('Step 12: Wait for SYSSTART - Start')
        # test.dut.dstl_collect_result('Step 12: Wait for SYSSTART',
        #                              test.dut.at1.wait_for(".*SYSSTART.*SSIM READY.*", timeout=test.systart_timeout))

        test.log.info("*** AIDON checks some device infos - approx. 160 seconds ***")
        test.sleep(160)

        test.log.step('Step 13: Wait for registration - Start')
        # result = test.dut.at1.send_and_verify_retry('at+cereg?',
        #                                           expect='.*CEREG: [0124],5.*OK.*',
        #                                           retry=30,
        #                                           sleep=5, retry_expect='.*OK.*|.*ERROR.*')
        result = test.dut.at1.send_and_verify_retry('at+cereg?;+creg?',
                                                  expect='.*CEREG: [0124],5.*OK.*',
                                                  retry=30,
                                                  sleep=5, retry_expect='.*OK.*|.*ERROR.*')

        test.dut.dstl_collect_result('Step 13: Wait for registration', result)


        test.log.step('Step 14: Check at^smoni - Start')
        test.dut.dstl_collect_result('Step 14: Check at^smoni', test.dut.at1.send_and_verify('at^smoni', expect='.*OK.*'))
        test.log.step('Step 14: Check at^smoni - Start')

        test.dut.at1.send_and_verify('at+cops?', expect='.*OK.*')


        test.log.step('Step 15: Send <LIST> command - Start')
        test.dut.dstl_collect_result('Step 15: Send <LIST> command', test.dut.at1.send_and_verify('AT^SNLWM2M=status/srv,<list>', expect='.*registered.*OK.*'))

        test.log.step('Step 16: Activate LPA/engine 2 times - Start')
        result = test.dut.at1.send_and_verify('AT^SUSMA="LPA/Engine",1', expect='.*OK.*')
        result = test.dut.at1.send_and_verify('AT^SUSMA="LPA/Engine",1', expect='.*OK.*') and result
        test.dut.dstl_collect_result('Step 16: Activate LPA/engine 2 times', result)


        test.log.step('Step 17: Try to send notifications 2 times - Start')
        result = test.dut.at1.send_and_verify_retry('AT^SUSMA="LPA/Ext/NotificationSent"',
                                                  expect='.*OK.*',
                                                  retry=2,
                                                  sleep=20, retry_expect='.*CME ERROR.*')
        # result = test.dut.at1.send_and_verify('AT^SUSMA="LPA/Ext/NotificationSent"', expect='.*OK.*')
        # test.sleep(20)
        # result = test.dut.at1.send_and_verify('AT^SUSMA="LPA/Ext/NotificationSent"', expect='.*OK.*') and result
        test.dut.dstl_collect_result('Step 17: Try to send notifications 2 times', result)


        test.log.step('Step 18: Check at^scid - Start')
        test.dut.dstl_collect_result('Step 18: Check at^scid', test.dut.at1.send_and_verify('at^scid', expect='.*893540102103040.*OK.*'))



    def cleanup(test):

        test.dut.dstl_get_all_mods_settings()
        test.dut.dstl_check_apn_and_mods_apns(apn="internet")
        test.dut.at1.send_and_verify('at&v', expect='.*OK.*')

        test.dut.dstl_print_results()

        # test.log.com("passed: " + str(test.verdicts_counter_passed))
        # test.log.com("total: " + str(test.verdicts_counter_total))
        # test.kpi_store(name=KPI_NAME, value=test.verdicts_counter_passed,
        #                type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)
        #
        # test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
        #                                 testkey, str(test.test_result), test.campaign_file,
        #                                 test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()