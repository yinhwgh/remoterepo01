#responsible: christoph.dehm@thalesgroup.com
#location: Berlin

#!/usr/bin/env unicorn
"""

This file represents Unicorn test template, that should be the base for every new test. Test can be executed with
unicorn.py and test file as parameter, but also can be run as executable script as well. Code defines only what is
necessary while creating new test. Examples of usage can be found in comments. For more details please refer to
basetest.py documentation.

"""

import unicorn
import time
import os
from core.basetest import BaseTest
#from dstl.init import dstl_detect
#from dstl.restart_module import dstl_restart
#import dstl.security.adb_mode
#from dstl.security.lock_unlock_sim import lock_sim
#from dstl.cellular_networks.register_to_network import enter_pin
#

def GetCrashDumpHash(sLines):
    saLines = sLines.splitlines()

    for line in saLines:
        if 'SABR: ' in line:
            break;

    print("GetCrashDumpHashLine: " + line)

    if '"' in line:
        saParts = line.split('"')
        #saParts = saParts[1].split('"')
        m = len(saParts)
        if m>=3:
            return saParts[1]

    print("return with empty string")
    return ""

def GetCrashDumpLen(sLines):
    saLines = sLines.splitlines()

    for line in saLines:
        if 'SABR: ' in line:
            break;

    print("GetCrashDumpLenLine: " + line)

    if ',' in line:
        saParts = line.split(',')
        #saParts = saParts[1].split('"')
        m = len(saParts)
        if m>=2:
            return saParts[1]

    print("return with empty string")
    return ""



