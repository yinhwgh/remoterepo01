"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0088024.001 - GpsDeadReckoning
intention:  Check additional NMEA data for GPS and Glonass system, if deadreckoning is on
LM-No (if known): LM0003351.xxx - Automotive Dead Reckoning (DR) Support
used eq.: DUT-At1, roof antenna
execution time (appr.): 5 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.auxiliary.restart_module import dstl_restart

class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.smbv = SMBV(test.plugins.network_instrument)

        if test.smbv.dstl_check_smbv():
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()
        else:
            test.log.com("Roof Antenna has to be  used")
        test.dut.dstl_detect()
        
    def run(test):
        nmea_sentences=[
        "PCWMV",
        "GPZDA",
        "GPGRS"
        ]

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 3: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 3: Wait for first fix position', test.dut.dstl_check_ttff() != 0)

        test.sleep(40)

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        dead_Reck = ["on", "off"]
        for i in range(len(dead_Reck)):
            test.log.step('Step 5.' + str(i) + ': Configure Dead Reckoning to ' + dead_Reck[i] + ' - Start')
            test.dut.dstl_collect_result('Step 5.' + str(i) + ': Configure Dead Reckoning to ' + dead_Reck[i], test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/DeadReckoning\",\""+dead_Reck[i]+"\"",".*OK.*"))

            test.log.step('Step 6' + str(i) + ': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 6.' + str(i) + ': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.dut.nmea.read()
            test.sleep(5)
            nmea_data = test.dut.nmea.read()

            test.log.step('Step 7' + str(i) + ': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i) + ': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            for m in range(len(nmea_sentences)):
                if dead_Reck[i] == "on":
                    test.log.step('Step 8.' + str(i) + '.' + str(m) + ': Check nmea_sentence ' + nmea_sentences[m] + ' (should be available) - Start')
                    test.dut.dstl_collect_result('Step 8.' + str(i) + '.' + str(m) + ': Check nmea_sentence ' + nmea_sentences[m] + ' (should be available)',
                                                 test.dut.dstl_find_nmea_data(nmea_data, nmea_sentences[m]))
                else:
                    test.log.step('Step 9.' + str(i) + '.' + str(m) + ': Check nmea_sentence ' + nmea_sentences[m] + ' (should be not available) - Start')
                    test.dut.dstl_collect_result('Step 9.' + str(i) + '.' + str(m) + ': Check nmea_sentence ' + nmea_sentences[m] + ' (should be not available)',
                                                 not test.dut.dstl_find_nmea_data(nmea_data, nmea_sentences[m]))

    def cleanup(test):
        if test.smbv.dstl_check_smbv():
            test.smbv.dstl_smbv_close()

        test.log.step('Step 10: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 10: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

if "__main__" == __name__:
    unicorn.main()
