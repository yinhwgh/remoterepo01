"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0107179.001 - Gnss_US_Territory_Galileo_Beidou
Jira:
intention:  Check, that Galileo and Beidou are not active over US territory, when AT^SGPSC=Engine/Galileo was set to 1.
            If it's set to 2, it should be active anyway.
LM-No (if known):
used eq.: DUT-At1, NMEA-port, SMBV
execution time (appr.): 25 min
"""


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *

GNSS_SYSTEM = {"Gl+Ga":          {"Glonass": "AAN", "Galileo": "ANA"},
               "Gl+Ga+Bei":      {"Glonass": "AANN", "Galileo": "ANAN", "Beidou": "ANNA"},
               "Gl+Ga+Bei+QZSS": {"Glonass": "AANNN", "Galileo": "ANANN", "Beidou": "ANNAN", "QZSS": "ANNNA"}
               }


class Test(BaseTest):
    res = {}
    resOkError = {}

    def setup(test):
        err_text = 'no SMBV found -> stop testcase'
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna(smbv_required=True)
        if not test.smbv_active:
            err_text_plugin = 'network_instrument plugin NOT installed/active or no SMBV found -> stop testcase !!!'
            all_results.append([err_text_plugin, 'FAILED'])
            test.log.error(err_text_plugin)
            test.expect(False, critical=True)

        test.log.com("Setting SMBV")
        test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        #        error_counter = 0
        #        maxTimeForFix = 32
        #        loop_no = 1  # number loops to be checked
        GNSS_ind = {}
        GNSS_mod_ind = ''
        GNSS_mod_ind_us = ''
        #        timeDatafound = -1

        if test.dut.project == 'BOBCAT':
            GNSS_ind = GNSS_SYSTEM['Gl+Ga+Bei+QZSS']
            GNSS_mod_ind = ['AAAAA','AANNA']
            #GNSS_mod_ind_us = 'ANNNN'
        elif test.dut.project == 'MIAMI':
            GNSS_ind = GNSS_SYSTEM['Gl+Ga']
            GNSS_mod_ind = ['AAA','ANN']
            #GNSS_mod_ind_us = 'ANN'
        # elif test.dut.project == 'SERVAL':    # Serval did not have coldstart feature
        #     GNSS_ind = GNSS_SYSTEM['Gl+Ga+Bei']
        #     GNSS_mod_ind = 'AAAA'
        #     GNSS_mod_ind_us = 'ANNN'
        elif test.dut.project == 'VIPER':
            GNSS_ind = GNSS_SYSTEM['Gl+Ga+Bei+QZSS']
            GNSS_mod_ind = ['AAAAA','AANNA']
            #GNSS_mod_ind_us = 'ANNNN'
        else:
            test.log.warning('DIF: project: ' + test.dut.project + ' not configured')

        test.expect(test.dut.dstl_switch_off_engine())

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Start coldstart, switch on engine, and wait for fix - Start')
        test.dut.dstl_collect_result('Step 2: Start coldstart, switch on engine, and wait for fix', test.dut.dstl_coldstart_and_waitfor_fix())
        test.dut.nmea.read()

        test.log.step('Step 3: Check mod-indicators of all systems - Start')
        a = test.dut.dstl_waitfor_nmea_data_response('.*AAAAA.*', maxtime=300)

        result = test.dut.dstl_mode_indicator(a)

        test.dut.dstl_collect_result('Step 3: Check mod-indicators of all systems. result: '+str(result), result == GNSS_mod_ind[0])

        test.log.step('Step 4: Change location to New York at simulator - Start')
        test.dut.dstl_switch_off_engine()
        test.smbv.dstl_smbv_change_location("New York")
        test.dut.dstl_collect_result('Step 4: Change location to New York at simulator', True)

        test.log.step('Step 5: Cold start, switch on engine and wait for fix position - Start')
        test.dut.dstl_collect_result('Step 5: Cold start, switch on engine and wait for fix position',test.dut.dstl_coldstart_and_waitfor_fix())

        test.dut.dstl_waitfor_nmea_data(nmea_data='.*GNGNS.*,' + GNSS_mod_ind[1] + ',.*', maxtime=300)
        test.dut.nmea.read()
        test.sleep(5)
        data = test.dut.nmea.read()
        ind = test.dut.dstl_mode_indicator(data)

        test.log.step('Step 6.1: Check NMEA data, Galileo must invisible now - Start')
        test.dut.dstl_collect_result('Step 6: Check NMEA data, Galileo  must invisible now: ' + ind, ind[2] == 'N')

        test.log.step('Step 6.2: Check NMEA data, Beidou must invisible now - Start')
        test.dut.dstl_collect_result('Step 6: Check NMEA data, Beidou must invisible now: ' + ind, ind[3] == 'N')

        test.log.step('Step 7: Change Galileo and Beidou capability to worldwide - Start')
        test.dut.dstl_collect_result('Step 7: Change Galileo and Beidou capability to worldwide',  test.dut.at1.send_and_verify('at^sgpsc=engine/galileo,2' , '^SGPSC: \"Engine/Galileo\",\"2\"') and test.dut.at1.send_and_verify('at^sgpsc=engine/beidou,2' , '^SGPSC: \"Engine/Beidou\",\"2\"'))

        test.log.step('Step 8: Start coldstart, switch on engine, and wait for fix - Start')
        test.dut.dstl_restart()
        test.dut.dstl_collect_result('Step 8: Start coldstart, switch on engine, and wait for fix', test.dut.dstl_coldstart_and_waitfor_fix())
        test.sleep(120)
        test.dut.nmea.read()
        test.sleep(5)
        test.log.step('Step 9: Check NMEA data, Galileo and Beidou must visible now - Start')
        data = test.dut.nmea.read()
        ind = test.dut.dstl_mode_indicator(data)
        test.dut.dstl_collect_result('Step 9.1: Check NMEA data, Galileo  must visible now: ' + ind, ind[2] == 'A')
        test.dut.dstl_collect_result('Step 9.2: Check NMEA data, beidou  must visible now: ' + ind, ind[3] == 'A')
        '''
        if test.dut.dstl_find_nmea_data(data, "GNGNS", "AAAAA", 6):
            test.dut.dstl_collect_result('Step 9: Check NMEA data, Galileo and Beidou must visible now', True)
        else:
            ind = test.dut.dstl_mode_indicator(data)
            test.dut.dstl_collect_result('Step 9: Check NMEA data, Galileo and Beidou must visible now: '+str(ind), False)
        '''
    def cleanup(test):

        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 10: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 10: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 11: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 11: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

        pass

if "__main__" == __name__:
    unicorn.main()
