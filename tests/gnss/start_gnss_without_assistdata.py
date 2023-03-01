"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105084.001 - StartGnssWithoutAssistdata
intention:  Start GNSS without assisted data. TTFF will take 1/27/29 (hot/warm/cold), depends on last fix position
LM-No (if known): LM0007083.001
used eq.: DUT-At1, NMEA-port, roof Antenna
execution time (appr.): 2 min
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
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):
        read_time_after_clear_buffer = 10
        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        test.log.step('Step 2: Configure GNSS operation to higher priority than LTE  - Start')
        test.dut.dstl_collect_result('Step 2: Configure GNSS operation to higher priority than LTE ', test.dut.at1.send_and_verify("at^scfg=\"MEopMode/RscMgmt/Rrc\",\"1\"", "OK"))

        test.log.step('Step 3: Configure GNSS start mode without assistance data - Start')
        test.dut.dstl_collect_result('Step 3: Configure GNSS start mode without assistance data', test.dut.at1.send_and_verify("at^sgpsc=\"Engine/StartMode\",\"0\"", "OK"))

        test.log.step('Step 4: restart module - Start')
        test.dut.dstl_collect_result('Step 4: Restart module', test.dut.dstl_restart())

        test.log.step('Step 5: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 5: Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))

        token=time.time()
        test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100)
        ttff =time.time()-token

        test.log.step('Step 6: Determine TTFF 3/35 sec (hot/warm/cold): '+str(ttff)+' - Start')
        test.dut.dstl_collect_result('Step 6: Determine TTFF 3/35 sec (hot/warm/cold): '+str(ttff), ttff <35)

        test.sleep(5)
        test.dut.nmea.read()
        test.sleep(read_time_after_clear_buffer)
        nmea_data = test.dut.nmea.read()

        test.log.step('Step 7.1: Check NMEA Data GPGSV (GPS) is visible- Start')
        test.dut.dstl_collect_result('Step 7.1: Check NMEA Data GPGSV (GPS) is visible', test.dut.dstl_find_nmea_data(nmea_data, "GPGSV"))

        test.log.step('Step 7.2: Check NMEA Data GLGSV (Glonass) is visible- Start')
        test.dut.dstl_collect_result('Step 7.2: Check NMEA Data GLGSV (Glonass) is visible', test.dut.dstl_find_nmea_data(nmea_data, "GLGSV"))

        test.log.step('Step 7.3: Check NMEA Data G[NP]GSA is visible- Start')
        test.dut.dstl_collect_result('Step 7.3: Check NMEA Data G[NP]GSA is visible', test.dut.dstl_find_nmea_data(nmea_data, "G[NP]GSA"))

        test.log.step('Step 7.4: Check NMEA Data G[NP]VTG is visible- Start')
        test.dut.dstl_collect_result('Step 7.4: Check NMEA Data G[NP]VTG is visible', test.dut.dstl_find_nmea_data(nmea_data, "G[NP]VTG"))

        test.log.step('Step 7.5: Check NMEA Data G[NP]RMC is visible- Start')
        test.dut.dstl_collect_result('Step 7.5: Check NMEA Data G[NP]RMC is visible', test.dut.dstl_find_nmea_data(nmea_data, "G[NP]RMC"))

        test.log.step('Step 7.6: Check NMEA Data G[NP]GGA is visible- Start')
        test.dut.dstl_collect_result('Step 7.6: Check NMEA Data G[NP]GGA is visible', test.dut.dstl_find_nmea_data(nmea_data, "G[NP]GGA"))


    def cleanup(test):
        test.log.step('Step 8: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 8: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
