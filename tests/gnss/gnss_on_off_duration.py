"""
author: katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC00?????.001 - GNSS_on_off_duration
intention: switch engine on / off and check duration for TTFF for different times (alwasy 3 loops)
LM-No (if known):
used eq.: DUT-At1, DUT-Nmea, roof antenna
execution time (appr.): for min = 1 min, 12 min, 30 min, 60 min, 2 hours (120), 4 hours (240) - time: app. 16 hours

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
import time
from datetime import datetime


def check_time_diff(timeToCompare, measuredTime, tolerance):
    result = False

    diff_time = (timeToCompare * tolerance) / 100
    minTime = timeToCompare - diff_time
    maxTime = timeToCompare + diff_time
    if measuredTime > minTime and measuredTime < maxTime:
        result = True

    return result


class Test(BaseTest):
    res = {}
    resOkError = {}
    sgpse_available = False

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):
        maxTimeForFix = 35
        min = ["1", "12", "30", "60", "120", "240"]  # => 1 min, 12 min, 30 min, 60 min, 2 hours (120), 4 hours (240)
        #min = ["1","2"]  # in minutes
        time_tolerance = 5  # percent

        if (test.dut.project == 'BOBCAT' and test.dut.step == '2|3') or test.dut.project == 'VIPER':
            test.sgpse_available = True

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Activate URC for position fix notification  - Start')
        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=1", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 1,.*OK.*")
        test.dut.dstl_collect_result('Step 2: Activate URC for position fix notification', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"on\"", ".*OK.*"))


        test.log.step('Step 3: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 3: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 4: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 4: Wait for first fix position', test.dut.dstl_check_ttff() < 35)

        sleep_time = 13    # 13 minutes
        test.log.com('sleep ' + str(sleep_time) + ' minutes after first fix')
        test.sleep(sleep_time*60)

        test.dut.at1.read()
        test.dut.nmea.read()
#        buffer = test.dut.nmea.last_response
#        test.log.com('last response before loop: ' + test.dut.nmea.last_response)

        k = 0
        for i in range(len(min)):
            for j in range(2):
                test.log.com('loop ' + str(j+1) + ' - ' + min[i] + ' minutes  - start')

                test.log.step('Step 5.'+str(i+1)+' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Switch off GNSS engine - Start')
                test.dut.dstl_collect_result('Step 5.'+str(i+1)+' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Switch off GNSS engine', test.dut.dstl_switch_off_engine())

                test.log.com('sleep ' + min[i] + ' minutes after GNSS switch off')
                test.sleep(int(min[i])*60)

                test.dut.at1.read()
                test.dut.nmea.read()
#                buffer = test.dut.nmea.last_response
#                test.log.com('last response after waiting: ' + test.dut.nmea.last_response)


                test.log.step('Step 6.'+str(i+1)+' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Switch on GNSS engine - Start')
                test.dut.dstl_collect_result('Step 6.'+str(i+1)+' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Switch on GNSS engine', test.dut.dstl_switch_on_engine())

                test.log.info('Wait for fix position')
                test.res[k]=test.dut.dstl_check_ttff(120)
                if test.res[k] == 0:
                    test.resOkError[k] = ' - NO FIX'
                    test.log.step('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position - Start')
#                    test.log.com('DIF: TTFF-check: no fix found - test abort !!!')
                    test.log.com('DIF: TTFF-check: no fix found !!!')
                    test.dut.dstl_collect_result('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position', False)

                elif test.res[k] > maxTimeForFix:
                    test.log.step('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position - Start')
                    test.dut.dstl_collect_result('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position', True)

                    test.log.step('Step 8.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                    test.log.com('DIF: TTFF-check: error, more than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[k]))
                    test.resOkError[k] = ' - ERROR'
                    test.dut.dstl_collect_result('Step 8.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Check TTFF (HID < ' + str(maxTimeForFix) + ' sec (%2.6f sec))' % test.res[k], False)

                else:
                    test.log.step('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position - Start')
                    test.dut.dstl_collect_result('Step 7.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Wait for fix position', True)

                    test.log.step('Step 8.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Check TTFF (HID < ' + str(maxTimeForFix) + ' sec) - Start')
                    test.log.com('EXP: TTFF-check: OK, less than ' + str(maxTimeForFix) + ' sec: ' + str(test.res[k]))
                    test.resOkError[k] = ' - OK'

                    test.dut.dstl_collect_result('Step 8.' + str(i+1) + ' - loop: ' + str(j+1) + ' (' + min[i] + ' minutes): Check TTFF (HID < ' + str(maxTimeForFix) + ' sec (%2.6f sec))' % test.res[k], True)

                fix_time_1 = time.time()
                test.log.com('fix_time_1: ' + str(fix_time_1) + ' => ' + datetime.fromtimestamp(fix_time_1).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

                test.dut.at1.read()
                test.dut.nmea.read()
#                buffer = test.dut.nmea.last_response
#                test.log.com('last response before additional sleep: ' + test.dut.nmea.last_response)

                sleep_time = 20
                test.log.com('sleep ' + str(sleep_time) + ' seconds before loop end')
                test.sleep(sleep_time)
                k = k + 1

                test.dut.at1.read()
                test.dut.nmea.read()
#                buffer = test.dut.nmea.last_response
#                test.log.com('last response before loop end: ' + test.dut.nmea.last_response)

                test.log.com('loop ' + str(j+1) + ' - ' + min[i] + ' minutes  - end')


    def cleanup(test):
        test.log.step('Step 9: Deactivate URC and Switch off Engine - Start')
        test.dut.dstl_collect_result('Step 9: Deactivate URC and Switch off Engine', test.dut.dstl_switch_off_engine() and test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"off\"",".*OK.*"))

        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=0", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 0,.*OK.*")

        for i in range(len(test.res)):
            test.log.com('Test[%2d] - TTFF: %4.6f sec %s' % (i+1, test.res[i], test.resOkError[i]))

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

if "__main__" == __name__:
    unicorn.main()
