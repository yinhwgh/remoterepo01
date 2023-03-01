# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-338 - Check factory stabilization: Set download Mode with at+cops=2 (Radio Off)
# Precondition: no operational profile on eSIM

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


testkey = "UNISIM01-338"

class Test(BaseTest):
    """
    Use Case: Initial Provisioning with Instant Connect
    """
    systart_timeout = 300
    kpi_name_registration_after_startup = ""

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_detect()
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)
        test.dut.dstl_restart()



    def run(test):

        max_loop = 10
        for i in range(1, max_loop+1):

            dstl.log.info('****** Loop: ' + str(i) + ' of ' + str(max_loop) + ' - Start ******')

            test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatM","80000","0"', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SXRAT=7,7', expect='.*OK.*'))
            test.dut.dstl_restart()

            # cops=2
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2', expect='.*OK.*', timeout=30))

            test.expect(test.dut.at1.send_and_verify('AT+CGMM', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT\\Q3', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('ATI1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SSET=1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND="CEER",1,99', expect='.*OK.*'))

            test.expect(test.dut.at1.send_and_verify('AT^SIND=euiccid,1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=ICCID,2', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=ICCID,1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=simstatus,1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=simdata,1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=eons,1', expect='.*OK.*'))


            #test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/CatM","80000","0"', expect='.*OK.*'))
            #test.expect(test.dut.at1.send_and_verify('AT^SXRAT=7,7', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify("at^susmc=\"LPA/Ext/URC\",1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at^susmc=\"LPA/Engine/URC\",1", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at^susmc=\"LPA/Profiles/Download/URC\",1",
                                                ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT+CEREG=1', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CGREG=2', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SIND=simstatus,2', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CGSN', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at^scid', expect='.*OK.*'))

            test.expect(test.dut.dstl_activate_lpa_engine())

            test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*2.*OK.*', timeout=120))

            test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*SRVCFG: "MODS","usm/downloadMode","1".*OK.*'))

            if 'Auto Profile Enable failed' in test.dut.at1.last_response:
                test.sleep(1)
                test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*SRVCFG: "MODS","usm/downloadMode","0".*OK.*'))
                test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*SRVCFG: "MODS","usm/downloadMode","1".*OK.*'))


            test.dut.at1.verify_or_wait_for('.*SSIM READY.*', timeout=45)

            test.sleep(5)

            test.dut.at1.send_and_verify('at^SUSMA="LPA/Profiles/Info"', expect='.*OK.*')
            if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
                dstl.log.info("Looks fine your bootstrap profile is active")
            else:
                dstl.log.error("Bootstrap is somehow not active - Something went wrong")
                result = False

            # cfun = 1
            #test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', expect='.*OK.*'))
            # cops=0
            test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*0.*OK.*', timeout=120))
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='.*OK.*|.*ERROR.*', timeout=180))

            test.expect(test.dut.dstl_check_network_registration())
            test.expect(test.dut.at1.send_and_verify('at+cereg?', expect='.*OK.*'))



            test.dut.dstl_deactivate_bootstrap()
            test.dut.dstl_set_download_mode_wo_agent(download_mode=0)


            test.sleep(10)
            dstl.log.info('****** Loop: ' + str(i) + ' of ' + str(max_loop) + ' - End ******')

    def cleanup(test):

        test.dut.dstl_print_results()

        test.log.com("passed: " + str(test.verdicts_counter_passed))
        test.log.com("total: " + str(test.verdicts_counter_total))

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start,test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
