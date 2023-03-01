"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0085478.001 - TcNmeaOutputFrequency
           TC0096529.001 - GNSSFrequencyConfiguration
intention: Check NMEA data output frequency
LM-No (if known):
used eq.: DUT-At1, DUT-Nmea, roof antenna
execution time (appr.): for sec = ["60", "120"] - time: appr. 8 minutes
                        for sec = ["60", "120", "300"] - time: appr. 18 minutes
                        for sec = ["1800"] - time: 62 minutes
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

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):

        sec = ["60", "120", "300", "600", "1800", "6000"]  # => 1 min, 2 min, 5 min, 10 min, 30 min, 100 min
        #sec = ["60"]
        time_tolerance = 5  # percent

        test.expect(test.dut.dstl_switch_off_engine())
        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Cold start - Start')
        test.dut.dstl_collect_result('Step 2: Cold start ', test.dut.at1.send_and_verify("at^sgpsc=engine,delete",".*OK.*"))

        test.log.step('Step 3: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 3.: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 4: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 4: Wait for first fix position', test.dut.dstl_check_ttff() < 35)
        test.sleep(20)

        for i in range(len(sec)):
            test.log.step('Step 5.'+str(i+1)+': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 5.'+str(i+1)+': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            test.log.step('Step 6.'+str(i+1)+': Set NMEA output frequency to '+sec[i]+' sec - Start')
            test.dut.dstl_collect_result('Step 6.'+str(i+1)+': Set NMEA output frequency to '+sec[i]+' sec', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Freq\",\""+sec[i]+"\"",".*OK.*"))

            test.log.step('Step 7.'+str(i+1)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 7.'+str(i+1)+': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.log.step('Step 8.'+str(i+1)+': Wait for fix position (part 1) - Start')
            test.dut.dstl_collect_result('Step 8.'+str(i+1)+': Wait for fix position (part 1)', test.dut.dstl_check_ttff(120) < 35)
            fix_time_1 = time.time()
            test.log.verbose('fix_time_1: ' + str(fix_time_1) + ' => ' + datetime.fromtimestamp(fix_time_1).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

            test.log.step('Step 9.' + str(i + 1) + ': Wait for new nmea data (part 1) - Start')
#            test.dut.dstl_collect_result('Step 9.' + str(i + 1) + ': Wait for new nmea data (part 1)', True in test.dut.nmea._wait_for("GNS", int(sec[i])+100))
            test.dut.dstl_collect_result('Step 9.' + str(i + 1) + ': Wait for new nmea data (part 1)', test.dut.nmea.wait_for("GNS", int(sec[i])+100) is True)
            nmea_time_1 = time.time()
            test.log.verbose('nmea_time_1: ' + str(nmea_time_1) + ' => ' + datetime.fromtimestamp(nmea_time_1).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time_diff_1 = nmea_time_1 - fix_time_1
            test.log.info('time: ' + str(time_diff_1))

            test.log.step('Step 10.' + str(i+1) + ': Check that '+sec[i]+' seconds an NMEA message will be output (part 1) - Start')
            test.dut.dstl_collect_result('Step 10.' + str(i+1) + ': Check that ' + sec[i] +' seconds an NMEA message will be output (part 1): %4.6f sec' % time_diff_1,
                                         check_time_diff(int(sec[i]), time_diff_1, time_tolerance))

            test.log.step('Step 11.' + str(i + 1) + ': Wait for fix position (part 2) - Start')
            test.dut.dstl_collect_result('Step 11.' + str(i + 1) + ': Wait for fix position (part 2)', test.dut.dstl_check_ttff() < 35)
            fix_time_2 = time.time()
            test.log.verbose('fix_time_2: ' + str(fix_time_2) + ' => ' + datetime.fromtimestamp(fix_time_2).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

            test.log.step('Step 12.' + str(i + 1) + ': Wait for new nmea data (part 2) - Start')
            test.dut.dstl_collect_result('Step 12.' + str(i + 1) + ': Wait for new nmea data (part 2)', test.dut.nmea.wait_for("GNS", int(sec[i])+100) is True)
            nmea_time_2 = time.time()
            test.log.verbose('nmea_time_2: ' + str(nmea_time_2) + ' => ' + datetime.fromtimestamp(nmea_time_2).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
            time_diff_2 = nmea_time_2 - fix_time_2
            test.log.info('time: ' + str(time_diff_2))

            test.log.step('Step 13.' + str(i + 1) + ': Check that ' + sec[i] + ' seconds an NMEA message will be output (part 2) - Start')
            test.dut.dstl_collect_result('Step 13.' + str(i + 1) + ': Check that ' + sec[i] + ' seconds an NMEA message will be output (part 2): %4.6f sec' % time_diff_2,
                                         check_time_diff(int(sec[i]), time_diff_2, time_tolerance))


    def cleanup(test):
        test.log.step('Step 14: Deactivate URC and Switch off Engine - Start')
        test.dut.dstl_collect_result('Step 14: Deactivate URC and Switch off Engine', test.dut.dstl_switch_off_engine() and test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"off\"",".*OK.*"))

        test.log.step('Step 15: set Nmea Frequency back - Start')
        test.dut.dstl_collect_result('Step 15: set Nmea Frequency back', test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Freq\",\"1\"", ".*OK.*"))

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

if "__main__" == __name__:
    unicorn.main()
