"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105089.001 - Gnss_US_Territory
intention:  It should be checked, that Galileo/Beidou  is not active over US territory
LM-No (if known): LM0007038.001 - Serval
used eq.: DUT-At1,DUT-NMEA, SMBV
execution time (appr.): 16 min
"""

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    def setup(test):
        err_text = 'no SMBV found -> stop testcase'
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna(smbv_required=True)
        if not test.smbv_active:
            err_text_plugin = 'network_instrument plugin NOT installed/active or no SMBV found -> stop testcase !!!'
            all_results.append([err_text_plugin, 'FAILED'])
            test.log.error(err_text_plugin)
            test.expect(False, critical=True)

        test.dut.dstl_detect()

    def run(test):

        test.log.com("Setting SMBV")
        test.smbv.dstl_smbv_switch_on_all_system()

        wait_time_after_fix = 30

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1 : Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.at1.send_and_verify("at^sgpsc=\"Power/Psm\",\"0\"", ".*OK.*")
        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

        test.log.step('Step 3: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 3: Wait for first fix position', test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 120) is True)

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        city = ['New York', 'Munich']
        for i in range(len(city)):

            test.smbv.dstl_smbv_change_location(city[i])
            test.log.step('Step 5.'+str(i+1) + ' (' + city[i] + '): Change at GNSS simulator the location to '+city[i]+' - Start')
            test.dut.dstl_collect_result('Step 5.'+str(i+1)+' (' + city[i] + '): Change at GNSS simulator the location to '+city[i], True)
            test.sleep(5)

            test.log.step('Step 6.'+str(i+1)+' (' + city[i] + '): Enable engine for Galileo - Start')
            test.dut.dstl_collect_result('Step 6.'+str(i+1)+' (' + city[i] + '): Enable engine for Galileo', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Galileo\",\"1\""))

            test.log.step('Step 7.'+str(i+1) + ' (' + city[i] + '): Restart module - Start')
            test.dut.dstl_collect_result('Step 7.'+str(i+1)+ ' (' + city[i] + '): Restart module', test.dut.dstl_restart())

            test.log.step('Step 8.'+str(i+1)+ ' (' + city[i] + '): Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 8.'+str(i+1)+ ' (' + city[i] + '): Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

            # workaround for Serval to find fix for US faster: switch off / on engine twice
            test.sleep(60)
            test.dut.nmea.read()

            if test.dut.project == 'SERVAL':
                test.log.com('Workaround for Serval to find fix for US/Munich faster: switch off / on engine twice - Info only')
                all_results.append(['Workaround for Serval to find fix for US/Munich faster: switch off / on engine twice', 'Info only'])

                test.log.step('Step 8-1.' + str(i+1) + ' (' + city[i] + '): Switch off GNSS engine - Start')
                test.dut.dstl_collect_result('Step 8-1.' + str(i + 1) + ' (' + city[i] + '): Switch off GNSS engine', test.dut.dstl_switch_off_engine())

                test.log.step('Step 8-2.' + str(i+1) + ' (' + city[i] + '): Switch on GNSS engine - Start')
                test.dut.dstl_collect_result('Step 8-2.'+str(i+1)+ ' (' + city[i] + '): Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

            test.log.step('Step 9.'+str(i+1) + ' (' + city[i] + '): Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 9.'+str(i+1) + ' (' + city[i] + '): Wait for first fix position', test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 600) is True)

            test.dut.nmea.read()
            test.sleep(wait_time_after_fix)
            nmea_data = test.dut.nmea.read()

            test.log.step('Step 10.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data GAGSV - Start')
            if city[i] == 'New York':
#            if i == 0:
                test.dut.dstl_collect_result('Step 10.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data over US: GAGSV must be invisible', not test.dut.dstl_find_nmea_data(nmea_data, "GAGSV"))
            else:
                test.dut.dstl_collect_result('Step 10.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data GAGSV: must be visible', test.dut.dstl_find_nmea_data(nmea_data, "GAGSV"))

            test.log.step('Step 11.1.'+str(i+1) + ' (' + city[i] + '): Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 11.1.'+str(i+1) +' (' + city[i] + '): Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            test.log.step('Step 11.2.'+str(i+1)+ ' (' + city[i] + '): Disable engine for Galileo - Start')
            test.dut.dstl_collect_result('Step 11.2.'+str(i+1)+ ' (' + city[i] + '): Disable engine for Galileo', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Galileo\",\"0\""))

            test.log.step('Step 11.3.'+str(i+1)+ ' (' + city[i] + '): Enable engine for Beidou - Start')
            test.dut.dstl_collect_result('Step 11.3.'+str(i+1)+ ' (' + city[i] + '): Enable engine for Beidou', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Beidou\",\"1\""))

            test.log.step('Step 11.4.'+str(i+1)+ ' (' + city[i] + '): Restart module - Start')
            test.dut.dstl_collect_result('Step 11.4.'+str(i+1)+ ' (' + city[i] + '): Restart module', test.dut.dstl_restart())

            test.log.step('Step 12.'+str(i+1)+ ' (' + city[i] + '): Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 12.'+str(i+1)+ ' (' + city[i] + '): Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

            test.log.step('Step 13.'+str(i+1)+ ' (' + city[i] + '): Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 13.'+str(i+1)+ ' (' + city[i] + '): Wait for first fix position', test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 600) is True)

            test.dut.nmea.read()
            test.sleep(wait_time_after_fix)
            nmea_data = test.dut.nmea.read()

            test.log.step('Step 14.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data BDGSV - Start')
            if city[i] == 'New York':
#            if i == 0:
                test.dut.dstl_collect_result('Step 14.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data over US: BDGSV must be invisible', not test.dut.dstl_find_nmea_data(nmea_data, "BDGSV"))
            else:
                test.dut.dstl_collect_result('Step 14.'+str(i+1)+ ' (' + city[i] + '): Check NMEA Data BDGSV: must be visible', test.dut.dstl_find_nmea_data(nmea_data, "BDGSV"))

            test.log.step('Step 15.1.' + str(i + 1) + ' (' + city[i] + '): Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 15.1.' + str(i + 1) + ' (' + city[i] + '): Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            test.log.step('Step 15.2.'+str(i+1)+ ' (' + city[i] + '): Disable engine for Beidou - Start')
            test.dut.dstl_collect_result('Step 15.2.'+str(i+1)+ ' (' + city[i] + '): Disable engine for Beidou', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Beidou\",\"0\""))


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 16: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 16: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