class Test(BaseTest):
    """TcCrashDumpDownload

    Feature:    BOB-4271
                LM000
    Products:   Bob2xy
    Intention:  trigger EXIT, check for entry in EXIT history and read out crash dump
    End state:  TC ends without PIN1
    Devices:    DUT_MDM

    Prerequisites:
    - SD-card has to be inserted otherwise 2nd partition is destroyed!

    Facts:
	- check reading out crash dump after EXIT appeared.
	- enable ADB-connection to check for SD-card and to read out crash dump

	-
	-
	Additional test impacts:
	-


    """

    time1 = 0

    def check_error(test):
        print("check for log critical in sub routine:")
        test.expect(False)
        test.log.error("This is an error!")
        return 0


    def check_timing(test, teststep=""):
        if teststep == "":
            teststep = "general time measuring"

        time2 = time.perf_counter()
        #print("T1", time1, "T2", time2, "diff", (time2-time1) )
        duration = time2 - test.time1
        resultmsg = teststep, "was: {:.1f} sec.".format(duration)
        if duration >10:
            resultmsg = resultmsg, "is bigger than 10 sec., see IPIS100293988"
            test.log.critical(resultmsg)
            return -1
        else:
            resultmsg = resultmsg, "is lower than 10 sec. as expected."
            test.log.info(resultmsg)
        return 0


    def GetNextSabrDataIntoFile(test, offset, size, fout):

        #sAtCmd = 'AT^SABR=coredump,read,' + offset + ',' + size
        sAtCmd = 'AT^SABR=coredump,read,{:d},{:d}'.format(offset, size)

        #line = '{:10d} {:s}'.format(size, file)
        #print(f"Bearbeitung : {dauer:.4} in Sekunden.\n")


        #test.dut.at1.send(message=sAtCmd, wait_after_send=0.0, timeout=0, end="\r")
        test.dut.at1.send_and_verify(sAtCmd, "^.*OK.*$", wait_for="OK") #, append=True)
        #time.sleep(5)
        #data = test.dut.at1.read()
        data = test.dut.at1.last_response
        test.dut.at1._flush()
        if '\r' in data:
            dataLines = data.split('\n')
        else:
            print('######> attention, no CrLf found!')
            print(data)
            return

        print('num of lines:', len(dataLines) )

        i=1
        for line in dataLines:
            print(f'Zeile {i}: {line}')
            i+=1

        if len(dataLines) >=2:
            lineStartMarker = '^SABR: {:d},{:d},'.format(offset, size)
            if dataLines[1].startswith(lineStartMarker):

                print("##> startmarker found with len:", len(lineStartMarker))
                iStart = len(lineStartMarker)
                iEnd = len(dataLines)
                rawLine = dataLines[1][iStart:]
                rawLine = rawLine.replace('\\00', chr(0x00) )
                rawLine = rawLine.replace('\\0D', chr(0x0D))    # Cr
                rawLine = rawLine.replace('\\0A', chr(0x0A))    # Lf
                rawLine = rawLine.replace('\\5C', chr(0x5C))    # backSlash
                newRawLine = rawLine.replace('\\E6', chr(0xE6))    # dez 230

            fout.write(newRawLine)

        return

    def setup(test):
        """Setup method.
        Steps to be executed before test is run.
        Examples:
        """


        test.log.info(" --- DSTL_DETECT() --- ")
        #test.dut.dstl_detect()

        test.log.info(" --- DSTL_ENTER_PIN() --- ")
        #test.dut.enter_pin()
        test.log.info(" --- DSTL_LOCK_SIM() --- ")
        #test.dut.dstl_lock_sim()

        test.pin1_value = test.dut.sim.pin1



        '''
        filePath = logPath + '\meineausgabe.txt'
        print("filePath:", filePath)
        fout = open(filePath, "w")
        fout.write(filePath)
        fout.close()
        '''



        """
        # check if PIN1 is already entered:
        test.dut.at1.send_and_verify('AT+CPIN?', "^.*OK.*$")
        if "+CPIN: SIM PIN" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('AT+CPIN="{}"'.format(test.pin1_value), "^.*OK.*$")
            test.sleep(3.5)

        " ""
        # check if CPIN1 lock is active, otherwise set it:
        test.dut.at1.send_and_verify('AT+CLCK="SC",2', "^.*OK.*$")
        if "+CLCK: 0" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('AT+CLCK="SC",1,"{}"'.format(test.pin1_value), "^.*OK.*$")


        test.log.info("\n --- 0. verify module is on 4G/LTE registered --- ")
        test.dut.at1.send_and_verify('AT+CREG=2', "^.*OK.*$")
        #test.dut.at1.send_and_verify('AT+CEREG=2', "^.*OK.*$")
        test.dut.at1.send_and_verify('AT+CREG?', "^.*OK.*$")
        if '",7' in test.dut.at1.last_response:
            test.log.info("##> module is registered on 4G/LTE, ok")
        else:
            test.log.info("##> module is NOT registered on 4G/LTE, test case needs 4G registration! Please check following settings: ")
            test.dut.at1.send_and_verify('AT+CGDCONT?', "^.*OK.*$")
            test.dut.at1.send_and_verify('AT^SMONI', "^.*OK.*$")
            test.dut.at1.send_and_verify('AT^SCFG?', "^.*OK.*$")

            # abort because no suite able response found!
            test.expect(False, critical=True)

        pass
        """

    def run(test):
        """Run method.

        Actual test steps.

        Examples:
            #expect test.config.local_config_path parameter is different than None
            test.expect(test.config.local_config_path)
        """

       # test.expect(True)                   # main should set at least one expect() flag
                                            # then the main finishes with exit return value '0' if all passed
                                            # or with '-100' if one or more are set to expect(False)
                                            # in case no .expect() is performed then exit return value is '-200'
        #test.expect(False)
        #test.check_error()

        #sprint("check for log results in main:")
        #test.log.critical("This is a error!")   # this is only for the log file and does not increment the error counter
                                                # and has no influence to the exit return value !



        test.log.info("\n --- 1. check if CoreDump is stored on other partition ---")
        result = test.dut.at1.send_and_verify('at^SABR="CoreDump","info"', "OK" )
        response = test.dut.at1.last_response
        cdHash = GetCrashDumpHash(response)
        cdLen  = GetCrashDumpLen(response)
        print(' Len:', cdLen)

        if cdHash != "":
            print(' Hash found:', cdHash)

        if cdLen.isnumeric():
            print(' numeric Len found:', cdLen)
        else:
            print(' alphan. Len found:', cdLen)


        test.log.info("\n --- 2. read out CoreDump with SABR command: ---")

        logPath =  test.workspace
        print("logPath:", logPath)
        filePath = logPath + '\SabrOutput.bin'
        fout = open(filePath, "w")

        test.GetNextSabrDataIntoFile(  0, 256, fout)
        test.GetNextSabrDataIntoFile(256, 256, fout)
        test.GetNextSabrDataIntoFile(512, 256, fout)

        #test.dut.at1.send(message='AT^SABR=coredump,read,0,256', wait_after_send=0.0, timeout=0, end="\r")
        #test.dut.at1.send(message='at^sbnr="nv",5038,128', wait_after_send=0.0, timeout=0, end="\r")
        #test.dut.at1.send_and_verify('AT^SCFG=?', "^.*OK.*$", timeout=25, append=True)
        #time.sleep(5)
        #response = test.dut.at1.last_response
        #data = test.dut.at1.read()
        #fout.write(data)



        #test.dut.at1.send(message='AT^SABR=coredump,read,256,256', wait_after_send=0.0, timeout=0, end="\r")
        #test.dut.at1.send(message='at^sbnr="nv",5038,128', wait_after_send=0.0, timeout=0, end="\r")
        #test.dut.at1.send_and_verify('AT^SCFG=?', "^.*OK.*$", timeout=25, append=True)


        #response = test.dut.at1.last_response
        #data = test.dut.at1.read()
        #fout.write(data)


        fout.close()

        print("response:", response)




        #test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[03].*', timeout=95, append=True))

        print("ausgabe in datei fertig!")



        """
        test.log.info("\n --- 1. enable ADB mode ---")
        test.dut.dstl_adb_enable()



        test.log.info("\n --- 2. disable ADB mode ---")
        test.dut.dstl_adb_disable()
        time.sleep(25)



        " ""
        #test.log.info("\n --- 1. registering on 2G, coming from 4G ---")
        #test.log.critical("main only with test.log.critical, what is the result code ?")

        test.log.info("\n --- 1. registering on 2G, coming from 4G ---")

        test.time1 = time.perf_counter()
        test.dut.at1.send_and_verify('AT+COPS=0,,,0', "^.*OK.*$", timeout=25, append=True)
        test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[03].*', timeout=95, append=True))
        ret = test.check_timing("1. registration time from 4G to 2G")
        if (ret<0):
            test.expect(test.dut.at1.send_and_verify('AT+INFO: WA: for throwing a negative exit code! - IPIS100302701'))

        test.log.info("\n --- 2. registering on 2G, coming from airplane mode ---")

        test.dut.at1.send_and_verify('AT+CFUN=4')
        test.sleep(5)
        test.dut.at1.send_and_verify('AT+CFUN=1')
        test.time1 = time.perf_counter()
        test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[03].*', timeout=95, append=True))
        ret = test.check_timing("2. registration time from airplane mode to 2G")
        if (ret < 0):
            test.expect(test.dut.at1.send_and_verify('AT+INFO: WA: for throwing a negative exit code! - IPIS100302701'))

        test.log.info("\n --- 3. registering on 2G, coming from 3G ---")

        status = test.dut.at1.send_and_verify('AT+COPS=0,,,2', "^.*OK.*$", timeout=85, append=True)
        if status!=0:
            test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[6].*', timeout=95, append=True))
            test.sleep(5)
            test.time1 = time.perf_counter()
            test.dut.at1.send_and_verify('AT+COPS=0,,,0', "^.*OK.*$", timeout=25, append=True)
            test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[03].*', timeout=35, append=True))
            ret = test.check_timing("3. registration time from 4G to 2G")
            if (ret < 0):
                test.expect(test.dut.at1.send_and_verify('AT+INFO: WA: for throwing a negative exit code! - IPIS100302701'))

        else:
            test.log.error(" something went wrong to register at 3G in step 3.")

        pass
        """

    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        #test.dut.at1.send_and_verify('AT+COPS=0', "^.*OK.*$", timeout=25)
        #test.sleep(5)
        pass

if "__main__" == __name__:
    unicorn.main()
