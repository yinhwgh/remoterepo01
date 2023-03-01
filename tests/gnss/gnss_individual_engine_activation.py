"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096341.001 - GNSS_IndividualEngineActivation
Jira:
intention: The test will check, if the GNSS engines can be individually activated and delivering
           the expected NMEA output, when active. Also, there is a check, that Galileo is not active over US territory,
           when AT^SGPSC=Engine/Galileo was set to 1. If it's set to 2, it should be active anyway.
LM-No (if known): LM0006327.001 - Bobcat, Viper
used eq.: DUT-At1, NMEA-port, SMBV
execution time (appr.): 15 min
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

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
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
            GNSS_mod_ind = 'AAAAA'
            GNSS_mod_ind_us = 'ANNNN'
        elif test.dut.project == 'MIAMI':
            GNSS_ind = GNSS_SYSTEM['Gl+Ga']
            GNSS_mod_ind = 'AAA'
            GNSS_mod_ind_us = 'ANN'
        # elif test.dut.project == 'SERVAL':    # Serval did not have coldstart feature
        #     GNSS_ind = GNSS_SYSTEM['Gl+Ga+Bei']
        #     GNSS_mod_ind = 'AAAA'
        #     GNSS_mod_ind_us = 'ANNN'
        elif test.dut.project == 'VIPER':
            GNSS_ind = GNSS_SYSTEM['Gl+Ga+Bei+QZSS']
            GNSS_mod_ind = 'AAAAA'
            GNSS_mod_ind_us = 'ANNNN'
        else:
            test.log.warning('DIF: project: ' + test.dut.project + ' not configured')

        test.expect(test.dut.dstl_switch_off_engine())

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Start coldstart, switch on engine, and wait for fix - Start')
        test.dut.dstl_collect_result('Step 2: Start coldstart, switch on engine, and wait for fix', test.dut.dstl_coldstart_and_waitfor_fix())
        test.dut.nmea.read()

        test.log.step('Step 3: Check mod-indicators of all systems - Start')
        nmea_data = test.dut.dstl_waitfor_nmea_data_response(nmea_data='.*GNGNS.*,' + GNSS_mod_ind + ',.*', maxtime=60)
        print(nmea_data)
        print(nmea_data[1])
        result = test.dut.dstl_mode_indicator(nmea_data[1])
        test.dut.dstl_collect_result('Step 3: Check mod-indicators of all systems. result: '+str(result), True)

        test.log.step('Step 4: Switch Off all engines - Start')
        test.dut.dstl_collect_result('Step 4: Switch Off all engines', test.dut.dstl_switch_all_engines(state='off'))
        test.dut.nmea.read()
        test.sleep(1)

        i = 0
        for key, value in GNSS_ind.items():
            GNSS_sytem = key
            mode_indicator = value
            test.log.info('+++ Test ' + str(i+1) + ' ' + GNSS_sytem + ' - Start +++')
            test.dut.dstl_check_active_gnss_system(GNSS_sytem, mode_indicator, 5, (i + 1))
            test.log.info('+++ Test ' + str(i+1) + ' ' + GNSS_sytem + ' - End +++')
            i = i + 1


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 9: switch off GNSS engine, enable all GNSS systems and restart UE - Start')
        test.dut.dstl_collect_result('Step 9: switch off GNSS engine, enable all GNSS systems and restart UE',
                                     test.dut.dstl_switch_all_engines(state='on', restart=True))

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
