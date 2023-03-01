# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# Test case: UNISIM01-249: Perform network scan measurements and provide time measurements via KPI's
#

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary.devboard.devboard import *
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *

import datetime

testkey = "UNISIM01-249"

class Test(BaseTest):
    """
    Init
    """

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings_max_values()
        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_set_real_time_clock()


    def run(test):
        test.time_for_scan = 300
        test.kpi_nw_scan_power_consumption = "none"
        test.mc_test4_available = False

        try:
            test.mctest_present = test.dut.devboard.send_and_verify("MC:VBATT", "OK")
            if test.mctest_present:
                test.dut.dstl_switch_off_at_echo(serial_ifc=0)
                test.dut.dstl_switch_off_at_echo(serial_ifc=1)
                test.dut.dstl_set_urc(urc_str="off")
                if 'MC-Test4' in test.dut.dstl_get_dev_board_version():
                    test.mc_test4_available = True
        except Exception as e:
            test.mc_test4_available = False


        kpi_timer = 'network_scan_catm'
        snmon_parameter = '"INSCatM",2'
        step = 1
        if test.mc_test4_available:
            test.kpi_nw_scan_power_consumption = "esim_network_scan_catm_power_consumption"
        test.scan_network(kpi_timer, snmon_parameter, step_number=step, kpi_power_consumption=test.kpi_nw_scan_power_consumption)


        kpi_timer = 'network_scan_nb_iot'
        snmon_parameter = '"INSCatNB",2'
        step = 2
        if test.mc_test4_available:
            test.kpi_nw_scan_power_consumption = "esim_network_scan_nb_iot_power_consumption"
        #test.scan_network(kpi_timer, snmon_parameter, step_number=step)
        test.scan_network(kpi_timer, snmon_parameter, step_number=step, kpi_power_consumption=test.kpi_nw_scan_power_consumption)


        kpi_timer = 'network_scan_catm_band_3_20'
        snmon_parameter = '"INSCatM",2,"00080004"'
        step = 3
        if test.mc_test4_available:
            test.kpi_nw_scan_power_consumption = "esim_network_scan_catm_band_3_20_power_consumption"
        #test.scan_network(kpi_timer, snmon_parameter, step_number=step)
        test.scan_network(kpi_timer, snmon_parameter, step_number=step, kpi_power_consumption=test.kpi_nw_scan_power_consumption)


        if test.dut.product.upper() == "EXS82" or test.dut.product.upper() == "TX82":
            kpi_timer = 'network_scan_2g'
            snmon_parameter = '"INS2G",2'
            step = 4
            if test.mc_test4_available:
                test.kpi_nw_scan_power_consumption = "esim_network_scan_2g_power_consumption"
            #test.scan_network(kpi_timer, snmon_parameter, step_number=step)
            test.scan_network(kpi_timer, snmon_parameter, step_number=step, kpi_power_consumption=test.kpi_nw_scan_power_consumption)


    def scan_network(test, kpi_timer="", snmon_parameter="", step_number=0, kpi_power_consumption="none"):
        test.log.step(f'Step {step_number}: Network scan: {kpi_timer} - Start')
        test.log.info(f'Start KPI timer: {kpi_timer}')
        test.kpi.timer_start(kpi_timer, device=test.dut)
        if "none" not in kpi_power_consumption:
            test.log.info(f'Start KPI NW scan power consumption: {kpi_power_consumption}')
            test.dut_devboard.send_and_verify("mc:ccmeter=on", expect=".*OK.*")

        result = test.dut.at1.send_and_verify(f'at^snmon={snmon_parameter}', expect=".*OK.*", timeout=test.time_for_scan)
        #result = re.match('(?is).*SNMON:.*INS.*OK.*', test.dut.at1.last_response) and result
        test.dut.dstl_collect_result(f'Step {step_number}: Network scan: {kpi_timer}', result)
        if result:
            test.kpi.timer_stop(kpi_timer)
            test.log.info(f'Stop KPI timer: {kpi_timer}')
        else:
            test.log.error(f'error during network scan: {kpi_timer} - no KPI measurement')
            test.dut.at1.send_and_verify('at', expect=".*O.*")

        if "none" not in kpi_power_consumption:
            test.log.info(f'Stop and save KPI NW scan power consumption: {kpi_power_consumption}')
            test.dut_devboard.send_and_verify("mc:ccmeter=off", expect=".*OK.*")
            test.dut_devboard.send_and_verify("mc:ccmeter=read", expect=".*OK.*")
            power_value = re.findall(r'.*W= *(\d{1,4}\.\d{1,4})mAh.*',
                                 test.dut.devboard.last_response, re.I | re.S)
            if power_value and result:
                dstl.test.kpi_store(name=kpi_power_consumption, value=power_value[0], type='num', device=test.dut)

    def cleanup(test):

        test.log.com('*** reset radio band settings ***')
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.sleep(5)

        test.dut.dstl_print_results()

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
