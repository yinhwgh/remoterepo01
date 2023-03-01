"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0104208.001
intention:  Check the validity of XTRA file, which was injected in the GNSS engine before.
            It will show the current week number (since 06.01.1980,00:00:00) + minutes and the count down of validity duration in minutes
            And URC can be enabled to check the time, when User wants to get URC before validity duration is ran out.
LM-No (if known): LM0004037.001+002 Bobcat_01, 02, 03, 04, Viper_01
used eq.: DUT-At1, log_path,
execution time (appr.): 14 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    sgpse_available = False
    switch_urc_port = False

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):
#        local_xtrafile = test.log_path + '\\xtra.bin'
        local_xtrafile = test.workspace + '\\xtra.bin'

        if (test.dut.project == 'BOBCAT' and ((test.dut.step == '2') or (test.dut.step == '3'))) or test.dut.project == 'VIPER':
            test.sgpse_available = True

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())


        test.log.step('Step 2: Activate URC for position fix notification  - Start')
        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=1", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 1,.*OK.*")

        if test.dut.dstl_changend_urc_port('mdm') == True:
            test.switch_urc_port = True

        test.dut.dstl_collect_result('Step 2: Activate URC for position fix notification', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"on\"", ".*OK.*"))

        test.log.step('Step 3: Delete existing XTRA file and check sgpsc=info,xtra - Start')
        test.dut.dstl_collect_result('Step 3: Delete existing XTRA file and check sgpsc=info,xtra', test.dut.dstl_delete_xtrafile())

        test.log.step('Step 4: Change Time to "greenwich" - Start')
        test.dut.dstl_collect_result('Step 4: Change Time to "greenwich"', test.dut.dstl_set_time())

        test.log.step('Step 5: Download XTRA file from server - Start')
        test.dut.dstl_collect_result('Step 5: Download XTRA file from server', test.dut.dstl_download_xtrafile(local_xtrafile), test_abort=True)

        test.log.step('Step 6: Send Binary Data (XTRA file) to the module - Start')
        test.dut.dstl_collect_result('Step 6: Send Binary Data (XTRA file) to the module', test.dut.dstl_inject_file(local_xtrafile), test_abort=True)

        test.log.step('Step 7: Activate info urc - Start')
        test.dut.dstl_collect_result('Step 7: Activate info urc', test.dut.at1.send_and_verify("at^sgpsc=\"Info\",\"Urc\",\"on\"", "OK"))

        test.log.step('Step 8: Set nmea Output to off - Start')
        test.dut.dstl_collect_result('Step 8: Set nmea Output to off', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/Output\",\"off\""))

        test.log.step('Step 9: Start engine with XTRA file - Start')
        test.dut.dstl_collect_result('Step 9: Start engine with XTRA file ', test.dut.at1.send_and_verify("at^sgpsc=engine,2", "OK"))

        set_time = [2, 10]
        for i in range(len(set_time)):
            test.dut.at1.read()
            test.log.step('Step 10.'+str(i+1)+': Read out the XTRA file - info  - Start')
            test.dut.dstl_collect_result('Step 10.'+str(i+1)+': Read out the XTRA file - info ', test.dut.at1.send_and_verify("at^sgpsc=info,xtra", "SGPSC") is True, True)
            data = test.dut.at1.last_response
            element = data.split(',')
#            print(element[5].strip('\r\nOK'))
            test.log.step('Step 11.' + str(i + 1) + ': Check XTRA file - info - Start')
            if "\"0\",\"0\",\"0\"" in element[5].strip('\r\nOK'):
                test.dut.dstl_collect_result('Step 11.' + str(i+1) + ': Check XTRA file - info: no data available -> step over step 12 an 13 !!!', False)
            else:
                test.dut.dstl_collect_result('Step 11.' + str(i + 1) + ': Check the XTRA file - info: data available', True)
                urc_time = int(element[5].strip('"\r\nOK')) - set_time[i]

                test.log.step('Step 12.'+str(i+1)+': Set URC to the time to InfoXtraDurationMinutes - Start')
                test.dut.dstl_collect_result('Step 12.'+str(i+1)+': Set URC to the time to InfoXtraDurationMinutes ',
                                test.dut.at1.send_and_verify("at^sgpsc=\"Info\",\"Urc\",\"on\"," + str(urc_time), '.*' + str(urc_time) + '.*', "OK"))

                test.log.step('Step 13.'+str(i+1)+': Wait for URC ^SGPSE: 2,xxx (after ' + str(set_time[i]) + ' minutes) - Start')
                test.dut.dstl_collect_result('Step 13.'+str(i+1)+': Wait for URC ^SGPSE: 2,xxx (after ' + str(set_time[i]) + ' minutes)', test.dut.at1.wait_for('.*SGPSE: 2,.*' +str(urc_time), set_time[i] * 60 + 10) is True)

    def cleanup(test):
        test.log.step('Step 14: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 14: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 15: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 15: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 16: Delete XTRA file - Start')
        test.dut.dstl_collect_result('Step 16: Delete XTRA file', test.dut.dstl_delete_xtrafile())

        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=0", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 0,.*OK.*")

        if test.switch_urc_port == True:
            test.dut.dstl_changend_urc_port('app')

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
