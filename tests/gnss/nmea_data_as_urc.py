"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096531.001 - NmeaDataAsUrc
intention: Display NMEA data at control interface (at-command interface) as URC : ^SGPSE: 3, xxx
            Type of GNSS system can be selected, each system or all combinations of GPS, Glonass, Galileo, Beidou and QZSS
LM-No (if known):
used eq.: DUT-At1, DUT-Nmea, roof antenna or SMBV
execution time (appr.): 5 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
KPI_TYPE = "bin"


class Test(BaseTest):
    switch_urc_port = False

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        takler_id = ["GP", "GL", "GA", "BD", "QZ"]
        gn = ["GNDTM","GNGNS","GNVTG","GNRMC","GNGSA"]

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 3: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 3: Wait for first fix position', test.dut.dstl_check_ttff() != 0, True)
        test.sleep(20)

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 5: set Nmea Output to modem port - Start')
        test.dut.dstl_collect_result('Step 5: set Nmea Output to modem port', test.dut.dstl_nmea_data_to_modemport())
        if test.dut.dstl_changend_urc_port('mdm') == True:
                test.switch_urc_port = True

        test.log.step('Step 6: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 6: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        for value in range(32):   # 32
            asUrc = [False, False, False, False, False]
            gn_asUrc = [False, False, False, False, False]
            test.log.step('Step 7.' + str(value) + ': set nmea Data for GPS system: '+str(value)+' - Start')
            test.dut.dstl_collect_result('Step 7.' + str(value) + ': set nmea Data for GPS system: '+str(value), test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Data\"," + str(value)),".*OK.*")

            test.dut.at1.read()
            test.sleep(5)
            data = test.dut.at1.read()
            gnss_data= data.split('^')
            for n in range(len(gnss_data)):
                x = gnss_data[n]
                element = x.split(',')
                if (len(element) != 1):
                    for y in range(0, 5):
                        if ((takler_id[y] in element[1]) and ((value & (2 ** y)) == (2 ** y))):
                            asUrc[y] = True
                        if (gn[y] in element[1]):
                            gn_asUrc[y] = True

            for b in range(5):
                test.log.step('Step 8.' + str(value) + ': check if takler_id '+takler_id[b]+' is visible - Start')
                if ((value & (2 ** b)) == (2 ** b)):
                    test.dut.dstl_collect_result('Step 8.' + str(value) + ': takler_id '+takler_id[b]+' visible', asUrc[b])
                else:
                    if (asUrc[b] == True):
                        test.dut.dstl_collect_result('Step 8.' + str(value) + ': takler_id '+takler_id[b]+' is visible - ERROR', False)
                        test.log.info('should not be visible')
                    else:
                        test.dut.dstl_collect_result('Step 8.' + str(value) + ': takler_id ' + takler_id[b] + ' is invisible - OK', True)

            for c in range(5):
                test.log.step('Step 9.' + str(value) + ': check nmea sentences ' + gn[c] + ' is visible - Start')
                if value == 0:
                    if (gn_asUrc[c] == True):
                        test.dut.dstl_collect_result(
                            'Step 9.' + str(value) + ': check nmea sentences ' + gn[c] + ' is visible - ERROR', False)
                        test.log.info('should not be visible')
                    else:
                        test.dut.dstl_collect_result(
                            'Step 9.' + str(value) + ': check nmea sentences ' + gn[c] + ' is invisible - OK', True)
                else:
                    if (gn_asUrc[c] == True):
                        test.dut.dstl_collect_result(
                            'Step 9.' + str(value) + ': check nmea sentences ' + gn[c] + ' is visible - OK', True)
                    else:
                        test.dut.dstl_collect_result(
                            'Step 9.' + str(value) + ': check nmea sentences ' + gn[c] + ' is invisible - ERROR', False)


    def cleanup(test):
        test.log.step('Step 10: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 10: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 11: URC back to nmea port - Start')
        test.dut.dstl_collect_result('Step 11: URC back to nmea port', test.dut.at1._send_and_verify("at^sgpsc=\"Nmea/Output\",\"on\"",".*OK.*"))

        if test.switch_urc_port == True:
            test.dut.dstl_changend_urc_port('app')

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')
        test.kpi_store(name=test.testname+'_kpi', value=test.verdicts_counter_passed, type=KPI_TYPE, total=test.verdicts_counter_total, device=test.dut)

if "__main__" == __name__:
    unicorn.main()
