"""
author: duangkeo.krueger@thalesgroup.com, katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC0096530.001 - GnssColdstart
intention: Coldstart must be possible without switch off the Engine, Coldstart means all Almanac and Ephemeris data must be deleted
LM-No (if known): LM0006519.001 - GNSS engine delete
used eq.: DUT-At1, DUT-Nmea, roof antenna or SMBV
execution time (appr.): 6 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
KPI_NAME ="gnss_coldstart_kpi"
KPI_NAME_NUM="time_to_first_fix"
OPPORTUNITIES_NUM = 10
KPI_TYPE = "bin"


class Test(BaseTest):
    res = {}
    resOkError = {}
    fix_counter = 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()
        test.dut.at1.send_and_verify("at+GSN", ".*OK.*")

    def run(test):
        maxTimeForFix = 32
        loop_no = 10 # number loops to be checked
        i = 0

        #test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        #test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        GNSS_mod_ind = 'AAAAA'
        test.dut.dstl_switch_on_engine()
        test.dut.dstl_check_ttff(120)

        test.log.step('Step 3: Check mod-indicators of all systems - Start')
        result = test.dut.dstl_waitfor_nmea_data_response(nmea_data='.*GNGNS.*,' + GNSS_mod_ind + ',.*', maxtime=60) == 0
        test.dut.dstl_collect_result('Step 3: Check mod-indicators of all systems. result: ', True)

        while i < loop_no:

            test.log.step('Step 2: Switch On GNSS engine - Start')
            test.dut.dstl_collect_result('Step 2: Switch On GNSS engine', test.dut.dstl_switch_on_engine())
            test.sleep(1)

            test.log.info('+++ Test loop: ' + str(i+1) + ' - Start +++')

            test.log.step('Step 3.' + str(i+1) + ': Start cold start - Start')
            test.dut.dstl_collect_result('Step 3.' + str(i+1) + ': Start cold start', test.dut.dstl_coldstart(), test_abort=False)

            test.log.info('Wait for fix position')
            test.res[i]=test.dut.dstl_check_ttff(120)
            if test.res[i] == 0:
                test.resOkError[i] = ' - NO FIX'
                test.log.step('Step 4.' + str(i+1) + ': Wait for fix position - Start')
                test.log.com('DIF: TTFF-check: no fix found - testcase abort !!!')
                test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Wait for fix position', False, test_abort=False )

            elif test.res[i] > maxTimeForFix:
                test.log.step('Step 4.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 5.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('DIF: TTFF-check: error, more than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - ERROR'
                test.dut.dstl_collect_result('Step 5.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', False)

            else:
                test.log.step('Step 4.' + str(i+1) + ': Wait for fix position - Start')
                test.dut.dstl_collect_result('Step 4.' + str(i+1) + ': Wait for fix position', True)

                test.log.step('Step 5.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                test.log.com('EXP: TTFF-check: OK, less than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[i]))
                test.resOkError[i] = ' - OK'
                test.fix_counter = test.fix_counter +1
                test.dut.dstl_collect_result('Step 5.' + str(i+1) + ': Check TTFF (HID < ' + str(maxTimeForFix) + ' sec)', True)
            dstl.test.kpi_store(name=KPI_NAME_NUM, value=test.res[i], type='num', device=test.dut)
            test.log.info('+++ Test loop: ' + str(i+1) + ' - End +++')
            i = i+1

            test.log.step('Step 6: switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 6: switch off GNSS engine', test.dut.dstl_switch_off_engine())

            #test.dut.dstl_init_gnss()

    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 6: switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 6: switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.dut.nmea.read()

        test.log.com(' ')
        test.log.com('***** Results of all TTFF Tests *****')
        test.log.com(' ')

        for i in range(len(test.res)):
            test.log.com('Test[%2d] - TTFF: %4.6f sec %s' % (i+1, test.res[i], test.resOkError[i]))

        test.dut.dstl_print_results()

        test.kpi_store(name=KPI_NAME, value=test.fix_counter, type=KPI_TYPE, total=OPPORTUNITIES_NUM, device=test.dut)

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

        print("passed" + str(test.verdicts_counter_passed))
        print("total" + str(test.verdicts_counter_total))
        #test.kpi_store(name=test.testname, value=test.verdicts_counter_passed, type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)


if "__main__" == __name__:
    unicorn.main()
