"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096241.001 - GNSS_Raw_Data
intention: This test is built to check the structure of arriving GNSS raw data on a serial port.
           That means that we collect raw data samples for a specific time and analyze them afterwards.
           The test will dissect the data (TLV Format) into QMI Message Types and verify their given
           message length parameters of their headers.
           The content of the data are NOT part of the test and can't be analyzed or verified (for now)
           The header of a message consists of:
           sequence start flag 0x5A                             1 byte
           QMI_LOC_EVENT_ID (0x0024, 0x0025, 0x0086, 0x0087)    2 byte
           length of the QMI message                            2 byte

           The raw data is scanned for a sequence start flag. If one is found, the message length will be extracted. Then the length is compared to distance of the next occurrence of sequence start flag. If they are the same, the message is verified in length, the messages ID is extracted and the message is logged as verified.
           If the message could no be verified, the code will be logged with "NOT FOUND" as message type and raises the error counter -> The test will fail then. 
LM-No (if known): LM0006181.00x - GNSS raw data
used eq.: DUT-At1, DUT-Nmea
execution time (appr.): 4 minutes
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.raw_data import *


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        (test.smbv_active, test.smbv) = test.dut.dstl_select_antenna()
        if test.smbv_active:
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()

        test.dut.dstl_detect()

    def run(test):
        workspace = test.workspace

        test.log.step('Step 1: Initialise_GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise_GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 2: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        test.log.step('Step 3: Wait for first fix position and check time for cold start - Start')
        test.dut.dstl_collect_result( 'Step 3: Wait for first fix position and check time for cold start ', test.dut.dstl_check_ttff() != 0)

        test.sleep(5)

        test.log.step('Step 4: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 4: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 5: Set Nmea data format to raw data - Start')
        test.dut.dstl_collect_result('Step 5: Set Nmea data format to raw data',test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Data/Format\",\"raw\""))

        test.log.step('Step 6: Set Nmea raw mask to default value - Start')
        test.dut.dstl_collect_result('Step 6: Set Nmea raw mask to default value',test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Data/RawMask\",15"))

        test.log.step('Step 7: Switch on GNSS engine - Start')
        test.dut.dstl_collect_result('Step 7: Switch on GNSS engine', test.dut.dstl_switch_on_engine())

        readtime_rawdata = 2
        read_loop = 60
        data = b""    # bytes, binary string
        test.dut.nmea.read()
        test.log.step("*** Collecting data with %s seconds timeout ***" % (readtime_rawdata*read_loop))
        for i in range(read_loop):
            # loop because Unicorn read_binary function has problems with buffer overflow
            #test.dut.nmea.read()
            data = data + test.dut.nmea.read_binary(timeout=readtime_rawdata)

        test.log.step('Step 8: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 8: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 9: Analysis of raw data - Start')
        analyes_res, event_id_count_lst = test.dut.dstl_analyse_raw_data(workspace, data)
#        test.dut.dstl_collect_result('Step 9: Analysis of raw data', test.dut.dstl_analyse_raw_data(workspace, data))
        test.dut.dstl_collect_result('Step 9: Analysis of raw data', analyes_res)

        test.log.step('Step 10: Analysis of all Event_IDs - Start')
        dstl.log.com("----------------------------------------")
        all_events_occur = True
        for i in range(len(event_id_count_lst)):
            if event_id_count_lst[i][1] > 0:
                dstl.log.com("Event_ID: " + str(event_id_count_lst[i][0]) + " : " + str(event_id_count_lst[i][1]) + " time(s) -> OK - occurs at least 1 time")
            else:
                dstl.log.com("Event_ID: " + str(event_id_count_lst[i][0]) + " : " + str(event_id_count_lst[i][1]) + " time -> ERROR - did not occurs")
                all_events_occur = False
        test.dut.dstl_collect_result('Step 10: Analysis of all Event_IDs', all_events_occur)


    def cleanup(test):

        if test.smbv_active == True:
            test.smbv.dstl_smbv_close()

        test.log.step('Step 11: Switch off GNSS engine - Start')
        test.dut.dstl_collect_result('Step 11: Switch off GNSS engine', test.dut.dstl_switch_off_engine())

        test.log.step('Step 12: Set back NMEA data format to NMEA - Start')
        test.dut.dstl_collect_result('Step 12: Set back NMEA data format to NMEA',test.dut.at1.send_and_verify("at^sgpsc=\"Nmea/Data/Format\",\"NMEA\""))

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
