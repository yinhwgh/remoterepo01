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
import re

from core.basetest import BaseTest
#from dstl.init import detect
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    """TcFastRegisterToGsm

    Feature:    BOB-4270
                LM000  // IPIS100293988 COmega: COPS slow under some conditions
    Products:   Bob2xy
    Intention:  test registration time even if module comes from LTE and shall work on GSM now
    End state:  TC ends without PIN1
    Devices:    DUT_MDM

    Facts:
	- IPIS defect shows a long time (approx. 1min) for registration time even if the module is already registered
	  on 4G/LTE and shall search and register now on GSM by (+COPS=0,,,0)
	- by using workaround (+COPS=2/+COPS=0,,,0) the registration is finished within 4 to 5 seconds!
	- -> 1. verify registration for 2G time with automatic mode coming from 4G registration
	  -> 2. verify registration for 2G time with automatic mode after restart/entering PIN
	  -> verify registration for 2G time with automatic mode coming from 3G registration
    - make sure all bands are enabled all the time

	Additional test impacts:
	- registration behaviour is different with 2G or 3G+4G registration (no CREG-URC for 4G registration, but +CEREG instead)


    """

    time1 = 0

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

    def setup(test):
        """Setup method.
        Steps to be executed before test is run.
        Examples:
        """
        #test.dut.detect()
        test.pin1_value = test.dut.sim.pin1

        ## check for LTE-TN SIM, and check/set for correct Provider Config:
        test.imsi = test.dut.sim.imsi
        print("IMSI:", test.imsi) # SIMID: 'LTE 035', IMSI:
        idx = test.imsi.index("26295")
        if idx==0:
            print("IMSI starts with 26295 -- lets check for correct LTE-TN setting")

            # lets check for if 'tn1de' as prov cfg is available:
            bTn1deAvailable = test.dut.at1.send_and_verify('AT^SCFG=?', '^.*SCFG: "MEopMode/Prov/Cfg",.*"tn1de".*SCFG: .*OK.*$', timeout=5)   #, append=True)
            if bTn1deAvailable:
                bDoRestart = False
                # check if AutoSelect is really OFF:
                status = test.dut.at1.send_and_verify('AT^SCFG?', '^.*SCFG: "MEopMode/Prov/AutoSelect","off".*$', timeout=5)   #, append=True)
                if status==False:
                    test.dut.at1.send_and_verify('AT^SCFG=MEopMode/Prov/AutoSelect,"off"', '^.*OK.*$', timeout=7)
                    bDoRestart = True

                test.dut.at1.send_and_verify('AT^SCFG=MEopMode/Prov/Cfg,"tn1de"', '^.*OK.*$')

                if bDoRestart:
                    test.dut.dstl_restart()

        else:
            print("IMSI does not show a LTE-TN-SIM")

        ###
        test.dut.at1.send_and_verify('AT+COPS=0', '^.*OK.*$', timeout=11)

        # check if PIN1 is already entered:
        test.dut.at1.send_and_verify('AT+CPIN?', "^.*OK.*$")
        if "+CPIN: SIM PIN" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('AT+CPIN="{}"'.format(test.pin1_value), "^.*OK.*$")
            test.sleep(3.5)

        # check if CPIN1 lock is active, otherwise set it:
        test.dut.at1.send_and_verify('AT+CLCK="SC",2', "^.*OK.*$")
        if "+CLCK: 0" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('AT+CLCK="SC",1,"{}"'.format(test.pin1_value), "^.*OK.*$")


        test.log.info("\n --- 0. verify module is on 4G/LTE registered --- ")
        test.dut.at1.send_and_verify('AT+CREG=2', "^.*OK.*$")
        #test.dut.at1.send_and_verify('AT+CEREG=2', "^.*OK.*$")

        # do it more times to be sure registration appears meanwhile:
        #test.dut.at1.send_and_verify('AT+CREG?', "^.*OK.*$")
        test.attempt(test.dut.at1.send_and_verify, "AT+CREG?", ".*CREG: 2,1,.*,.*,7.*OK.*", sleep=1, timeout=6, retry=100)

        if '",7' in test.dut.at1.last_response:
            test.log.info("##> module is registered on 4G/LTE, ok")
        else:
            test.log.error("##> module is NOT registered on 4G/LTE, test case needs 4G registration! Please check following settings: ")
            test.dut.at1.send_and_verify('AT+CGDCONT?', "^.*OK.*$")
            test.dut.at1.send_and_verify('AT^SMONI', "^.*OK.*$")
            test.dut.at1.send_and_verify('AT^SCFG?', "^.*OK.*$")

            test.log.error(
                "##> module is NOT registered on 4G/LTE, test case needs 4G registration! -- Aborting setup and skip test run! ")

            # abort because no suite able response found!
            test.expect(False, critical=True)

        pass


    def run(test):
        """Run method.

        Actual test steps.

        Examples:
            #expect test.config.local_config_path parameter is different than None
            test.expect(test.config.local_config_path)
        """

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


    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        test.dut.at1.send_and_verify('AT+COPS=0', "^.*OK.*$", timeout=25)
        test.expect(test.dut.at1.wait_for('.*CREG: [1],".*",".*",[7].*', timeout=95, append=True))
        pass

if "__main__" == __name__:
    unicorn.main()
