"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0104213.001 - GNSS_Powersave
intention:  Activates Sleep mode for the GNSS
LM-No (if known): LM0003030 - Power Saving Configuration of GPS-Engine
used eq.: DUT-At1
execution time (appr.): 2 min
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

        test.log.step('Step 2: Cnfigure sbas parameter - Start')
        test.dut.dstl_collect_result('Step 2: Configure sbas parameter', test.dut.at1.send_and_verify("At^sgpsc=\"nmea/sbas\",\"on\"","OK"))

        test.log.step('Step 3: Configure powersave parameter ERROR expected - Start')
        test.dut.dstl_collect_result('Step 3: Configure powersave parameter ERROR expected', test.dut.at1.send_and_verify("at^SGPSC= \"Power/Psm\",\"1\"","ERROR"))


        test.log.step('Step 4: Configure sbas parameter to off - Start')
        test.dut.dstl_collect_result('Step 4: configure sbas parameter to off', test.dut.at1.send_and_verify("at^sgpsc=\"nmea/sbas\",\"off\"", "OK"))

        test.log.step('Step 5: Configure nmea data format parameter to nmea - Start')
        test.dut.dstl_collect_result('Step 5: Configure nmea data format parameter to nmea', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Data/Format\",\"Nmea\"","OK"))

        test.log.step('Step 6: Configure drsync parameter to off - Start')
        test.dut.dstl_collect_result('Step 6: Configure drsync parameter to off', test.dut.at1.send_and_verify("at^sgpsc=\"nmea/drsync\",\"off\"", "OK"))

        test.log.step('Step 7: Configure nmea frequency parameter to 1 - Start')
        test.dut.dstl_collect_result('Step 7: Configure nmea frequency parameter to 1', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Freq\",\"1\"", "OK"))

        test.log.step('Step 8: Increase the frequency of position requests to 1000 - Start')
        test.dut.dstl_collect_result('Step 8: Increase the frequency of position requests to 1000', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/FreqMs\",\"1000\"", "OK"))

        test.log.step('Step 9: Activate powersave parameter (set to 1) - Start')
        test.dut.dstl_collect_result('Step 9: Activate powersave parameter to (set to 1)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"1\"", "OK"))

        test.log.step('Step 10: Restart Module - Start')
        test.dut.dstl_collect_result('Step 10: Restart Module', test.dut.dstl_restart())

        test.log.step('Step 11: Check powersave parameter after restart - Start')
        test.dut.dstl_collect_result('Step 11: Check powersave parameter after restart', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\"", ".*1.*OK.*"))

        test.log.step('Step 12: Deactivate powersave parameter (set to 0) - Start')
        test.dut.dstl_collect_result('Step 12: Deactivate powersave parameter (set to 0)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"0\"", "OK"))
        
    def cleanup(test):
        test.log.step('Step 13: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 13: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

    if "__main__" == __name__:
        unicorn.main()
