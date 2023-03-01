"""
author: katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC00xxxxx.001 - gnss_simple
intention: start GNSS and check if fix is found in a loop
LM-No (if known): LM000xxxx.001 - GNSS engine
used eq.: DUT-At1, DUT-Nmea, roof antenna
execution time (appr.): app. 16 min (depends of getting fix)
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
        maxTimeForFix = 120
        loop_no = 10  # number loops to be checked

        i = 0
        while i < loop_no:
            test.log.info('+++ Test loop: ' + str(i+1) + ' - Start +++')

            test.log.step('Step 1.' + str(i+1) + ': Initialise_GNSS engine to default setting - Start')
            test.dut.dstl_collect_result('Step 1.' + str(i+1) + ': Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

            test.log.step('Step 2.' + str(i+1) + ': Switch On GNSS engine - Start')
            test.dut.dstl_collect_result('Step 2.' + str(i+1) + ': Switch On GNSS engine', test.dut.dstl_switch_on_engine())
            test.sleep(1)

            test.log.info('Wait for fix position')
            test.res[i]=test.dut.dstl_check_ttff(maxTimeForFix)
            if test.res[i] == 0:
                test.resOkError[i] = ' - NO FIX'
                test.log.step('Step 3.' + str(i+1) + ': Wait for fix position - Start')
                test.log.com('DIF: TTFF-check: no fix found - testcase abort !!!')
                test.dut.dstl_collect_result('Step 3.' + str(i+1) + ': Wait for fix position', False)

            elif test.res[i] > maxTimeForFix:
                test.log.step('Step 3.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 3.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 4.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('DIF: TTFF-check: error, more than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - ERROR'
                test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', False)

            else:
                test.log.step('Step 3.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 3.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 4.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('EXP: TTFF-check: OK, less than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - OK'
                test.fix_counter = test.fix_counter +1
                test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', True)

            test.log.step('Step 5.' + str(i+1) + ': Initialise_GNSS engine to default setting - Start')
            test.dut.dstl_collect_result('Step 5.' + str(i+1) + ': Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

            test.log.info('+++ Test loop: ' + str(i+1) + ' - End +++')
            i = i+1

    def cleanup(test):
        test.log.step('Step 6: switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 6: switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 7: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 7: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

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
