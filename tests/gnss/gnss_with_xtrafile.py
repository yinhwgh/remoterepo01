"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0085479.001 - GnssWithXtrafile
intention: Determine time to first fix(TTFF)  with Xtrafile(AGPS data). GNSS will get faster TTFF, lower 10 seconds.
           Xtra file is to download from QCT server
LM-No (if known): LM0002790.xxx, LM0003429.001
used eq.: DUT-At1, DUT-Nmea, roof antenna
execution time (appr.): 5 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *


class Test(BaseTest):
    res = {}
    resOkError = {}
    local_xtrafile = ''

    def setup(test):
        test.local_xtrafile = test.workspace + '\\xtra_local.bin'
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

        test.log.step('Step 1: Download xtra file to ' + test.local_xtrafile + ' - Start')
        test.dut.dstl_collect_result('Step 1: Download xtra file to ' + test.local_xtrafile,
                            test.dut.dstl_download_xtrafile(test.local_xtrafile), test_abort=True)
        test.sleep(2)

    def run(test):
        maxTimeForFix = 10
        loop_no = 10  # number loops to be checked

        test.log.step('Step 2: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 2: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())
        test.sleep(1)
        test.log.step('Step 3: Set RTC to Greenich Mean Time (GMT: 0) - Start')
        test.dut.dstl_collect_result('Step 3: Set RTC to Greenich Mean Time (GMT: 0)', test.dut.dstl_set_time())

        i = 0
        while i < loop_no:
#            test.expect(test.dut.dstl_switch_off_engine())
            test.dut.dstl_switch_off_engine()
            test.log.info('+++ Test loop: ' + str(i+1) + ' - Start +++')
            test.log.step('Step 4.' + str(i+1) +': delete xtrafile - Start')
            test.dut.dstl_collect_result('Step 4.' + str(i+1) +': delete xtrafile', test.dut.dstl_delete_xtrafile())

            test.log.step('Step 5.' + str(i+1) +': inject new xtrafile - Start')
            test.dut.dstl_collect_result('Step 5.' + str(i+1) +': inject new xtrafile', test.dut.dstl_inject_file(test.local_xtrafile), test_abort=True)
            test.sleep(1)

            test.log.step('Step 6.' + str(i+1) +': Switch On GNSS engine in A-GNSS mode - Start')
            test.dut.dstl_collect_result('Step 6.' + str(i+1) +': Switch On GNSS engine in A-GNSS mode', test.dut.dstl_switch_on_engine(2), test_abort=True)
            test.log.info('Wait for fix position')
            test.res[i] = test.dut.dstl_check_ttff(90)
            if test.res[i] == 0:
                test.resOkError[i] = ' - NO FIX'
                test.log.step('Step 7.' + str(i+1) + ': Wait for fix position - Start')
                test.log.com('DIF: TTFF-check: no fix found - testcase abort')
                test.dut.dstl_collect_result('Step 7.' + str(i+1) + ': Wait for fix position', False, test_abort=True)

            elif test.res[i] > maxTimeForFix:
                test.log.step('Step 7.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 7.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 8.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('DIF: TTFF-check: error, more than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - ERROR'
                test.dut.dstl_collect_result('Step 8.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', False)

            else:
                test.log.step('Step 7.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 7.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 8.' + str(i + 1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('EXP: TTFF-check: OK, less than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - OK'
                test.dut.dstl_collect_result('Step 8.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', True)

            test.log.info('+++ Test loop: ' + str(i+1) + ' - End +++')
            i = i+1

    def cleanup(test):
        test.log.step('Step 9: switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 9: switch off GNSS engine', test.dut.dstl_switch_off_engine())

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
