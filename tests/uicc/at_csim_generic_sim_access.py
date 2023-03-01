#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0065609.001,TC0065609.002 - AT+CSIM Generic SIM Access

'''

AT+CSIM allows direct control of the SIM.
For parameter and SIM result coding please refer GSM 11.11.
However, only the following SIM commands are supported by AT+CSIM:
SELECT, SEEK, STATUS, READ BINARY, UPDATE BINARY, READ RECORD, INCREASE and UPDATE RECORD.

A special sim card will be used  especially during test the INCREASE functionality.

Detail info can be found from GSM11.11 and ETSI TS 102 221

'''

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usim import get_df_name
import re

class TpAtCmeeBasic(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("1. Disble SIM PIN lock before testing  ")
        test.dut.dstl_unlock_sim()
        test.log.info("1. Wait about 10s Before SIM is ready")

    def run(test):
        test.log.info("1. Test AT+CSIM SELECT Functionality")
        ## SELECT CLA is '0X' or '4X' or '6X', INS is 'A4'

        # Scenario1: P1=00 Select DF, EF or MF by file id , P2=04 Return FCP Template
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1 = 00 Select DF, EF or MF by file id , P2 = 04 Return FCP Template")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 3F00 then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004023F00"', ".*(61).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*(62\w+(90\d\d|91\w\w)).*", timeout=30))

        test.log.info("Select 2F00 then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004022F00"', ".*(61).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*(62\w+(90\d\d|91\w\w)).*", timeout=30))

        test.log.info("Select 7F10 then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004027F10"', ".*(61).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*(62\w+(90\d\d|91\w\w)).*", timeout=30))

        test.log.info("Select 6F44 then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004026F44"', ".*(61).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*(62\w+(90\d\d|91\w\w)).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1 = 00 Select DF, EF or MF by file id , P2 = 0C No data returned")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 3F00")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000C023F00"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.log.info("Select 2F00")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000C022F00"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.log.info("Select 7F10")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000C027F10"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.log.info("Select 6F44")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4000C026F44"', ".*(90\d\d|91\w\w).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1 = 03 Select parent DF of the current DF, P2 = 04 Return FCP template  3F00\\7F10\\5F3A")
        test.log.info("*************************************************************************************************************")
        if test.dut.platform is 'QCT':
            test.log.info("QCT platform does not support P1 b1=1 of select,please refer to IPIS100322524")
        else:
            test.log.info("Select 5F3A then select its parent DF 7F10 then Get Response")
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004023F00"', ".*(61\w\w).*", timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004027F10"', ".*(61\w\w).*", timeout=30))
            test.expect(
                test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40004025F3A"', ".*(61\w\w).*", timeout=30))
            # Select 7F10 via 00A4030400
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00A4030400"', ".*(61\w\w).*", timeout=30))
            test.expect(
                test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=04 Selection by DF name, P2=04 Return FCP template  AID: Get From 2F00")
        test.log.info("*************************************************************************************************************")
        ADF_1 = test.dut.dstl_get_df_name('01')

        test.expect(test.dut.at1.send_and_verify('AT+CSIM=42,"00A4040410{}"'.format(ADF_1), ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=04 Selection by DF name, P2=04 Return FCP template  AID: Get From 2F00")
        test.log.info("*************************************************************************************************************")
        ADF_2 = test.dut.dstl_get_df_name('02')
        if ADF_2:
            if test.dut.platform is 'QCT':
                test.log.info(
                    "For QCT platform need to open a new logic channel before select the second AID,please refer to IPIS100321831")
                test.expect(
                    test.dut.at1.send_and_verify('AT+CSIM=10,"0070000001"', ".OK.*", timeout=30))
                test.expect(
                    test.dut.at1.send_and_verify('AT+CSIM=42,"01A4040410{}"'.format(ADF_2), ".*(61\w\w).*", timeout=30))
                test.expect(
                    test.dut.at1.send_and_verify('AT+CSIM=10,"01C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
            else:
                test.expect(
                    test.dut.at1.send_and_verify('AT+CSIM=42,"00A4040410{}"'.format(ADF_2), ".*(61\w\w).*", timeout=30))
                test.expect(
                    test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
        else:
            test.log.info('ADF2 is none')


        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=04 Selection by DF name, P2=0C No data returned  AID: AID: Get From 2F00")
        test.log.info("*************************************************************************************************************")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=42,"00A4040C10{}"'.format(ADF_1), ".*(90\d\d|91\w\w).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=04 Selection by DF name, P2=0C No data returned  AID: AID: Get From 2F00")
        test.log.info("*************************************************************************************************************")
        if ADF_2:
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=42,"00A4040C10{}"'.format(ADF_2), ".*(90\d\d|91\w\w).*", timeout=30))
        else:
            test.log.info('ADF2 is none')

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=08 Select by path from MF , P2=04 Return FCP template")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 7F106F3A then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A40804047F106F3A"', ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A40804047F106F3B"', ".*(61\w\w).*", timeout=30))
        test.log.info("Select 7F106F3B then Get Response")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=08 Select by path from MF , P2=0C No data returned")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 7F106F3A")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3A"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.log.info("Select 7F106F3B")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3B"', ".*(90\d\d|91\w\w).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=09 Select by path from current DF , P2=04 Return FCP template")
        test.log.info("*************************************************************************************************************")
        if test.dut.platform is 'QCT':
            test.log.info("QCT platform does not support P1 b1=1 of select,please refer to IPIS100322524")
        else:
            test.log.info("Select 6F43 then Get Response")
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40904026F43"', ".*(61\w\w).*", timeout=30))
            test.expect(
                test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
            test.log.info("Select 6F40 then Get Response")
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A40904026F40"', ".*(61\w\w).*", timeout=30))
            test.expect(
                test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SELECT: P1=09 Select by path from current DF , P2=0C No data returned")
        test.log.info("*************************************************************************************************************")
        if test.dut.platform is 'QCT':
            test.log.info("QCT platform does not support P1 b1=1 of select,please refer to IPIS100322524")
        else:
            test.log.info("Select 6F43")
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4090C026F43"', ".*(90\d\d|91\w\w).*", timeout=30))
            test.log.info("Select 6F40")
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A4090C026F40"', ".*(90\d\d|91\w\w).*", timeout=30))

        test.log.info("2. Test AT+CSIM STATUS Functionality")
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=00 No indication , P2=00 Response parameters and data are identical to the response parameters and data of the SELECT command")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select ADF1 then Get STATUS")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSIM=42,"00A4040410{ADF_1}"', ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("Select 7F106F3A then Get STATUS")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3A"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=00 No indication , P2=01 The DF name TLV-object of the currently selected application is returned")
        test.log.info( "*************************************************************************************************************")
        test.log.info("Get STATUS Return current AID of 7F106F3A")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2000100"', ".*(A0\w+(9000|91\w\w)).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=00 No indication , P2=0C No data returned")
        test.log.info("*************************************************************************************************************")
        test.log.info("Get STATUS of 7F106F3A, but no data returned")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2000C00"', ".*((9000|91\w\w)).*", timeout=30))


        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=01 Current application is initialized in the terminal , P2=00 Response parameters and data are identical to the response parameters and data of the SELECT command")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select ADF1 then Get STATUS")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSIM=42,"00A4040410{ADF_1}"', ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2010000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("Select 7F106F3A then Get STATUS")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3A"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2010000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=01 Current application is initialized in the terminal , P2=01 The DF name TLV-object of the currently selected application is returned")
        test.log.info( "*************************************************************************************************************")
        test.log.info("Get STATUS Return current AID of 7F106F3A")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2010100"', ".*(A0\w+(9000|91\w\w)).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=01 Current application is initialized in the terminal , P2=0C No data returned")
        test.log.info("*************************************************************************************************************")
        test.log.info("Get STATUS of 7F106F3A, but no data returned")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2010C00"', ".*((9000|91\w\w)).*", timeout=30))


        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=02 The terminal will initiate the termination of the current application, P2=00 Response parameters and data are identical to the response parameters and data of the SELECT command")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select ADF1 then Get STATUS")
        test.expect(test.dut.at1.send_and_verify(f'AT+CSIM=42,"00A4040410{ADF_1}"', ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2020000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("Select 7F106F3A then Get STATUS")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3A"', ".*(90\d\d|91\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2020000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=02 The terminal will initiate the termination of the current application, P2=01 The DF name TLV-object of the currently selected application is returned")
        test.log.info( "*************************************************************************************************************")
        test.log.info("Get STATUS Return current AID of 7F106F3A")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2020100"', ".*(A0\w+(90\d\d|91\w\w)).*", timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_STATUS: P1=02 The terminal will initiate the termination of the current application, P2=0C No data returned")
        test.log.info("*************************************************************************************************************")
        test.log.info("Get STATUS of 7F106F3A, but no data returned")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"80F2020C00"', ".*(90\d\d|91\w\w).*", timeout=30))

        test.log.info("3. Test AT+CSIM UPDAT_BINARY&READ_BINARY Functionality")
        ## UPDATE BINARY CLA is '0X' or '4X' or '6X', INS is 'D6'
        ## READ BINARY is '0X' or '4X' or '6X', INS is 'B0'
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_READ BINARY: P1=00 Offset to the first byte to read is 0 , P2=00 the low part of the offset")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 7FFF6F05 then read all the bianry data ")
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A40804047FFF6F05"', ".*(61\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00C0000000"', ".*.*(62\w+(9000|91\w\w)).*.*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B0000000"', ".*(\w{6}(9000|91\w\w)).*", timeout=30))
        data_len=len(re.search('CSIM: \w+,"(\w+)9000"',test.dut.at1.last_response).group(1))
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_UPDATE BINARY: P1=00 Offset to the first byte to read is 0 , P2=00 the low part of the offset")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 7FFF6F05 then UPDATE the bianry data to ABCDEF123456")
        binary_string = "ABCDEF123456" # Original string will be write to 7FFF605
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=22,"00D6000006{}"'.format(binary_string), ".*(\w*(9000|91\w\w)).*", timeout=30))

        for offset_bytes in range(int(len(binary_string)/2)):
            test.log.info("*************************************************************************************************************")
            test.log.info("CSIM_READ BINARY: P1=00 Offset to the first byte to read is 0 , P2={} offset is byte {}".format(offset_bytes,offset_bytes))
            test.log.info("*************************************************************************************************************")
            test.log.info("Read Binary of 6F05, result should be {}".format(binary_string[offset_bytes*2:]))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B0000{}00"'.format(offset_bytes), f'.*({binary_string[offset_bytes*2:]}{"F"*(data_len-12)}(9000|91\w\w)).*', timeout=30))

        update_binary_string = "11" # A new byte string will be updated to 7FFF605 with different offset
        for offset_bytes in range(int(len(binary_string)/2)):
            test.log.info("*************************************************************************************************************")
            test.log.info("CSIM_UPDATE BINARY: P1=00 Offset to the first byte to read is 0 , P2={} offset is byte {}".format(offset_bytes,offset_bytes))
            test.log.info("*************************************************************************************************************")
            test.log.info("Select 7FFF6F05 then UPDATE the bianry data to {}".format(update_binary_string))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=12,"00D6000{}01{}"'.format(offset_bytes,update_binary_string), ".*(\w*(9000|91\w\w)).*", timeout=30))
            binary_string = binary_string.replace(binary_string[offset_bytes*2:(offset_bytes+1)*2],update_binary_string)
            test.log.info("Read the whole bianry data, it should be {}".format(binary_string))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B0000000"', f'.*({binary_string}{"F"*(data_len-12)}(9000|91\w\w)).*', timeout=30))

        test.log.info("4. Test AT+CSIM UPDAT_Record, READ_Recodr and SEARCH_Record Functionality")

        ## UPDAT_Record CLA is '0X' or '4X' or '6X', INS is 'DC'
        ## READ_Record CLA is '0X' or '4X' or '6X', INS is 'B2'
        ## SEARCH_Record CLA is '0X' or '4X' or '6X', INS is 'A2'
        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_UPDATE RECORD: P1= Record number , P2= 04 Absolute/current mode, the record number is given in P1")
        test.log.info("*************************************************************************************************************")
        test.log.info("Select 7F106F3A then UPDATE the bianry data to {}") # 7F106F3A Size = 34 bytes, Record Total =250
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A4080C047F106F3A"', ".*((9000|91\w\w)).*", timeout=30))
        test.log.info("Empty 30 records with FFFF")
        P1 = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        for record_index in range(15):
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC0{}0422{}"'.format(P1[record_index],'F'*68), ".*((9000|91\w\w)).*", timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC1{}0422{}"'.format(P1[record_index],'F'*68), ".*((9000|91\w\w)).*", timeout=30))
        test.log.info("Update 30 records with different values")
        for record_index in range(15):
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC0{}0422{}"'.format(P1[record_index],P1[record_index]*68), ".*((9000|91\w\w)).*", timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC1{}0422{}"'.format(P1[record_index],P1[record_index]*68), ".*((9000|91\w\w)).*", timeout=30))


        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_READ RECORD: P1= Record number , P2= 04 Absolute/current mode, the record number is given in P1")
        test.log.info("*************************************************************************************************************")
        test.log.info("Read 30 records and check if the value is correct")
        for record_index in range(15):
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B20{}0422"'.format(P1[record_index]), '.*({}{{68}}(9000|91\w\w)).*'.format(P1[record_index]), timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B21{}0422"'.format(P1[record_index]), '.*({}{{68}}(9000|91\w\w)).*'.format(P1[record_index]), timeout=30))


        test.log.info("*************************************************************************************************************")
        test.log.info("CSIM_SEARCH RECORD: P1= Record number , P2= 04 Absolute/current mode, the record number is given in P1")
        test.log.info("*************************************************************************************************************")
        test.log.info("Update index 1,2,3,4,5,6,10,17 to 1111 then search ")
        for i in range(6):
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC0{}0422{}"'.format(i+1,'1'*68), ".*((9000|91\w\w)).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=78,"00DC0A0422{}"'.format('1' * 68), ".*((9000|91\w\w)).*",timeout=30))

        test.log.info("SEARCH all record")
        # Le= empty, no record numbers will be returned. Total 8 recorder were found
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=14,"00A20104021111"', ".*((9000|91\w\w)|6108).*", timeout=30))
        # Le = 00 Total 8 recorder will be found
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111100"', ".*((0102030405060A11(9000|91\w\w))|6108).*", timeout=30))

        # Search the 1st record, return the index
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111101"', ".*(01(9000|91\w\w))|(6101).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111102"', ".*(0102(9000|91\w\w))|(6102).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111103"', ".*(010203(9000|91\w\w))|(6103).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111104"', ".*(01020304(9000|91\w\w))|(6104).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111105"', ".*(0102030405(9000|91\w\w))|(6105).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111106"', ".*(010203040506(9000|91\w\w))|(6106).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111107"', ".*(0102030405060A(9000|91\w\w))|(6107).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111108"', ".*(0102030405060A11(9000|91\w\w))|(6108).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00A2010402111109"', ".*(0102030405060A11(9000|91\w\w))|(6F00)|(6108).*",timeout=30))

        test.log.info("*************************************************************************************************************")
        test.log.info("5. Test AT+CSIM INCREASE Functionality")
        test.log.info("*************************************************************************************************************")
        #INCREASE  CLA: '8X' or 'CX' or 'EX'    INS: 32
 
        '''
        # Verify the ADM KEY
        test.expect(
            test.dut.at1.send_and_verify('AT+CSIM=26,"F02A000F080000000000000000"', ".*(9000|91\w\w).*", timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A40804047F106F06"', ".*(61\w\w).*", timeout=30))
        # update INCREASE access condition to "ADM1"
        test.expect(test.dut.at1.send_and_verify(
            'AT+CSIM=160,"00DC09044B800103A406830101950108800158A40683010A950108840132A40383010AFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"',
            ".*(9000).*", timeout=30))
        '''
        # select 6F39 as the tested cylic file.
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A40804047F206F39"', ".*(61\w\w).*", timeout=30))
        # Empty all 10 record in 6F39.
        P1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        Value = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        for i in range(10):
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00DC0{}0303{}"'.format(P1[i],'F'*6), ".*(9000|91\w\w).*", timeout=30))
            test.expect(test.dut.at1.send_and_verify('AT+CSIM=10,"00B20{}0403"'.format(P1[i]),'.*(F{6}(9000|91\w\w)).*', timeout=30))

        #Update the 5th record to "1111111", and it becomes record number 1
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=16,"00DC050303{}"'.format('1' * 6), ".*(9000|91\w\w).*",timeout=30))
        test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A2010403{}00"'.format('1'*6), ".*((01(9000|91\w\w))|6101).*",timeout=30))


        for i in range(9):
            test.expect(
                test.dut.at1.send_and_verify('AT+CSIM=16,"8032000003{}"'.format('1' * 6), ".*(61\w\w).*", timeout=30))
            for j in range(i + 2):
                test.expect(test.dut.at1.send_and_verify('AT+CSIM=18,"00A2010403{}00"'.format(Value[j + 1] * 6),
                                                         ".*((0{}(9000|91\w\w))|6101).*".format(P1[i - j + 1]),
                                                         timeout=30))


    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()