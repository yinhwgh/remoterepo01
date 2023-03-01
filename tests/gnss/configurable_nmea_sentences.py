"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105083.001
intention:  NMEA -GSV Data for different system can be enable/disable
            The settings become effective immediately and is stored non-volatile
LM-No (if known): LM0006731.003 - Serval
used eq.: DUT-At1, NMEA-port, SMBV preferred (roof Antenna, if SMBV not available)
execution time (appr.): 12 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    smbv_active = False

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        sleep_time_after_fix = 60
        read_time_after_clear_buffer = 20

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.at1.send_and_verify("at^sgpsc=\"Power/Psm\",\"0\"", ".*OK.*")
        test.log.step('Step 2.1: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2.1: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 2.2 Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 2.2: Wait for first fix position', test.dut.nmea.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100) is True)

        test.sleep(sleep_time_after_fix)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        # GPS and GLNOASS active
        nmea=['GPGSV', 'GLGSV','GNGSA','GNVTG','GNRMC' ,'GPGGA']     # should be visible
        for i in range(len(nmea)):
            test.log.step('Step 3.'+str(i+1)+': Check NMEA Data '+nmea[i]+' - Start')
            test.dut.dstl_collect_result('Step 3.'+str(i+1)+': Check NMEA Data '+nmea[i], test.dut.dstl_find_nmea_data(nmea_data,nmea[i]))

        nmea = ['BDGSV', 'GAGSV']              # should be not visible
        for i in range(len(nmea)):
            test.log.step('Step 3.'+str(i+7)+': Check NMEA Data '+nmea[i]+'  is invisible - Start')
            test.dut.dstl_collect_result('Step 3.'+str(i+7)+': Check NMEA Data '+nmea[i]+' is invisible', not test.dut.dstl_find_nmea_data(nmea_data,nmea[i]))

        test.log.step('Step 4: Disable NMEA for GPS - Start')
        test.dut.dstl_collect_result('Step 4: Disable NMEA for GPS', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/GPS\",\"off\""))

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 5: Check NMEA Data GPGSV is invisible- Start')
        test.dut.dstl_collect_result('Step 5: Check NMEA Data GPGSV is invisible', not test.dut.dstl_find_nmea_data(nmea_data, "GPGSV"))

        test.log.step('Step 6.1: Enable NMEA for GPS - Start')
        test.dut.dstl_collect_result('Step 6.1: Enable NMEA for GPS',  test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/GPS\",\"on\""))

        test.log.step('Step 6.2: Disable NMEA for Glonass - Start')
        test.dut.dstl_collect_result('Step 6.2:  disable NMEA for Glonass', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Glonass\",\"off\""))

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 7: Check NMEA Data GLGSV - Start')
        test.dut.dstl_collect_result('Step 7: Check NMEA Data GLGSV', not test.dut.dstl_find_nmea_data(nmea_data, "GLGSV"))

        test.log.step('Step 8: Enable NMEA for Glonass - Start')
        test.dut.dstl_collect_result('Step 8: Enable NMEA for Glonass', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Glonass\",\"on\""))

        # Galileo test
        if test.smbv_active:
            test.log.com("Setting SMBV: GPS and Galileo")
            test.smbv.dstl_smbv_switch_on_gps_galileo_systems()
            test.sleep(5)

        test.log.step('Step 9.1: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 9.1: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 9.2: Enable Galileo system - Start')
        test.dut.dstl_collect_result('Step 9.2: Enable Galileo system', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Galileo\",\"1\""))

        test.log.step('Step 9.3: restart module- Start')
        test.dut.dstl_collect_result('Step 9.3: restart module',  test.dut.dstl_restart())

        test.log.step('Step 9.4: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 9.4: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 9.5: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 9.5: Wait for first fix position', test.dut.nmea.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100) is True)

        test.sleep(sleep_time_after_fix)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        nmea = ['GPGSV', 'GAGSV', 'GNGSA', 'GNVTG', 'GNRMC', 'GPGGA']       # should be visible
        for i in range(len(nmea)):
            test.log.step('Step 10.' + str(i + 1) + ': Check NMEA Data ' + nmea[i] + ' - Start')
            test.dut.dstl_collect_result('Step 10.' + str(i + 1) + ': Check NMEA Data ' + nmea[i], test.dut.dstl_find_nmea_data(nmea_data, nmea[i]))

        nmea = ['GLGSV', 'BDGSV']                 # should be not visible
        for i in range(len(nmea)):
            test.log.step('Step 10.' + str(i + 7) + ': Check NMEA Data ' + nmea[i] + '  is invisible- Start')
            test.dut.dstl_collect_result('Step 10.' + str(i + 7) + ': Check NMEA Data ' + nmea[i]+' is invisible', not test.dut.dstl_find_nmea_data(nmea_data, nmea[i]))

        test.log.step('Step 11: Disable NMEA data for Galileo - Start')
        test.dut.dstl_collect_result('Step 11: Disable NMEA data for Galileo', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Galileo\",\"off\""))

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 12: Check NMEA Data GAGSV - Start')
        test.dut.dstl_collect_result('Step 12: Check NMEA Data GAGSV', not test.dut.dstl_find_nmea_data(nmea_data, "GAGSV"))

        test.log.step('Step 13: Enable NMEA for Galileo - Start')
        test.dut.dstl_collect_result('Step 13: Enable NMEA for Galileo', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Galileo\",\"on\""))

        # Beidou - Test
        # disable Galileo
        test.log.step('Step 14.1: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 14.1: Switch off GNSS engine', test.dut.dstl_switch_off_engine())
        test.log.step('Step 14.2: Disable Galileo system - Start')
        test.dut.dstl_collect_result('Step 14.2: Disable Galileo system', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Galileo\",\"0\""))

        # enable Beidou
        if test.smbv_active:
            test.log.com("Setting SMBV: GPS and Beidou")
            test.smbv.dstl_smbv_switch_on_gps_beidou_systems()
            test.sleep(5)

        test.log.step('Step 14.3:Enable Beidou system - Start')
        test.dut.dstl_collect_result('Step 14.3: Enable Beidou system', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Beidou\",\"1\""))

        test.log.step('Step 14.4: restart module- Start')
        test.dut.dstl_collect_result('Step 14.4: restart module',  test.dut.dstl_restart())

        test.log.step('Step 14.5: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 14.5: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 14.6: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 14.6: Wait for first fix position', test.dut.nmea.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100) is True)

        test.sleep(sleep_time_after_fix)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        nmea = ['GPGSV', 'BDGSV', 'GNGSA', 'GNVTG', 'GNRMC', 'GPGGA']
        for i in range(len(nmea)):
            test.log.step('Step 15.' + str(i + 1) + ': Check NMEA Data ' + nmea[i] + ' - Start')
            test.dut.dstl_collect_result('Step 15.' + str(i + 1) + ': Check NMEA Data ' + nmea[i], test.dut.dstl_find_nmea_data(nmea_data, nmea[i]))

        nmea = ['GLGSV', 'GAGSV']
        for i in range(len(nmea)):
            test.log.step('Step 15.' + str(i + 7) + ': Check NMEA Data ' + nmea[i] + ' is invisible - Start')
            test.dut.dstl_collect_result('Step 15.' + str(i + 7) + ': Check NMEA Data ' + nmea[i]+ ' is invisible', not test.dut.dstl_find_nmea_data(nmea_data, nmea[i]))

        test.log.step('Step 16: Disable NMEA for Beidou - Start')
        test.dut.dstl_collect_result('Step 16: Disable NMEA for Beidou', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Beidou\",\"off\""))

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 17: Check NMEA Data BDGSV is invisible - Start')
        test.dut.dstl_collect_result('Step 17: Check NMEA Data BDGSV is invisible', not test.dut.dstl_find_nmea_data(nmea_data, "BDGSV"))

        test.log.step('Step 18: Enable NMEA for Beidou - Start')
        test.dut.dstl_collect_result('Step 18: Enable NMEA for Beidou', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Beidou\",\"on\""))

        test.log.step('Step 19.1: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 19.1: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 19.2: Disable Beidou system - Start')
        test.dut.dstl_collect_result('Step 19.2: Disable Beidou system', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/Beidou\",\"0\""))

        test.log.step('Step 19.3: restart module- Start')
        test.dut.dstl_collect_result('Step 19.3: restart module', test.dut.dstl_restart())

        test.log.step('Step 20.1: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 20.1: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 20.2: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 20.2: Wait for first fix position', test.dut.nmea.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100) is True)

        test.sleep(sleep_time_after_fix)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 21.1:Check NMEA Data GPGSV - Start')
        test.dut.dstl_collect_result('Step 21.1: Check NMEA Data GPGSV', test.dut.dstl_find_nmea_data(nmea_data, "GPGSV"))

        test.log.step('Step 21.2:Check NMEA Data GLGSV - Start')
        test.dut.dstl_collect_result('Step 21.2: Check NMEA Data GLGSV', test.dut.dstl_find_nmea_data(nmea_data, "GLGSV"))


    def cleanup(test):
        test.log.step('Step 22: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 22: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        if test.smbv_active == True:
            test.smbv.dstl_smbv_switch_on_all_system()
            test.smbv.dstl_smbv_close()

        test.log.step('Step 23: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 23: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
