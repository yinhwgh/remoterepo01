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
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart


#^SCFG: "Radio/Band/2G",("00000001-0000000f"),,("0","1")
#^SCFG: "Radio/Band/TdScdma",("00000001-00000021"),,("0","1")
def GetMaxBandSetting1(sScfgLine):
    print("GetMaxBandS1: " + sScfgLine)
    if "," in sScfgLine:
        saParts = sScfgLine.split("-")
        saParts = saParts[1].split('"')
        m = len(saParts)
        return saParts[0]

    print("return with empty string")
    return ""

#^SCFG: "Radio/Band/4G",("00000001-8a0e00d5"),("00000002-000001e2"),("0","1")
def GetMaxBandSetting2(sScfgLine):
    print("GetMaxBandS2: " + sScfgLine)
    if "," in sScfgLine:
        saParts = sScfgLine.split(",")
        saParts = saParts[2].split("-")
        saParts = saParts[1].split('"')
        m = len(saParts)
        return saParts[0]

    return None


class Test(BaseTest):
    """TcScfgRadioBandRbe

    Feature:    BOB-3405 / CR01934
                LM0002647.014: Multi Band/ RAT Selection for Modules Supporting 2G, 3G and 4G RAT
    Products:   Bob210: ALAS5-W_210, Bob300: PLPS9-*
    Intention:  test parameter <rbe> of AT^Scfg sub cmds Radio/Band/2G, /3G, 4G and TDSCDMA only
    End state:  TC ends with SetMaxRadioBandValues() and Restart() of module without PIN1
    Devices:    DUT_MDM

    Facts:
	- verify that the correct product is supporting it, each other should not be tested or a negative test should be performed
	- AT-cmd works without and with PIN
	- each RAT can be set to 0, at least one band of all should stay active
	    -> if all bands shall be disabled by <rbaXY> then a CME ERROR should appear
	- in case <rbe>=0: new band setting is active after next restart
	- in case <rbe>=1: new band setting is active at once: module should deregister and perform a new full scan of all network bands
	- 				   new band setting is also active for next restart

	Additional test impacts:
	- registration behaviour is different with 4G or 2G+3G registration (no CREG-URC for 4G registration)
	  -> pay attention to be registered at least one time on 2G or 3G to see +CREG:2 after rbe=1 setting


    """

    bBand2G = False
    bBand3G = False
    bBand4G1 = False
    bBand4G2 = False
    bBandTds = False

    sMaxBand2G = ""
    sMaxBand3G = ""
    sMaxBand4G1 = ""
    sMaxBand4G2 = ""
    sMaxBandTds = ""

    def SetMaxRadioBandValues(test):
        """
        set all maximum values of Radio/Band/xy stored in global variable test.sMaxBandxy
        preform a module restart to take effect
        show SCFG? output of new values
        :return: none
        """
        test.log.info("\n --- set back to factory default: ----")
        if test.bBand2G:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG="+ "Radio/Band/2G," + test.sMaxBand2G + ",,0", "^.*OK.*$"))
        if test.bBand3G:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG="+ "Radio/Band/3G," + test.sMaxBand3G + ",,0", "^.*OK.*$"))

        if test.bBand4G2:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG="+ "Radio/Band/4G," + test.sMaxBand4G1 + "," + test.sMaxBand4G2 + ",0"
                                                    , "^.*OK.*$"))
        elif test.bBand4G1:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/4G," + test.sMaxBand4G1  + ",0", "^.*OK.*$"))

        if test.bBandTds:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG="+ "Radio/Band/Tdscdma," + test.sMaxBandTds + ",,0", "^.*OK.*$"))

        # perform full restart to take effect - maybe <rbe> did not work before!
        test.dut.dstl_restart()
        # check setting after restart:
        test.dut.at1.send_and_verify("AT^SCFG?", "^.*OK.*$")
        return


    def setup(test):
        """Setup method.
        - extract default Radio/Band values from ^SCFG=?
        """
        test.pin1_value = test.dut.sim.pin1


        # extract default Radio/Band values from ^SCFG=?
        status = test.dut.at1.send_and_verify("AT^SCFG=?", "^.*OK.*$")
        response = test.dut.at1.last_response
        if "Radio/Band" in response:
            responselines = test.dut.at1.last_response.splitlines()
            m = len(responselines)
            test.log.info("Anzahl Teile: ")
            test.log.info(m)


            # find line and detect highest value as of:
            # ^SCFG: "Radio/Band/2G",("00000001-0000000f"),,("0","1")

            sMaxBand2G = GetMaxBandSetting1("Hallo")

            test.log.info("Check ?")
            test.log.info("NoneReturn is:_" + sMaxBand2G + "_")

            for a in responselines:
                if "Radio/Band/2G" in a:
                    test.sMaxBand2G = GetMaxBandSetting1(a)
                    if test.sMaxBand2G != "":
                        test.bBand2G = True

                elif "Radio/Band/3G" in a:
                    test.sMaxBand3G = GetMaxBandSetting1(a)
                    if test.sMaxBand3G != "":
                        test.bBand3G = True

                elif "Radio/Band/4G" in a:
                    test.sMaxBand4G1 = GetMaxBandSetting1(a)
                    if test.sMaxBand4G1 != "":
                        test.bBand4G1 = True
                    test.sMaxBand4G2 = GetMaxBandSetting2(a)
                    if test.sMaxBand4G2 != "":
                        test.bBand4G2 = True

                elif "Radio/Band/TdScdma" in a:
                    test.sMaxBandTds = GetMaxBandSetting1(a)
                    if test.sMaxBandTds != "":
                        test.bBandTds = True

            test.log.info("max 2G: " + test.sMaxBand2G)
            test.log.info("max 3G: " + test.sMaxBand3G)
            test.log.info("max 4G1: " + test.sMaxBand4G1)
            test.log.info("max 4G2: " + test.sMaxBand4G2)
            test.log.info("max Tds: " + test.sMaxBandTds)

        else:
            # abort because no suite able response found!
            test.log.error(
                "##> SETUP has failed, test run skipped.")
            test.expect(False, critical=True)


    def run(test):
        """Run method.
        1. do some illegal cmds
        2. set all settings to 0 with rbe=0, last one should show an CME ERROR:
            2.1 check setting after setting all to ZERO with reb=0
            2.2 check scfg setting after restart and try to register
        3. enable all bands with RBE=1 step by step
            3.1 check for each if module triggers a network scan
        9. clean up ... set all maximum rba values back and restart (see cleanUp)
        """

        testSection = "\n --- 1. do some illegal cmds --- "
        test.log.info(testSection)
        test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/2G" + ",0" + ",",  "^.*CME ERROR:.*$")
        test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G" + ",1" + ",,", "^.*CME ERROR:.*$")
        test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/2G" + ",1" + ",,a", "^.*CME ERROR:.*$")
        test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G" + ",,,0", "^.*CME ERROR:.*$")

        testSection = "\n --- 2. set all settings to 0 with rbe=0, last one should show an CME ERROR: --- "
        test.log.info(testSection)
        # check setting before setting all to ZERO:
        test.dut.at1.send_and_verify("AT^SCFG?", "^.*OK.*$")

        if test.bBandTds==True:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG="+ "Radio/Band/Tdscdma," + "0,,0"
                                                     , "^.*OK.*$"))
        else:
            print(" ###  ELSE TDSCDMA ####")

        if test.bBand4G2==True:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/4G," + "0,0,0", "^.*OK.*$"))
        elif test.bBand4G1:  # only in case a module does not support 4G2 parameter:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/4G," + "0,0", "^.*OK.*$"))
        else:
            print(" ###  ELSE 4g1+2 ####")

        if test.bBand3G==True:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G," + "0,,0", "^.*OK.*$"))
        else:
            print(" ###  ELSE 3G ####")

        if test.bBand2G==True:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/2G," + "0,,1", "^.*CME ERROR.*$"))
        else:
            print(" ###  ELSE 2G ####")


        testSection = "\n --- 2.1 check setting after setting all to ZERO with reb=0"
        test.log.info(testSection)

        test.dut.at1.send_and_verify("AT^SCFG?", "^.*OK.*$")

        # all bands are zero now without <rbe>  (rbe==0)
        # so we check module behave after restart: will it register to any net ?
        testSection = "\n --- 2.2 check scfg setting after restart and try to register --- "
        test.log.info(testSection)
        test.dut.dstl_restart()

        # pin1_value
        print("AT+CPIN= ", test.pin1_value)
        test.dut.at1.send_and_verify('at+cpin={};+CREG=2'.format(test.pin1_value), "^.*OK.*$")
        test.expect(test.dut.at1.wait_for("+CREG: [02]", timeout=25))
