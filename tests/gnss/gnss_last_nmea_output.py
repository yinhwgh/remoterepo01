"""
author: duangkeo.krueger@thalesgroup.com, katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC0105538.001    - GnssLastNmeaOutput
intention: To query any time only one  NMEA sentence (containing the sentences of GSA,VTG,RMC,GGA and GSV)
LM-No (if known): LM0006731.005 - GNSS: Configurable Output of NMEA Sentences
used eq.: DUT-At1, DUT-Nmea
execution time (appr.):  14 minutes

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
            #test.smbv.dstl_smbv_switch_on_all_system()
            test.smbv.dstl_smbv_switch_on_gps_glonass_systems()

        test.dut.dstl_detect()

    def run(test):
        wait_time_60sec = 60
        wait_time_45sec = 45
        nmea = ['GSA', 'VTG', 'RMC', 'GGA', 'GSV']

        if (test.dut.project == 'BOBCAT' and test.dut.step == '2|3') or test.dut.project == 'VIPER':
            test.sgpse_available = True

        test.dut.dstl_switch_off_engine()
        test.log.step('Step 1: Configure GNSS to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Configure GNSS to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Activate URC for position fix notification  - Start')
        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=1", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 1,.*OK.*")
        test.dut.dstl_collect_result('Step 2: Activate URC for position fix notification', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"on\"", ".*OK.*"))

        test.log.step('Step 3: Switch off NMEA output  - Start')
        test.dut.dstl_collect_result('Step 3: Switch off NMEA output', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/Output\",\"off\"", ".*OK.*"))

        test.log.step('Step 4: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        data = test.dut.at1.last_response
        test.log.com('last response data\n' + data)
        data1 = test.dut.at1.read()
        test.log.com('last response data1\n' + data1)

        if ("SGPSE: 1,1" in data) or ("SGPSE: 1,1" in data1):
            test.log.com('COM: last response after SGPSE: 1,1 in data (=last_response)')
            test.dut.dstl_collect_result('Step 5: Wait position fix notification ', True)
        else:
            test.dut.dstl_collect_result('Step 5: Wait position fix notification', test.dut.at1.wait_for("SGPSE: 1,1", timeout=120))

        test.sleep(5)

        for n in range(10):
            test.log.step('Step 6 (loop '+str(n+1)+'): Read only one NMEA sentence - Start')
            test.dut.dstl_collect_result('Step 6 (loop '+str(n+1)+'): Read only one NMEA sentence', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Output\",\"last\"", ".*OK.*"))

            data = test.dut.at1.last_response

            for i in range(len(nmea)):
               test.log.step('Step 6.' + str(i + 1) + ' (loop '+str(n+1)+'): Check NMEA Data ' + nmea[i] + ' - Start')
               test.dut.dstl_collect_result('Step 6.' + str(i + 1) + ' (loop '+str(n+1)+'): Check NMEA Data ' + nmea[i], test.dut.dstl_find_nmea_data(data, nmea[i]))

            test.log.com('Wait ' + str(wait_time_60sec)  + ' seconds')
            test.sleep(wait_time_60sec)

        test.log.step('Step 7: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 7: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.com('Wait ' + str(wait_time_60sec)  + ' seconds')
        test.sleep(wait_time_60sec)

        data = test.dut.at1.last_response
        test.log.com('last response data\n' + data)
        data1 = test.dut.at1.read()
        test.log.com('last response data1\n' + data1)

        test.log.step('Step 8: Wait for GNSS event notification - Start')
        if test.dut.project == 'SERVAL' and test.dut.step == '3':
            test.dut.dstl_collect_result('Step 8: Wait for GNSS event notification - For Serval_03: GNSS event notification does not occur (see SRV03-1333)', True)
        else:
            if ("SGPSE: 1,0" in data) or ("SGPSE: 1,0" in data1):
                test.log.com('COM: last response after SGPSE: 1,0 in data (=last_response)')
                test.dut.dstl_collect_result('Step 8: Wait for GNSS event notification', True)
            else:
                test.dut.dstl_collect_result('Step 8: Wait for GNSS event notification', test.dut.at1.wait_for("SGPSE: 1,0", timeout=60))

        test.log.com('Wait ' + str(wait_time_45sec) + ' seconds')
        test.sleep(wait_time_45sec)

        test.log.step('Step 9: Read only one NMEA sentence - Start')
        test.dut.dstl_collect_result('Step 9: Read only one NMEA sentence', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Output\",\"last\"", ".*OK.*"))

        data = test.dut.at1.last_response

        for i in range(len(nmea)):
            test.log.step('Step 9.' + str(i + 1) + ': Check NMEA Data ' + nmea[i] + ' - Start')
            test.dut.dstl_collect_result('Step 9.' + str(i + 1) + ': Check NMEA Data ' + nmea[i], test.dut.dstl_find_nmea_data(data, nmea[i]))


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.dut.dstl_switch_off_engine()
        test.log.step('Step 10: Configure GNSS to default setting - Start')
        test.dut.dstl_collect_result('Step 10: Configure GNSS to default setting', test.dut.dstl_init_gnss())

        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=0", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 0,.*OK.*")

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
