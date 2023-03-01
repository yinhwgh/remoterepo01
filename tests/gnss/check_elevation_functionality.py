"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
intention:  Minimum GNSS Elevation Angle (5-45 degrees) is configurable
LM-No (if known):
used eq.: DUT-At1,
execution time (appr.): 25 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *


class Test(BaseTest):
    def setup(test):
        err_text = 'no SMBV found -> stop testcase'
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.smbv = SMBV(test.plugins.network_instrument)

        if test.smbv.dstl_check_smbv():
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()
        else:
            all_results.append([err_text, 'FAILED'])
            test.log.error(err_text)
            test.expect(False, critical=True)

        test.dut.dstl_detect()

    def run(test):
        angle = ['5', '20']
        notSvs = ['03', '11', '20', '21', '22',
                  "04","13","17","23","25","31"]

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.smbv.dstl_smbv_change_value("BB:GPS:LOC:SEL \"Moscow\"")
        test.smbv.dstl_smbv_change_value("BB:GPS:NAV:SIM:DATE 2018, 08, 19")
        test.smbv.dstl_smbv_change_value("BB:GPS:SAT:COUNT 16")

        for i in range(2):

            test.smbv.dstl_smbv_change_value("BB:GPS:NAV:SIM:TIME 15, 30, 00")

            test.log.step('Step 2.'+str(i+1)+': Configure elevation angle for '+angle[i]+' degree - Start')
            test.dut.dstl_collect_result('Step 2.'+str(i+1)+': Configure elevation angle'+angle[i]+' degree', test.dut.at1.send_and_verify('at^SGPSC=Sens/MinElevAngle,' + angle[i], ".*OK.*"))

            test.log.step('Step 3.' + str(i + 1) + ': Configure elevation angle for ' + angle[i] + ' degree - Start')
            test.dut.dstl_collect_result('Step 3.' + str(i + 1) + ': Configure elevation angle' + angle[i] + ' degree', test.dut.at1.send_and_verify('at^SGPSC?', "\"Sens/MinElevAngle\",\""+angle[i]+"\""))

            test.log.step('Step 4.'+str(i+1)+': Restart module - Start')
            test.dut.dstl_collect_result('Step 4.'+str(i+1)+': Restart module', test.dut.dstl_restart())

            test.log.step('Step 5.'+str(i+1)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 5.'+str(i+1)+': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.log.step('Step 6.'+str(i+1)+': Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 6.'+str(i+1)+': Wait for first fix position', test.dut.dstl_check_ttff() != 0)

            test.sleep(240)

            test.dut.nmea.read()
            test.sleep(5)
            data = test.dut.nmea.read()
            nmea_data = data.split('\n')

            test.log.step('Step 7.' + str(i + 1) + ': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i + 1) + ': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            test.log.step('Step 8.'+str(i+1)+': check SVs - Start')
            testresult = True
            gsa=''
            gga=''
            for n in range(len(nmea_data)):
                if "GPGGA" in nmea_data[n]:
                    gga = nmea_data[n].split(',')
                    test.log.com("Total number of satellites: " + gga[7])
                    test.log.com(nmea_data[n])
                    for y in range(len(nmea_data)):
                        if "GSA" in nmea_data[y]:
                            gsa = nmea_data[y].split(',')
                            print("\n" + str(gsa) + "\n")
                            test.log.com("sv Max: "+ gga[7])
                            break
                    break
            for n in range(3,int(gga[7])):
                print(str(gsa))
                test.log.com("SV_ID: " + gsa[n])
                if gsa[n] in notSvs[n+i*5]:
                    test.log.com("SV_ID: " + gsa[n]+" is found")
                else:
                    test.log.com("SV_ID: " + gsa[n]+" is not found")
                    if n < 5:
                        testresult = False
            test.dut.dstl_collect_result('Step 8.' + str(i + 1) + ': Check SVs', testresult)

            test.smbv.dstl_smbv_change_value("BB:GPS:NAV:SIM:TIME 17, 40, 00")

            test.log.step('Step 9.'+str(i+1)+': Start cold start - Start')
            test.dut.dstl_collect_result('Step 9.'+str(i+1)+': Start cold start', test.dut.dstl_coldstart())

            test.log.step('Step 10.'+str(i+1)+': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 10.'+str(i+1)+': Switch off GNSS engine', test.dut.dstl_switch_on_engine())

            test.log.step('Step 11.'+str(i+1)+': Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 11.'+str(i+1)+': Wait for first fix position', test.dut.dstl_check_ttff() != 0)

            test.sleep(240)

            test.dut.nmea.read()
            test.sleep(5)
            data = test.dut.nmea.read()
            nmea_data = data.split('\n')

            test.log.step('Step 12.'+str(i+1)+': Check that the satellite ID - Start')
            for n in range(len(nmea_data)):
                if "GPGGA" in nmea_data[n]:
                    gga = nmea_data[n].split(',')
                    test.log.com("Total number of satellites: " + gga[7])
                    test.log.com(nmea_data[n])
                    for y in range(len(nmea_data)):
                        if "GSA" in nmea_data[y]:
                            gsa = nmea_data[y].split(',')
                            print("\n" + str(gsa) + "\n")
                            test.log.com("sv Max: "+ gga[7])
                            break
                    break
            for n in range(3,int(gga[7])):
                print(str(gsa))
                test.log.com("SV_ID: " + gsa[n])
                if gsa[n] in notSvs[n+5]:
                    test.log.com("SV_ID: " + gsa[n]+" is found")
                else:
                    test.log.com("SV_ID: " + gsa[n]+" is not found")
                    if n < 5:
                        testresult = False
            test.dut.dstl_collect_result('Step 12.' + str(i + 1) + ': Check SVs', testresult)

            test.log.step('Step 13.'+str(i+1)+': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 13.'+str(i+1)+': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

    def cleanup(test):
        if test.smbv.dstl_check_smbv():
            test.smbv.dstl_smbv_close()

        test.log.step('Step 14: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 14: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 15: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 15: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.nmea.read()
        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