#        time.sleep(25)

        test.expect(test.dut.at1.send_and_verify('AT+CREG?', "^.*\\+CREG: 2,4.*OK.*$"))
        test.dut.at1.send_and_verify('AT^MONI', "^.*OK.*$")


        testSection = "\n --- 3. enable all bands with RBE=1 step by step --- "
        test.log.info(testSection)

        bWorkaround = False

        testSection = " === 3.1) enable all bands with RBE=1, step by step manually ==="
        test.log.info(testSection)

        if test.bBand2G:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/2G," + test.sMaxBand2G + ",,1", "^.*OK.*$"))
            response = test.dut.at1.last_response
            test.expect(test.dut.at1.wait_for("+CREG: [02]", timeout=5))
            if '+CME ERROR: 767' in response or '+CME ERROR: operation failed' in response:
                test.log.error("\n ==> see IPIS100299901, Bob200, do a work around now: ")
                test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/2G," + test.sMaxBand2G + ",,0", "^.*OK.*$"))
                bWorkaround = True

        if test.bBand3G:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G," + test.sMaxBand3G + ",,1", "^.*OK.*$"))
            response = test.dut.at1.last_response
            test.expect(test.dut.at1.wait_for("+CREG: [02]", timeout=5))
            if '+CME ERROR: 767' in response or '+CME ERROR: operation failed' in response:
                test.log.error("\n ==> see IPIS100299901, Bob200, do a work around now: ")
                test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G," + test.sMaxBand3G + ",,0", "^.*OK.*$"))
                bWorkaround = True

        if test.bBand4G2:
            test.expect(
                test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/4G," + test.sMaxBand4G1 + "," + test.sMaxBand4G2 + ",1"
                                             , "^.*OK.*$"))
            response = test.dut.at1.last_response
            if '+CME ERROR: 767' in response or '+CME ERROR: operation failed' in response:
                test.log.error("\n ==> see IPIS100299901, Bob200, do a work around now: ")
                test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G," + test.sMaxBand3G + ",,0", "^.*OK.*$"))
                bWorkaround = True

        elif test.bBand4G1:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/4G," + test.sMaxBand4G1 + ",1", "^.*OK.*$"))
            response = test.dut.at1.last_response
            if '+CME ERROR: 767' in response or '+CME ERROR: operation failed' in response:
                test.log.error("\n ==> see IPIS100299901, Bob200, do a work around now: ")
                test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/3G," + test.sMaxBand3G + ",,0", "^.*OK.*$"))
                bWorkaround = True

