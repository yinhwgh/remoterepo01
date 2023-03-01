"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number:  TC0107078.001 - gnss_power_antenna
intention:  Check Antenna power supply
            With an AT command the GPS antenna power supply can be configured (on, off and auto).
LM-No (if known): LM0007727.001 - GNSS configuration with Antenna Feeding/Diagnostic Support - Viper
used eq.: DUT-At1, myBlox-antenna has to be used, only McTest3 is working (01.09.2020, myBlox-GPS antenna on GPS connection)
execution time (appr.): 2:30 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *


class Test(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

        try:
            test.mctest_present = test.dut.devboard.send_and_verify("MC:VBATT", "OK")
        except Exception as e:
            test.mctest_present = False

        if test.mctest_present == False:
            err_text = 'no McTest available -> stop testcase !!!'
            all_results.append([err_text, 'FAILED'])
            test.log.error(err_text)
            test.expect(False, critical=True)

    def run(test):

        if test.mctest_present:
            test.dut.dstl_switch_off_at_echo(serial_ifc=0)
            test.dut.dstl_switch_off_at_echo(serial_ifc=1)

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\",\"auto\"","OK")

        test.log.step('Step 2: Check power antenna - Start')
        test.dut.dstl_collect_result('Step 2: Check power antenna', test.dut.at1.send_and_verify("at^sgpsc?","\"Power/Antenna\",\"auto\""))

        test.log.step('Step 3: Check with MCTEST for VGPS - Start')
        test.dut.dstl_collect_result('Step 3: Check with MCTEST for VGPS (=0)', test.dut_devboard.send_and_verify("mc:vgps","VGPS: 0"))

        test.log.step('Step 4: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 5: Check with MCTEST for VGPS - Start')
        test.dut.dstl_collect_result('Step 5: Check with MCTEST for VGPS (=1)', test.dut_devboard.send_and_verify("mc:vgps", "VGPS: 1"))

        test.log.step('Step 6: Start cold start - Start')
        test.dut.dstl_collect_result('Step 6: Start cold start', test.dut.dstl_coldstart())

        test.dut.nmea.read()
        test.log.step('Step 7: Wait for fix position - Start')
        test.dut.dstl_collect_result('Step 7: Wait for fix position', test.dut.dstl_check_ttff(120) > 20)

        test.log.step('Step 8: Set power antenna to off - Start')
        test.dut.dstl_collect_result('Step 8: Set power antenna to off', test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\",\"off\"","OK"))

        test.log.step('Step 9: Check with MCTEST for VGPS - Start')
        test.dut.dstl_collect_result('Step 9: Check with MCTEST for VGPS (=0)', test.dut_devboard.send_and_verify("mc:vgps", "VGPS: 0"))

        test.log.step('Step 10: Set power antenna to on - Start')
        test.dut.dstl_collect_result('Step 10: Set power antenna to on', test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\",\"on\"","OK"))

        test.log.step('Step 11: Check with MCTEST for VGPS - Start')
        test.dut.dstl_collect_result('Step 11: Check with MCTEST for VGPS (=1)', test.dut_devboard.send_and_verify("mc:vgps", "VGPS: 1"))

        test.log.step('Step 12: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 12: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 13: Check with MCTEST for VGPS - Start')
        test.dut.dstl_collect_result('Step 13: Check with MCTEST for VGPS (=1)', test.dut_devboard.send_and_verify("mc:vgps", "VGPS: 1"))

        test.log.step('Step 14: Set power antenna back to: auto - Start')
        test.dut.dstl_collect_result('Step 14: Set power antenna back to: auto', test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\",\"auto\"", "OK"))

        test.log.step('Step 15: switch on GNSS and Wait for fix position - Start')
        test.dut.dstl_switch_on_engine()
        test.dut.dstl_collect_result('Step 15: Wait for fix position', test.dut.dstl_check_ttff(120))

    def cleanup(test):
        test.log.step('Step 16: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 16: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 17: Set power antenna back to: auto - Start')
        test.dut.dstl_collect_result('Step 17: Set power antenna back to: auto', test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\",\"auto\"","OK"))

        test.dut.nmea.read()
        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
