"""
author: katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC00xxxxx.001 - gnss_check_nmea_simple
intention: start GNSS and check if NMEA data are comming (fix is not checked)
LM-No (if known): LM000xxxx.001 - GNSS engine
used eq.: DUT-At1, DUT-Nmea, roof antenna or no antenna
execution time (appr.): app. 8 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *

class Test(BaseTest):
    res = {}
    resOkError = {}
    fix_counter = 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        test.dut.dstl_detect()

    def run(test):

        loop_no = 5  # number loops to be checked

        i = 0
        while i < loop_no:
            test.log.info('+++ Test loop: ' + str(i+1) + ' - Start +++')

            test.log.step('Step 1.' + str(i+1) + ': Initialise_GNSS engine to default setting - Start')
            test.dut.dstl_collect_result('Step 1.' + str(i+1) + ': Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

            test.log.step('Step 2.' + str(i+1) + ': Switch On GNSS engine - Start')
            test.dut.dstl_collect_result('Step 2.' + str(i+1) + ': Switch On GNSS engine', test.dut.dstl_switch_on_engine())
            test.sleep(1)

            test.dut.nmea.read()
            test.sleep(30)
            data = test.dut.nmea.read()

            test.log.step('Step 3.' + str(i + 1) + ': Check if NMEA data contain: VTG sentences - Start')
            num_vtg = data.count("VTG")
            test.log.com('number of VTG sentences: ' + str(num_vtg))
            if num_vtg >= 10:
                test.dut.dstl_collect_result('Step 3.' + str(i + 1) + ': VTG sentences are available (' + str(num_vtg) + ' times)', True)
            else:
                test.dut.dstl_collect_result('Step 3.' + str(i + 1) + ': VTG sentences are NOT available (or not enough) (' + str(num_vtg) + ' times)', False)

            test.log.step('Step 4.' + str(i + 1) + ': Check if NMEA data contain: RMC sentences - Start')
            num_rmc = data.count("RMC")
            test.log.com('number of RMC sentences: ' + str(num_rmc))
            if num_rmc >= 10:
                test.dut.dstl_collect_result('Step 4.' + str(i + 1) + ': RMC sentences are available (' + str(num_rmc) + ' times)', True)
            else:
                test.dut.dstl_collect_result('Step 4.' + str(i + 1) + ': RMC sentences are NOT available (or not enough) (' + str(num_rmc) + ' times)', False)

            test.log.step('Step 5.' + str(i + 1) + ': Check if NMEA data contain: GGA sentences - Start')
            num_gga = data.count("GGA")
            test.log.com('number of GGA sentences:' + str(num_gga))
            if num_gga >= 10:
                test.dut.dstl_collect_result('Step 5.' + str(i + 1) + ': GGA sentences are available (' + str(num_gga) + ' times)', True)
            else:
                test.dut.dstl_collect_result('Step 5.' + str(i + 1) + ': GGA sentences are NOT available (or not enough) (' + str(num_gga) + ' times)', False)

            test.log.step('Step 6.' + str(i+1) + ': Initialise_GNSS engine to default setting - Start')
            test.dut.dstl_collect_result('Step 6.' + str(i+1) + ': Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

            test.log.info('+++ Test loop: ' + str(i+1) + ' - End +++')
            i = i+1

    def cleanup(test):
        test.log.step('Step 7: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 7: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 8: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 8: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()

        test.log.com(' ')
        test.log.com('***** Results of all TTFF Tests *****')
        test.log.com(' ')

        for i in range(len(test.res)):
            test.log.com('Test[%2d] - TTFF: %4.6f sec %s' % (i+1, test.res[i], test.resOkError[i]))

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
