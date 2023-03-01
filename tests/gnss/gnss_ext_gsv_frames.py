"""
author: duangkeo.krueger@thalesgroup.com, katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC0094156.001 - ExtendedGSVFrames
intention: Testing the support of  the output of decimals in GSV elements Elevation, Azimuth, SNR/CN0.
LM-No (if known): LM0006731.004 - GNSS: Configurable Output of NMEA Sentences
used eq.: DUT-At1, DUT-Nmea
execution time (appr.): 4 minutes

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.auxiliary.devboard.devboard import *

class Test(BaseTest):
    sgpse_available = False
    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        test.dut.dstl_switch_off_engine()
        test.log.step('Step 1: Configure GNSS to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Configure GNSS to default setting', test.dut.dstl_init_gnss())

        # check NMEA ExtGSV = off
        test.log.step('Step 2: Switch off NMEA ExtGSV  - Start')
        test.dut.dstl_collect_result('Step 2: Switch off NMEA ExtGSV', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/ExtGSV\",\"off\"", ".*OK.*"))

        test.log.step('Step 3: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 3: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 4: Wait for fix position - Start')
        test.dut.dstl_collect_result('Step 4: Wait for fix position', test.dut.dstl_check_ttff() != 0, True)
        test.sleep(30)

        nmea_data = test.dut.nmea.read()
        #test.log.com('nmea_data\n' + nmea_data)

        test.log.step('Step 5: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 5: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 6: Check if no decimals in GSV elements Elevation, Azimuth, SNR - Start')
        test.dut.dstl_collect_result('Step 6: Check if no decimals in GSV elements Elevation, Azimuth, SNR', test.dut.dstl_check_extended_gsv_frames(nmea_data, extended_gsv=False))


        # check NMEA ExtGSV = on
        test.log.step('Step 7: Switch on NMEA ExtGSV  - Start')
        test.dut.dstl_collect_result('Step 7: Switch on NMEA ExtGSV', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/ExtGSV\",\"on\"", ".*OK.*"))

        test.log.step('Step 8: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 8: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 9: Wait for fix position - Start')
        test.dut.dstl_collect_result('Step 9: Wait for fix position', test.dut.dstl_check_ttff() != 0, True)
        test.sleep(30)

        nmea_data = test.dut.nmea.read()
        #test.log.com('nmea_data\n' + nmea_data)

        test.log.step('Step 10: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 10: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 11: Check if decimals in GSV elements Elevation, Azimuth, SNR - Start')
        test.dut.dstl_collect_result('Step 11: Check if decimals in GSV elements Elevation, Azimuth, SNR', test.dut.dstl_check_extended_gsv_frames(nmea_data, extended_gsv=True))


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 12: Configure GNSS to default setting - Start')
        test.dut.dstl_collect_result('Step 12: Configure GNSS to default setting', test.dut.dstl_init_gnss())


        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
