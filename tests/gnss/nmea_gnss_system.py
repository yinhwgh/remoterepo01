"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0093789.001 - TcNMEAGnssSystem
intention: A  check if the NMEA output will be configured by AT command, available output configurations are:
                          sgpsc=nmea/gps,
                          sgpsc=nmea/glonass,
                          sgpsc=nmea/galileo,
                          sgpsc=nmea/beidou
                          sgpsc=nmea/qzss
           and if the following sentences are configurable by this AT command:
                        - NMEA sentences for GPS: GP
                        - NMEA sentences for Glonass:  GL
                        - NMEA sentences for Galileo: GA
                        - NMEA sentences for Beidou: BD
                        - NMEA sentences for QZSS: QZ
LM-No (if known):     LM0004980.001 - Selection of Supported GNSS Systems
                      LM0006731.003 - GNSS: Configurable Output of NMEA Sentences - Bobcat
                      LM0006731.004 - GNSS: Configurable Output of NMEA Sentences - Viper

used eq.: DUT-At1, SMBV (sometimes also roof antenna works)
execution time (appr.): 18 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *

class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        takler_ids = test.dut.dstl_get_talker_ids()
        GNSS_satelite = ['GPS', 'Glonass', 'Galileo', 'Beidou', 'Qzss']
        GNSS = [
        ["on", "off", "off", "off", "off"],
        ["off", "on", "off", "off", "off"],
        ["off", "off", "on", "off", "off"],
        ["off", "off", "off", "on", "off"],
        ["off", "off", "off", "off", "on"]
        ]
        result = ["",""]

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 3: Start cold start - Start')
        test.dut.dstl_collect_result('Step 3: Start cold start', test.dut.dstl_coldstart())

        test.log.step('Step 4: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 4: Wait for first fix position', test.dut.dstl_check_ttff() != 0)

        test.sleep(420)

        test.log.step('Step 5: Wait for all satellite system will be tracked - Start')
        test.dut.dstl_collect_result('Step 5: Wait for all satellite system will be tracked',  test.dut.nmea.wait_for('.*AAAAA.*', 180)!= 0)

        test.log.step('Step 6: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 6: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        for i in range(len(takler_ids)):
            test.log.step('Step 7.' + str(i) + '.0: ' + GNSS_satelite[i] + ' Test - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i) + '.0: ' + GNSS_satelite[i] + ' Test Start', True)
            for sat in range(len(takler_ids)):
                test.log.step('Step 7.'+str(i)+'.'+str(sat+1)+': set NMEA ' + GNSS_satelite[sat] +' '+ GNSS[i][sat] + ' - Start')
                test.dut.dstl_collect_result('Step 7.'+str(i)+'.'+str(sat+1)+': set NMEA ' + GNSS_satelite[sat] +' '+ GNSS[i][sat],
                            test.dut.at1.send_and_verify('at^sgpsc=\"Nmea/' + GNSS_satelite[sat] + '\",\"' + GNSS[i][sat] + '\"', ".*OK.*") and
                            test.dut.at1.send_and_verify('at^sgpsc=\"Nmea/' + GNSS_satelite[sat] + '\"', '.*\"Nmea/' + GNSS_satelite[sat] + '\",\"' + GNSS[i][sat] + '\".*OK.*'))

            test.dut.at1.send_and_verify('at^sgpsc?', '.*OK.*')

            test.log.step('Step 8.'+str(i)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 8.'+str(i)+': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.sleep(5)

            test.log.step('Step 9.'+str(i)+': Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 9.'+str(i)+': Wait for first fix position', test.dut.dstl_check_ttff() != 0)

            test.dut.nmea.read()
            test.sleep(5)
            gnss_data = test.dut.nmea.read()

            test.log.step('Step 10.' + str(i) + ': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 10.' + str(i) + ': Switch off GNSS engine',
                                         test.dut.dstl_switch_off_engine())

            test.log.step('Step 11.' + str(i) + '.0: find ' + GNSS_satelite[i] + ' ID-Takler - Start')
            test.dut.dstl_collect_result('Step 11.' + str(i) + '.0: find ' + GNSS_satelite[i] + ' ID-Takler', True)

            for n in range(1,6):
                test.log.step('Step 11.' + str(i) + '.' + str(n) + ': ' + GNSS_satelite[n-1] + ' ID-Takler - Start')
                result = test.dut.dstl_find_nmea_data_response(gnss_data, takler_ids[n - 1]+'GSV')
                print(str(n)+"  !=  "+str(i))
                if n != (i+1):
                    test.dut.dstl_collect_result('Step 11.' + str(i) + '.' + str(n) + ': ' + GNSS_satelite[n-1] + ' ID-Takler: ' + result[1], not result[0])
                else:
                    test.dut.dstl_collect_result('Step 11.' + str(i) + '.' + str(n) + ': ' + GNSS_satelite[n-1] + ' ID-Takler: ' + result[1], result[0])

    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 13: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 12: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())
        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
