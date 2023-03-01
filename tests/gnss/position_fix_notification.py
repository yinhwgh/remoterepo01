"""
author: duangkeo.krueger@thalesgroup.com, katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC0103310.001 - PositionFixNotification
intention: Provide AT command to enable and disable the URC type "Position fix notification" if the positioning fix state changes
LM-No (if known): LM0006728.001 - Configurable "Position Fix Notification"
used eq.: DUT-At1, DUT-Nmea, McTest (default: ANT3, could be changed in local_config with other value), roof antenna
execution time (appr.): 3 minutes (in bad cases till 20 minutes)

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.auxiliary.devboard.devboard import *

class Test(BaseTest):
    sgpse_available = False
    mctest_antenna_int = ''
    mctest_antenna = ''
    switch_urc_port = False
    mc_test_ver = ''

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        try:
            test.mctest_present = test.dut.devboard.send_and_verify("MC:VBATT", "OK")
        except Exception as e:
            #print(str(e))
            test.mctest_present = False

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_gps_glonass_systems()
            #test.smbv.dstl_smbv_switch_on_all_system()
        else:
            if test.mctest_present == False:
                err_text = 'no SMBV found and no McTest available -> stop testcase !!!'
                all_results.append([err_text, 'FAILED'])
                test.log.error(err_text)
                test.expect(False, critical=True)

        test.dut.dstl_detect()

    def run(test):

        loop = 3
        if not test.mctest_antenna:             # could be set in local_config with parameter: mctest_antenna to choose another value
            test.mctest_antenna_int = '3'       # default: '3'   -> ANT3
        else:
            test.mctest_antenna_int = test.mctest_antenna  # take parameter mctest_antenna from local_config

        if (test.dut.project == 'BOBCAT' and ( test.dut.step == '2' or test.dut.step == '3')) or test.dut.project == 'VIPER':
            test.sgpse_available = True

       # if test.mctest_present than switch off URCs
        if test.mctest_present:
            test.dut.dstl_switch_off_at_echo(serial_ifc=0)
            test.dut.dstl_switch_off_at_echo(serial_ifc=1)

        test.dut.dstl_switch_off_engine()
        test.log.step('Step 1: Initialize GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialize GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Activate URC for position fix notification  - Start')
        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=1", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 1,.*OK.*")

        if test.dut.dstl_changend_urc_port('mdm') == True:
                test.switch_urc_port = True

        test.dut.dstl_collect_result('Step 2: Activate URC for position fix notification', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"on\"", ".*OK.*"))

        test.log.step('Step 3: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 3: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        for i in range(1, loop+1):
            test.log.step('+++ Test loop: ' + str(i) + ' - Start +++')

            test.log.step('Step 4.'+str(i)+': Wait for fix position - Start')
            data = test.dut.nmea.read()
            test.dut.dstl_collect_result('Step 4.'+str(i)+': Wait for fix position', (test.dut.dstl_check_ttff(120) > 0))
            test.sleep(2)

            test.log.step('Step 5.' + str(i) + ': Wait position fix notification - Start')

            data = test.dut.at1.last_response
            test.log.com('last response data\n' + data)
            data1 = test.dut.at1.read()
            test.log.com('last response data1\n' + data1)

            if ("SGPSE: 1,1" in data) or ("SGPSE: 1,1" in data1):
                test.log.com('COM: last response after SGPSE: 1,1 in data (=last_response)')
                test.dut.dstl_collect_result('Step 5.' + str(i) + ': Wait position fix notification ', True)
            else:
                test.dut.dstl_collect_result('Step 5.' + str(i) + ': Wait position fix notification', test.dut.at1.wait_for("SGPSE: 1,1", timeout=5))
                # test.log.info('last response after SGPSE: 1,1:\n' + test.dut.at1.last_response)

            test.dut.at1.read()

            if test.smbv_active:
                test.log.step('Step 6.' + str(i) + ': Switch off SMBV - Start')
                test.smbv.dstl_smbv_on_off("off")
                test.dut.dstl_collect_result('Step 6.'+str(i)+': Switch off SMBV', True)
            else:
                test.log.step('Step 6.' + str(i) + ': Remove GNSS Antenna - Start')
                test.dut.dstl_collect_result('Step 6.'+str(i)+': Remove GNSS Antenna', test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=int(test.mctest_antenna_int), mode="OFF"))

            test.dut.nmea.read()
            test.log.step('Step 7.'+str(i)+': Check loss of position - Start')
            test.dut.dstl_collect_result('Step 7.'+str(i)+': Check loss of position', test.dut.nmea.wait_for(".*GGA,.*,,,,,0,,,,.*", timeout=45, append=True))

            #test.dut.nmea.read()
            test.log.step('Step 8.'+str(i)+': Wait for GNSS event notification - Start')

            data = test.dut.at1.last_response
            test.log.com('last response data\n' + data)
            data1 = test.dut.at1.read()
            test.log.com('last response data1\n' + data1)

            if ("SGPSE: 1,0" in data) or ("SGPSE: 1,0" in data1):
            # buffer = test.dut.at1.last_response
            # test.dut.at1.read()
            # test.log.com('last response buffer\n' + buffer)
            # if "SGPSE: 1,0" in buffer:
                test.log.com('COM: last response after SGPSE: 1,0 in data (=last_response)')
                test.dut.dstl_collect_result('Step 8.'+str(i)+': Wait for GNSS event notification', True)
            else:
                test.dut.dstl_collect_result('Step 8.'+str(i)+': Wait for GNSS event notification', test.dut.at1.wait_for("SGPSE: 1,0", timeout=60))

            test.dut.at1.read()

            if test.sgpse_available:
                test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE:.*OK.*")

            test.dut.nmea.read()
            test.sleep(5)

            if test.smbv_active:
                test.log.step('Step 9.' + str(i) + ': Switch on SMBV - Start')
                test.smbv.dstl_smbv_on_off("on")
                test.dut.dstl_collect_result('Step 9.' + str(i) + ': Switch on SMBV', True)
            else:
                test.log.step('Step 9.' + str(i) + ': Connect GNSS Antenna - Start')
                test.dut.dstl_collect_result('Step 9.'+str(i)+': Connect GNSS Antenna', test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=int(test.mctest_antenna_int), mode="ON1"))


#            data = test.dut.nmea.read()
            test.dut.nmea.read()
            test.dut.at1.read()

            test.log.step('+++ Test loop: ' + str(i) + ' - End +++')

        test.log.com('\n+++++++++++++++++++++++++++++++++++++++++++++++\n')

        # urc deactivation - check that GNSS Event notification does not occur
        test.log.step('Step 10: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 10: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 11: deactivate \'NMEA/URC (^SGPSE-URC)\' - Start')
        test.dut.dstl_collect_result('Step 11: deactivate \'NMEA/URC (^SGPSE-URC)\'', test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"off\"", ".*OK.*"))

        test.log.step('Step 12: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 12: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 13: Wait for fix position - Start')
        test.dut.nmea.read()
        test.dut.dstl_collect_result('Step 13: Wait for fix position', test.dut.dstl_check_ttff(120) > 0)

        test.sleep(20)
        resp = test.dut.at1.last_response
        test.log.com('response of dut.at1 after 20 seconds:\n' + resp)
        test.log.step('Step 14: Wait for NO position fix notification (^SGPSE: 1,1 - should not occur) - Start')

        if re.match('(?is).*SGPSE: 1,1.*', resp):
            test.dut.dstl_collect_result('Step 14: Wait for NO position fix notification (^SGPSE: 1,1 - should not occur, but did )', False)
        else:
            test.dut.dstl_collect_result('Step 14: Wait for NO position fix notification (^SGPSE: 1,1 - did not occur)', True)

        test.dut.at1.read()


        if test.smbv_active:
            test.log.step('Step 15.' + str(i) + ': Switch off SMBV - Start')
            test.smbv.dstl_smbv_on_off("off")
            test.dut.dstl_collect_result('Step 15.' + str(i) + ': Switch off SMBV', True)
        else:
            test.log.step('Step 15: Remove GNSS Antenna - Start')
            test.dut.dstl_collect_result('Step 15: Remove GNSS Antenna',test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=int(test.mctest_antenna_int), mode="OFF"))


        test.log.step('Step 16: Check loss of position - Start')
        test.dut.dstl_collect_result('Step 16: Check loss of position', test.dut.nmea.wait_for(".*GGA,.*,,,,,0,,,,.*", timeout=75))

        sleep_time = 75
        test.sleep(sleep_time)
        resp = test.dut.at1.last_response
        test.log.com('response of dut.at1 after ' + str(sleep_time) + ' seconds:\n' + resp)
        test.log.step('Step 17: Wait for NO position fix notification (^SGPSE: 1,0 - should not occur) - Start')
        if re.match('(?is).*SGPSE: 1,0.*', resp):
            test.dut.dstl_collect_result('Step 17: Wait for NO position fix notification (^SGPSE: 1,0 - should not occur, but did )', False)
        else:
            test.dut.dstl_collect_result('Step 17: Wait for NO position fix notification (^SGPSE: 1,0 - did not occur)', True)

        test.log.step('Step 18: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 18: Switch off GNSS engine', test.dut.dstl_switch_off_engine())


        if test.smbv_active:
            test.log.step('Step 19.' + str(i) + ': Switch on SMBV - Start')
            test.smbv.dstl_smbv_on_off("on")
            test.dut.dstl_collect_result('Step 19.' + str(i) + ': Switch on SMBV', True)
        else:
            test.log.step('Step 19: Switch on GNSS Antenna - Start')
            test.dut.dstl_collect_result('Step 19: Connect GNSS Antenna',test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=int(test.mctest_antenna_int), mode="ON1"))


    def cleanup(test):
        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()
        else:
            if test.mctest_present:
                test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=int(test.mctest_antenna_int), mode="ON1")

        #global mctest_antenna_int
        test.log.step('Step 20: Deactivate URC and switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 20: Deactivate URC and switch off GNSS engine', test.dut.dstl_switch_off_engine() and test.dut.at1.send_and_verify("at^sgpsc=\"NMEA/URC\",\"off\"", ".*OK.*"))

        if test.sgpse_available:
            test.dut.at1.send_and_verify("at^sgpse=0", ".*OK.*")
            test.dut.at1.send_and_verify("at^sgpse?", ".*SGPSE: 0,.*OK.*")

        if test.switch_urc_port == True:
            test.dut.dstl_changend_urc_port('app')

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
