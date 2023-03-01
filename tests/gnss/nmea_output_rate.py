"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105082.001 - NMEAOutputRate
intention: Check NMEA output frequency, which is output every 1 sec.
           This is default setting and cannot be changed with at-command
LM-No (if known): LM0006729.002 - NMEAOutputRate  -> Serval, Viper
used eq.: DUT-At1, roof Antenna or SMBV
execution time (appr.): 3 min
"""

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    OK_counter = 0
    ERR_counter = 0
    number_of_rate_meas = 0

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()


    def run(test):
        duration_time = {}

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Urc\",\"on\"", ".*OK.*")
        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.dut.nmea.read()
        test.dut.nmea.wait_for(".*G[NP]GGA.*", 10)
        test.dut.nmea.read()
        #test.dut.nmea.wait_for("GNGSA", 10)

        fix_found = False
        i = 0
        loop_num_ttff = 60      # number of loops before fix

        test.log.info("Check output rate before Fix or the first time")
        while ((fix_found == False) and (i < loop_num_ttff)):
            test.log.com("start loop_no (before Fix): " + str(i))
            start_time=time.time()
            test.dut.nmea.wait_for("G[NPL]GGA",10)
            duration_time[i]=time.time()-start_time
            test.number_of_rate_meas = test.number_of_rate_meas  + 1

#            test.log.info("last response: " + test.dut.nmea.last_response)
            if re.match(".*GSA,A,3.*|.*GSA,A,2.*", test.dut.nmea.last_response, re.M|re.I|re.S):
                fix_found = True
                test.log.com("Fix was found - end if loop")

            i = i + 1

        test.log.com("i after loop for fix or at the end: " + str(i))

        for i in range(len(duration_time)):
            if (duration_time[i] < 1.105 and duration_time[i] > 0.9):
                resultOkErr = 'OK'
                test.OK_counter = test.OK_counter + 1
            else:
                resultOkErr = 'ERROR'
                test.ERR_counter = test.ERR_counter + 1
            all_results.append(['Loop ' + str(i+1) + ': Check frequency of NMEA output data before fix or the 1rst time, duration time: '+str(duration_time[i]), resultOkErr])
            # test.log.step('Step 3.'+str(i+1)+': Check frequency of NMEA output data before fix or the 1rst time, duration time: '+str(duration_time[i])+'- Start')
            # test.dut.dstl_collect_result('Step 3.'+str(i+1)+': Check frequency of NMEA output data before fix or the 1rst time, duration time: '+str(duration_time[i]), duration_time[i] < 1.1 and duration_time[i] > 0.9)


        loop_no_after_ttff = 100    # number of loops after fix
        ttff_text = ""
        if fix_found == True:
            test.log.com("Check output rate after Fix")
            ttff_text = "after fix"
        else:
            test.log.com("Check output rate the additional " + str(loop_no_after_ttff) +" times")
            ttff_text = "for additional " + str(loop_no_after_ttff)

        i = 0
        while (i < loop_no_after_ttff):
            test.log.com("start loop_no (after Fix): " + str(i))
            start_time=time.time()
            test.dut.nmea.wait_for("G[NP]GGA",10)
            duration_time[i]=time.time()-start_time
            test.number_of_rate_meas = test.number_of_rate_meas + 1

            i = i + 1

        for i in range(len(duration_time)):
            if (duration_time[i] < 1.105 and duration_time[i] > 0.9):
                resultOkErr = 'OK'
                test.OK_counter = test.OK_counter + 1
            else:
                resultOkErr = 'ERROR'
                test.ERR_counter = test.ERR_counter + 1
            all_results.append(['Loop ' + str(i+1) + ': Check frequency of NMEA output data ' + ttff_text + ', duration time: '+str(duration_time[i]), resultOkErr])

#            test.log.step('Step 4.'+str(i+1)+': Check frequency of NMEA output data ' + ttff_text + ' , duration time: '+str(duration_time[i])+'- Start')
#            test.dut.dstl_collect_result('Step 4.'+str(i+1)+': Check frequency of NMEA output data ' + ttff_text + ', duration time: '+str(duration_time[i]), duration_time[i] < 1.1 and duration_time[i] > 0.9)

        test.log.com("number_of_rate_meas: " + str(test.number_of_rate_meas))
        test.log.com("OK_counter: " + str(test.OK_counter))
        test.log.com("ERR_counter: " + str(test.ERR_counter))

        err_rate = (test.ERR_counter * 100) / test.number_of_rate_meas
        check_output_rate_result = False
        err_procent = 10
        if err_rate <= err_procent:
            check_output_rate_result = True
        test.log.step('Step 3: Check frequency of NMEA output data ' + str(test.number_of_rate_meas) + ' times - Start')
        test.dut.dstl_collect_result('Step 3: Check frequency of NMEA output data ' + str(test.number_of_rate_meas) + ' times (%.2f %% are faulty ' % (err_rate) + '(<= ' + str(err_procent) + ' %))', check_output_rate_result)


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.com(' ')
        test.log.com('****************************')
        test.log.com("number_of_rate_meas: " + str(test.number_of_rate_meas))
        test.log.com("OK_counter: " + str(test.OK_counter))
        test.log.com("ERR_counter: " + str(test.ERR_counter))
        test.log.com("Note: error occurs if time difference between 2 sentences is between 0.9 and 1.105 seconds")

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
