"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096103.001 - GOST33471
intention:  Testing requirement from GOST 33471-2015
            At-Command like coldstart, change elevation angle (5-45), GPS+Glonass, Pz90 must be supported
LM-No (if known): LM0005180 - Conformity declaration according to GOST 33471 - 2015
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
        test.dut.dstl_detect()

    def run(test):

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.info("***** pz90 test *****")
        Pz90 = ["on", "off"]
        for i in range(len(Pz90)):
            test.log.step('Step 2.'+str(i)+': Configures support for the PZ-90 Geodetic Reference System to '+Pz90[i]+' - Start')
            test.dut.dstl_collect_result('Step 2.'+str(i)+': Configures support for the PZ-90 Geodetic Reference System to '+Pz90[i],
                                         test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/PZ90\",\""+Pz90[i]+ "\"",".*OK.*"))

            test.log.step('Step 3.'+str(i)+': Restart Module - Start')
            test.dut.dstl_collect_result('Step 3.'+str(i)+': Restart Module', test.dut.dstl_restart())

            test.log.step('Step 4.'+str(i)+': Verify parameter setting is non-volatile '+Pz90[i]+' - Start')
            test.dut.dstl_collect_result('Step 4.'+str(i)+': Verify parameter setting is non-volatile '+Pz90[i],
                                         test.dut.at1.send_and_verify("at^sgpsc?",".*\"Nmea/PZ90\",\""+Pz90[i]+"\".*"))

            test.log.step('Step 5.'+str(i)+': Perform cold start - Start')
            test.dut.dstl_collect_result('Step 5.'+str(i)+': Perform cold start', test.dut.dstl_coldstart())

            test.log.step('Step 6.'+str(i)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 6.'+str(i)+': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.log.step('Step 7.'+str(i)+': Wait for first fix position and check time for cold start - Start')
            test.dut.dstl_collect_result('Step 7.'+str(i)+': Wait for first fix position and check time for cold start ', test.dut.dstl_check_ttff() < 35)
            test.sleep(20)

            test.dut.nmea.read()
            test.sleep(5)
            nmea_data = test.dut.nmea.read()

            test.log.step('Step 8.'+str(i)+': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 8.'+str(i)+': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            if Pz90[i] == "on":
                test.log.step('Step 9.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Local datum code P90 - Start')
                test.dut.dstl_collect_result('Step 9.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Local datum code P90', test.dut.dstl_find_nmea_data(nmea_data,"GNDTM","P90", 1))

                test.log.step('Step 10.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Datum name W84 - Start')
                test.dut.dstl_collect_result('Step 10.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Datum name W84', test.dut.dstl_find_nmea_data(nmea_data, "GNDTM","W84", 8))
            else:
                test.log.step('Step 9.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Local datum code W84 - Start')
                test.dut.dstl_collect_result('Step 9.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Local datum code W84', test.dut.dstl_find_nmea_data(nmea_data, "GNDTM", "W84", 1))

                test.log.step('Step 10.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Datum name W84 - Start')
                test.dut.dstl_collect_result('Step 10.'+str(i)+': PZ90='+Pz90[i]+' find_nmea_data Datum name W84', test.dut.dstl_find_nmea_data(nmea_data, "GNDTM", "W84", 8))


        test.log.step('Step 11: Specifies the frequency of position requests to 10 - Start')
        test.dut.dstl_collect_result('Step 11: Specifies the frequency of position requests to 10', test.dut.at1.send_and_verify("at^SGPSC=\"Nmea/Freq\",\"10\"",".*OK.*"))

        test.log.step('Step 12: Configures the Minimum GNSS Elevation Angle to 25 - Start')
        test.dut.dstl_collect_result('Step 12: Configures the Minimum GNSS Elevation Angle to 25', test.dut.at1.send_and_verify("at^sgpsc=\"Sens/MinElevAngle\",\"25\"",".*OK.*"))

        test.log.step('Step 13: Restart Module - Start')
        test.dut.dstl_collect_result('Step 13: Restart Module ', test.dut.dstl_restart())

        test.log.step('Step 14: Verify parameter setting of Nmea/Freq after restart (should be 1) - Start')
        test.dut.dstl_collect_result('Step 14: Verify parameter setting of Nmea/Freq after restart (should be 1)', test.dut.at1.send_and_verify("at^sgpsc?",".*\"Nmea/Freq\",\"1\".*OK.*"))

        test.log.step('Step 15: Verify parameter setting of Sens/MinElevAngle after restart (should be 25) - Start')
        test.dut.dstl_collect_result('Step 15: Verify parameter setting setting of Sens/MinElevAngle after restart (should be 25)', test.dut.at1.send_and_verify("at^sgpsc?",".*\"Sens/MinElevAngle\",\"25\".*OK.*"))

    def cleanup(test):
        test.log.step('Step 16: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 16: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

if "__main__" == __name__:
    unicorn.main()
