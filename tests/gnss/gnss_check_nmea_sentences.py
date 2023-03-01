"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number:
intention:
LM-No (if known):
used eq.: DUT-At1, SMBV (sometimes also roof antenna works)
execution time (appr.):  min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
import codecs

class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        nmea=["RMC",
              "GGA",
              "VTG",
              "GNGNS",
              "GNGSA",]

        sat = ['GPGSV',
               'GLGSV',
               'GAGSV',
               'BDGSV',
               'QZGSV']

        check_sum_parameter=[13,
                             14,
                             9,
                             13,
                             18]

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 3: Wait for first fix position - Start')
        test.dut.dstl_collect_result('Step 3: Wait for first fix position', test.dut.dstl_check_ttff() != 0)
        test.sleep(240)

        test.dut.nmea.read()
        test.sleep(5)
        data = test.dut.nmea.read()
        gnss_data = data.split('\r\n')

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        token=[gnss_data[n].split(',') for n in range(len(gnss_data))]

        for x in range(len(nmea)):
            result=True
            test.log.step('Step 5.'+str(x+1)+': NMEA '+nmea[x]+' - Start')
            for n in range(len(token)):
                if nmea[x] in token[n][0]:
                    test.log.info("found: "+gnss_data[n])
                    test.log.info('check Parameter: '+str(check_sum_parameter[x]) +'/'+ str(gnss_data[n].count(',')))
                    if check_sum_parameter[x] != gnss_data[n].count(','):
                        result = False
                        test.log.error("paramter failed")
                    check_sum = 0
                    for i in range(len(gnss_data[n])):
                        if '*' in gnss_data[n][i + 1]:
                            break
                        check_sum = check_sum ^ ord(gnss_data[n][i + 1])
                    check_sum = format(check_sum, "X")
                    test.log.info('check sum: '+str(check_sum)+'/'+str(token[n][check_sum_parameter[x]]))
                    if str(check_sum) not in str(token[n][check_sum_parameter[x]]):
                        result = False
                        test.log.error("check sum failed")
                    test.dut.dstl_collect_result('Step 5.'+str(x+1)+': NMEA '+nmea[x], result)
                    break

                if len(token) == n+1:
                    test.dut.dstl_collect_result('Step 5.'+str(x+1)+': NMEA '+nmea[x], False)


        for x in range(len(sat)):
            test.log.step('Step 6.'+str(x+1)+': NMEA ' + str(sat[x])+' - Start' )
            if sat[x] in "QZGSV" and test.smbv_active:
                test.smbv.dstl_smbv_switch_on_gps_qzss_systems()
                test.dut.dstl_switch_on_engine()
                test.dut.dstl_check_ttff()
                test.sleep(240)
                test.dut.nmea.read()
                test.sleep(5)
                data = test.dut.nmea.read()
                gnss_data = data.split('\r\n')
                token = [gnss_data[n].split(',') for n in range(len(gnss_data))]

            result = True
            for n in range(len(gnss_data)):
                if sat[x] in token[n][0]:
                    for loop in range(int(token[n][1])):
                        test.log.info("found: " + gnss_data[n+loop])
                        if token[n+loop][1] not in token[n+loop][2] or int(token[n+loop][3])%4 == 0:
                            test.log.info('check number of SVs visible: cycle '+str(loop+1))
                            if gnss_data[n+loop].count(',')- 20 != 0:
                                result = False
                                test.log.error("SV's failed: "+gnss_data[n+loop])
                        else:
                            test.log.info('check number of SVs visible: cycle ' + str(loop + 1))
                            if gnss_data[n+loop].count(',') - 4*(int(token[n+loop][3])%4)-4 != 0:
                                result = False
                                test.log.error("SV's failed: "+gnss_data[n+loop])

                        check_sum = 0
                        for i in range(len(gnss_data[n+loop])):
                            if '*' in gnss_data[n+loop][i + 1]:
                                break
                            check_sum = check_sum ^ ord(gnss_data[n+loop][i + 1])
                        check_sum = format(check_sum, "X")
                        test.log.info('check sum: ' + str(check_sum) + '/' + str(token[n+loop][gnss_data[n+loop].count(',')]))
                        if str(check_sum) not in str(token[n+loop][gnss_data[n+loop].count(',')]):
                            result = False
                            test.log.error("check sum failed")

                    test.dut.dstl_collect_result('Step 6.'+str(x+1)+': NMEA ' + str(sat[x]), result)
                    break



                if len(token) == n + 1:
                    test.dut.dstl_collect_result('Step 6.'+str(x+1)+': NMEA: ' + str(sat[x]), False)




    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 7: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 7: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 8: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 8: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())
        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
