"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number:  TC0087419.001 - InjectGpsData
intention:  Load different type of XTRA file to the module, then start GPS with xtra file.
            Check the result depend on XTRA file (AGPS END OK, BAD_CRC, TIME_INFO_ERROR, OTHER_ERROR)
LM-No (if known):  	Functional Tests
used eq.: DUT-At1
execution time (appr.): 5 min
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

    def run(test):
        local_xtrafile = test.workspace + '\\xtra.bin'

        dummy_xtrafile = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "dstl", "gnss","dummy.bin"))
        Xtra2Old_xtrafile = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "dstl", "gnss","xtra2Old.bin"))
        Xtra3Old_xtrafile = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "dstl", "gnss","xtra3Old.bin"))

        test.log.info("workspace: "+test.workspace)
        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        if test.dut.project == 'BOBCAT' and ((test.dut.step == '2') or (test.dut.step == '3')):
            test.dut.at1.send_and_verify("at^sgpse=1", ".*OK.*")

        test.log.step('Step 2: Change Time to "greenwich" - Start')
        test.dut.dstl_collect_result('Step 2: Change Time to "greenwich"', test.dut.dstl_set_time())

        for xtra_path_nr in range(3):
            test.log.step('Step 3.'+str(xtra_path_nr+1)+': Delete existing XTRA file and check sgpsc=info,xtra - Start')
            test.dut.dstl_collect_result('Step 3.'+str(xtra_path_nr+1)+': Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

            test.log.step('Step 4.'+str(xtra_path_nr+1)+': Download XTRA file from server - Start')
            test.dut.dstl_collect_result('Step 4.'+str(xtra_path_nr+1)+': Download XTRA file from server', test.dut.dstl_download_xtrafile(local_xtrafile,xtra_path_nr))

            test.dut.at1.read()
            test.log.step('Step 5.'+str(xtra_path_nr+1)+': Send Binary Data (XTRA file) to the module - Start')
            test.dut.dstl_collect_result('Step 5.'+str(xtra_path_nr+1)+': Send Binary Data (XTRA file) to the module', test.dut.dstl_inject_file(local_xtrafile))

            test.log.step('Step 6.'+str(xtra_path_nr+1)+': xtra Data info - Start')
            test.dut.dstl_collect_result('Step 6.'+str(xtra_path_nr+1)+': xtra Data info', test.dut.dstl_check_xtra_info())

            test.log.step('Step 7.'+str(xtra_path_nr+1)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 7.'+str(xtra_path_nr+1)+': Switch on GNSS engine',  test.dut.dstl_switch_on_engine(2))

            test.log.step('Step 8.'+str(xtra_path_nr+1)+': Wait for first fix position and check time for cold start - Start')
            time = test.dut.dstl_check_ttff()
            test.dut.dstl_collect_result( 'Step 8.'+str(xtra_path_nr+1)+': Wait for first fix position and check time for cold start: ' + "{:.2f}".format(time) + 's', time < 10)

            test.log.step('Step 9.'+str(xtra_path_nr+1)+': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 9.'+str(xtra_path_nr+1)+': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.info("Check old xtra file")

        test.log.step('Step 10: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 10: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.dut.at1.read()
        test.log.step('Step 11: Send Binary Data (old file) to the module - Start')
        result = test.dut.dstl_inject_file_response(Xtra2Old_xtrafile,"OK", check_xtrafile=False)
        test.dut.dstl_collect_result('Step 11: Send Binary Data (old file) to the module: ' + result[1], ("ERROR" in result[1]) | ("FAILURE" in result[1])  )

        test.log.info("read: " + test.dut.at1.read())

        test.log.step('Step 12: xtra Data info - Start')
        test.dut.dstl_collect_result('Step 12: xtra Data info', test.dut.dstl_check_xtra_info(True))

        test.log.step('Step 13: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 13: Switch on GNSS engine - Start', test.dut.dstl_switch_on_engine(2))

        test.log.step('Step 14: Wait for first fix position and check time for cold start - Start')
        time = test.dut.dstl_check_ttff()
        test.dut.dstl_collect_result('Step 14: Wait for first fix position and check time for cold start: ' + "{:.2f}".format(time) + 's', time > 10)

        test.log.step('Step 15: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 15: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.info("Check nonsense file")

        test.log.step('Step 16: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 16: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.dut.at1.read()
        test.log.step('Step 17: Send Binary Data (XTRA dummy file) to the module - Start')
        result = test.dut.dstl_inject_file_response(dummy_xtrafile,"OK",check_xtrafile=False)
        test.dut.dstl_collect_result('Step 17: Send Binary Data (XTRA dummy file) to the module: ' + result[1], ("ERROR" in result[1]) | ("FAILURE" in result[1]) )

        test.log.info("read: " + test.dut.at1.read())

        test.log.step('Step 18: xtra Data info - Start')
        test.dut.dstl_collect_result('Step 18: xtra Data info', test.dut.dstl_check_xtra_info(True))

        test.log.step('Step 19: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 19: Switch on GNSS engine - Start', test.dut.dstl_switch_on_engine(2))

        test.log.step('Step 20: Wait for first fix position and check time for cold start - Start')
        time = test.dut.dstl_check_ttff()
        test.dut.dstl_collect_result('Step 20: Wait for first fix position and check time for cold start: ' + "{:.2f}".format(time) + 's', time > 10)

        test.log.step('Step 21: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 21: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.info("Set wrong time ")

        test.log.step('Step 22: Set wrong  RTC time - Start')
        test.dut.dstl_collect_result('Step 22: Set wrong  RTC time', test.dut.at1.send_and_verify("at+cclk=\"20/03/13,13:03:20\"","OK"))

        test.log.step('Step 23: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 23: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.dut.at1.read()

        test.log.step('Step 24: Send Binary Data (XTRA file with wrong time) to the module - Start')
        result = test.dut.dstl_inject_file_response(local_xtrafile,"OK",check_xtrafile=False)
        test.dut.dstl_collect_result('Step 24: Send Binary Data (XTRA file with wrong time) to the module: ' + result[1], ("ERROR" in result[1]) | ("FAILURE" in result[1])  )

        test.log.info("read: " + test.dut.at1.read())

        test.log.step('Step 25: xtra Data info - Start')
        test.dut.dstl_collect_result('Step 25: xtra Data info', test.dut.dstl_check_xtra_info(True))

        test.log.step('Step 26: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 26: Switch on GNSS engine - Start', test.dut.dstl_switch_on_engine(2))

        test.log.step('Step 27: Wait for first fix position and check time for cold start - Start')
        time = test.dut.dstl_check_ttff()
        test.dut.dstl_collect_result('Step 27: Wait for first fix position and check time for cold start: ' + "{:.2f}".format(time) + 's', time > 10)

        test.log.step('Step 28: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 28: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.info("Set correct parameters again")

        test.log.step('Step 29: Change Time to "greenwich" - Start')
        test.dut.dstl_collect_result('Step 29: Change Time to "greenwich"', test.dut.dstl_set_time())

        test.log.step('Step 30: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 30: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.dut.at1.read()
        test.log.step('Step 31: Send Binary Data (XTRA file) to the module - Start')
        test.dut.dstl_collect_result('Step 31: Send Binary Data (XTRA file) to the module', test.dut.dstl_inject_file(local_xtrafile))

        test.log.step('Step 32: xtra Data info - Start')
        test.dut.dstl_collect_result('Step 32: xtra Data info', test.dut.dstl_check_xtra_info())

        test.log.step('Step 33: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 33: Switch on GNSS engine', test.dut.dstl_switch_on_engine(2))

        test.log.step('Step 34: Wait for first fix position and check time for cold start - Start')
        time = test.dut.dstl_check_ttff()
        test.dut.dstl_collect_result('Step 34: Wait for first fix position and check time for cold start: ' + "{:.2f}".format(time) + 's', time < 10)

        test.log.step('Step 35: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 35: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

    def cleanup(test):
        test.log.step('Step 36: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 36: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 37: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 37: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.dut.nmea.read()
        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
