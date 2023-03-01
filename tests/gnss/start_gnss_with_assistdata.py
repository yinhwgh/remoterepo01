"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105085.001
intention:  Start GNSS with assistance data (Xtrafile)  TTFF will take < xx sec
LM-No (if known): LM0007083.001 - Serval
used eq.: DUT-At1, NMEA-port, roof Antenna
execution time (appr.): 2 min
"""

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
#from dstl.network_service import register_to_network
from dstl.network_service import attach_to_network
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *



class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):

        if test.dut.sim.umts_apn == '':
            if test.dut.sim.gprs_apn == '':
                test.log.error("No APN can be found for the SIM card in use. Please add umts_apn or gprs_apn field for the SIM card")
            else:
                apn = test.dut.sim.gprs_apn
        else:
            apn = test.dut.sim.umts_apn

        read_time_after_clear_buffer = 10
        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        test.log.step('Step 2: Configure GNSS operation to higher priority than LTE  - Start')
        test.dut.dstl_collect_result('Step 2: Configure GNSS operation to higher priority than LTE ', test.dut.at1.send_and_verify("at^scfg=\"MEopMode/RscMgmt/Rrc\",\"1\"", "OK"))

        test.log.step('Step 3: Configure GNSS start mode with assistance data - Start')
        test.dut.dstl_collect_result('Step 3: Configure GNSS start mode with assistance data', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/StartMode\",\"1\"", "OK"))

        test.log.step('Step 4: restart module - Start')
        test.dut.dstl_collect_result('Step 4: Restart module', test.dut.dstl_restart())
        test.sleep(5)

        test.log.step('Step 5: Register to network - Start')
        test.dut.dstl_collect_result('Step 5: Register to network', test.dut.dstl_register_to_network())

        test.log.step('Step 6: Set APN with at+cgdcont - Start')
        test.dut.dstl_collect_result('Step 6: Set APN with at+cgdcont', test.dut.at1.send_and_verify("at+cgdcont=1,\"IPV4V6\",\"" + apn + "\"", "OK"))

        if 'VZW' in test.dut.software:
            test.log.step('Step 6.1: Set APN with at^sgapn (internal AT-CMD) - Start')
            #D2_AE SIM by Nong
            #test.dut.at1.send_and_verify("at^sgapn=1,0,\"IPV4V6\",\"\",\"any\"", "OK")
            test.dut.dstl_collect_result('Step 6.1: Set APN with at^sgapn (internal AT-CMD)', test.dut.at1.send_and_verify("at^sgapn=1,0,\"IPV4V6\",\"" + apn + "\",\"any\"", "OK"))

        test.log.step('Step 7: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 7: Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

        token=time.time()
        test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100)
        ttff =time.time()-token

        test.log.step('Step 8: Determine TTFF 3/35 sec (hot/cold): '+str(ttff)+' - Start')
        test.dut.dstl_collect_result('Step 8: Determine TTFF 3/35 sec (hot/cold): '+str(ttff), ttff <35)

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 9.1: Check NMEA Data GPGSV (GPS) is visible- Start')
        test.dut.dstl_collect_result('Step 9.1: Check NMEA Data GPGSV (GPS) is visible', test.dut.dstl_find_nmea_data(nmea_data, "GPGSV"))

        test.log.step('Step 9.2: Check NMEA Data GLGSV (Glonass) is visible- Start')
        test.dut.dstl_collect_result('Step 9.2: Check NMEA Data GLGSV (Glonass) is visible', test.dut.dstl_find_nmea_data(nmea_data, "GLGSV"))

        test.log.step('Step 9.3: Check NMEA Data GNGSA is visible- Start')
        test.dut.dstl_collect_result('Step 9.3: Check NMEA Data GNGSA is visible', test.dut.dstl_find_nmea_data(nmea_data, "GNGSA"))

        test.log.step('Step 9.4: Check NMEA Data GNVTG is visible- Start')
        test.dut.dstl_collect_result('Step 9.4: Check NMEA Data GNVTG is visible', test.dut.dstl_find_nmea_data(nmea_data, "GNVTG"))

        test.log.step('Step 9.5: Check NMEA Data GNRMC is visible- Start')
        test.dut.dstl_collect_result('Step 9.5: Check NMEA Data GNRMC is visible', test.dut.dstl_find_nmea_data(nmea_data, "GNRMC"))

        test.log.step('Step 9.6: Check NMEA Data G[NP]GGA is visible- Start')
        test.dut.dstl_collect_result('Step 9.6: Check NMEA Data G[NP]GGA is visible', test.dut.dstl_find_nmea_data(nmea_data, "G[NP]GGA"))

    def cleanup(test):
        test.log.step('Step 10: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 10: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 11: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 11: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