#       4G does not trigger +CREG URC, therefore use CEREG!
#        if (test.bBand4G2 or test.bBand4G1):
#            test.expect(test.dut.at1.wait_for("+CREG: [02]", timeout=5))


        if test.bBandTds:
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/Tdscdma," + test.sMaxBandTds + ",,1", "^.*OK.*$"))
            response = test.dut.at1.last_response
            test.expect(test.dut.at1.wait_for("+CREG: [02]", timeout=5))
            if '+CME ERROR: 767' in response or '+CME ERROR: operation failed' in response:
                test.log.error("\n ==> see IPIS100299901, Bob200, do a work around now: ")
                test.expect(test.dut.at1.send_and_verify("AT^SCFG=" + "Radio/Band/Tdscdma," + test.sMaxBandTds + ",,0", "^.*OK.*$"))
                bWorkaround = True

        if bWorkaround:
            # perform a restart to make effect new setting by Workaround!
            test.dut.dstl_restart()
            test.dut.at1.send_and_verify('at+cpin={};+CREG=2'.format(test.pin1_value), "^.*OK.*$")

        # module should have found a valid network to register on, also in case of WA above!
        status = test.expect(test.dut.at1.wait_for("+CREG: 1", timeout=25))
        if status == False:
            test.log.error(
                "##> module is NOT registered, test case needs a network registration!")
        test.dut.at1.send_and_verify('AT^MONI', "^.*OK.*$")


#        print("AT+CPIN= ", test.pin1_value)
#        test.dut.at1.send_and_verify('at+cpin={};+CREG=2'.format(test.pin1_value), "^.*OK.*$")
#        test.dut.at1.wait_for("+CREG: 1", timeout=24)

        time.sleep(5)


        testSection = " --- 9. clean up ... without leading \\n ----"
        test.log.info(testSection)
        test.dut.at1.send_and_verify("ATi", "^.*OK.*$")
        pass


    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        test.SetMaxRadioBandValues()    # please not: restart, but no PIN entering!
        test.dut.dstl_restart()
        pass

if "__main__" == __name__:
    unicorn.main()
