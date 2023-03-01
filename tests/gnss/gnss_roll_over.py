"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
intention: Testing whether the date is correct when the gps week exceeds the gps minimum number +1024
TC-number: TC0094432.001
LM-No (if known): LM0003811 - Bobcat, Miami_04
used eq.: DUT-At1, SMBV
execution time (appr.): 45 min
"""

import unicorn
import os
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    # default value 1738 - 0xca 0x06 0x00 0x00 => enddate: 12.12.2032
    nvitem_06264_1738 = "002B8E452171F577199AC08345FB01503361C08345FB01503361C08345FB01503361C08345FB0150336155"
    debug_int = False    # default: False=NV-item not read, True=NV-item will be read

    def read_nv_item_06264(test):
        if test.debug_int == True and test.dut.project != 'SERVAL':
            # internal only
            test.log.com("Read NV-item 06264")
            diag_port = test.dut.diag.port
            diag_port_num = diag_port.replace('COM', '')
            print('com_diag_num: ' + diag_port_num)
            test.log.com('com_diag_num: ' + diag_port_num)
            cmd_line = 'o:\\aktuell\z_sw13\\tools\qnvitem.exe -v -p ' + diag_port_num + ' -r 6264'
            test.log.com('cmd_line: ' + cmd_line)
            lines = os.popen(cmd_line).readlines()
            for line in lines:
                test.log.com(line.strip())
        return

    def setup(test):
        err_text = 'no SMBV found -> stop testcase'
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.smbv = SMBV(test.plugins.network_instrument)

        if not test.smbv.dstl_check_smbv():
            all_results.append([err_text, 'FAILED'])
            test.log.error(err_text)
            test.expect(False, critical=True)

        test.dut.dstl_detect()

    def run(test):
        # GPS-roll over: first GPS date: 06.01.1990 => valid period 06.01.1980 - 22.08.1999
        #                duration of valid period: 1024 weeks (tool for calculation: https://www.topster.de/kalender/zeitrechner.php)
        # QCT default setting (state 05.03.2020) of NV-item 06264 is 1738 (0xca 0x06 0x00 0x00) => valid period 28.04.2013 - 12.12.2032
        #
        #

        # date = [["2019, 05, 05","050519"],
        #         ["2019, 05, 12","120519"],
        #         ["2019, 05, 19","190519"],        # after restart NV-item 06264 should be: 2054 - 0x06 0x08 0x00 0x00 => enddate: 01.02.2039
        #         ["2038, 12, 19","191238"],
        #         ["2039, 02, 02","190619"]]        # here rollover occurred, switch back

        date = [["2020, 02, 05","050220"],
                ["2020, 02, 12","120220"],
                ["2020, 02, 19","190220"],        # after restart NV-item 06264 should be: 2093 - 0x2d 0x08 0x00 0x00 => enddate: 05.10.2039
                ["2039, 08, 15","150839"],
                ["2040, 01, 13","290520"]]        # here rollover occurred, switch back

        test.log.com("Setting SMBV")
        test.smbv.dstl_smbv_switch_on_gps_glonass_systems(date=date[0][0])

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        test.log.step('Step 2: Write NV-item 06264 with 1738 - Start')
        test.dut.dstl_collect_result('Step 2: Write NV-item 06264 with 1738', test.dut.dstl_send_nv_item(test.nvitem_06264_1738))

        test.sleep(2)

        test.log.step('Step 3: Restart Module - Start')
        test.dut.dstl_collect_result('Step 3: Restart Module', test.dut.dstl_restart())

        test.read_nv_item_06264()

        for i in range(len(date)):
            test.log.info("***** " + str(i+1) +". Time date : " + date[i][0] + " *****")
            test.smbv.dstl_smbv_change_date(date[i][0])

            if test.dut.project != 'SERVAL':
                test.log.step('Step 4.' + str(i + 1) + ': Start cold start - Start')
                test.dut.dstl_collect_result('Step 4.' + str(i + 1) + ': Start cold start', test.dut.dstl_coldstart())

            test.log.step('Step 5.'+str(i+1)+': Switch on GNSS engine - Start')
            test.dut.dstl_collect_result('Step 5.'+str(i+1)+': Switch on GNSS engine', test.dut.dstl_switch_on_engine())

            test.log.step('Step 6.'+str(i+1)+': Wait for first fix position - Start')
            test.dut.dstl_collect_result('Step 6.'+str(i+1)+': Wait for first fix position', test.dut.dstl_check_ttff() != 0, True)

            if i <= 2:
                test.sleep(610)
            else:
                test.sleep(30)

            test.dut.nmea.read()
            test.sleep(5)
            nmea_data = test.dut.nmea.read()

            test.log.step('Step 7.' + str(i+1) + ': Check RMC date: '+ date[i][1] + ' - Start')
            test.dut.dstl_collect_result('Step 7.' + str(i+1) + ': Check RMC date: ' + date[i][1], test.dut.dstl_find_nmea_data(nmea_data, "RMC", date[i][1]))

            test.log.step('Step 8.' + str(i+1) + ': Switch off GNSS engine - Start')
            test.dut.dstl_collect_result('Step 8.' + str(i+1) + ': Switch off GNSS engine', test.dut.dstl_switch_off_engine())

            if i == 2:  # NV-item: 06264 must be 2093 after 3. time and restart)
                test.log.step('Step 8.' + str(i+1) + '.1: Restart module for activate new NV-item value (06264 must be "2093 - 0x2d 0x08 0x00 0x00" after 3. date) - Start')
                test.dut.dstl_collect_result('Step 8.' + str(i+1) + '.1: Restart module for activate new NV-item value (06264 must be "2093 - 0x2d 0x08 0x00 0x00" after 3. date)', test.dut.dstl_restart())

            test.read_nv_item_06264()


    def cleanup(test):
        if test.smbv.dstl_check_smbv():
            test.smbv.dstl_smbv_close()

        test.log.step('Step 9: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 9: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 10: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 10: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        test.log.step('Step 11: Write NV-item 06264 with 1738 - Start')
        test.dut.dstl_collect_result('Step 11: Write NV-item 06264 with 1738', test.dut.dstl_send_nv_item(test.nvitem_06264_1738))

        test.log.step('Step 12: Restart Module - Start')
        test.dut.dstl_collect_result('Step 12: Restart Module', test.dut.dstl_restart())

        test.read_nv_item_06264()

        test.sleep(1)

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

    if "__main__" == __name__:
        unicorn.main()
