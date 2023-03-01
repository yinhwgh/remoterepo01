#responsible: shiming.ren@thalesgroup.com
#location: Dalian
#TC0091758.001

#!/usr/bin/env unicorn
"""

This file represents Unicorn test template, that should be the base for every new test. Test can be executed with
unicorn.py and test file as parameter, but also can be run as executable script as well. Code defines only what is
necessary while creating new test. Examples of usage can be found in comments. For more details please refer to
basetest.py documentation.

"""
# To Run this script, please install pyvisa, R&S Visa, and connect CMW500 to your PC, it should test offline
import unicorn
import time
import pyvisa
from core.basetest import BaseTest


class Test(BaseTest):
    """TC0091758.001 - TpIndPsinfo

    Feature:
    Products:   Viper: ELS82/ELS62
    Intention:
    End state:
    Devices:    DUT_ASC0, CMW500

    Facts:
          0  GPRS/EGPRS not available in currently used cell
          1  GPRS available in currently used cell
          2  GPRS attached
          3  EGPRS available in currently used cell
          4  EGPRS attached
          5  camped on WCDMA cell
          6  WCDMA PS attached
          7  camped on HSDPA-capable cell
          8  PS attached in HSDPA capable cell
          9 camped on HSDPA/HSUPA-capable cell
          10 PS attached in HSDPA/HSUPA-capable cell
          16 camped on EUTRAN capable cell
          17 attached in EUTRAN capable cell
    """


    def setup(test):
        """
            Setup method.
        """
        # Restart to make pin locked

        test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*")
        rm = pyvisa.ResourceManager()
        visaResource = rm.list_resources()
        test.log.info("instrument list: {}".format(visaResource))
        for device in visaResource:
            if "USB" in device:
                test.cmw500 = rm.open_resource('USB0::0x0AAD::0x0057::0168357::INSTR')
                break

        test.log.info("CMW500 infor: {}".format(test.cmw500.query("*IDN?")))
        test.log.info("Reset CMW500 to default value: {}".format(test.cmw500.write("SYSTem:RESet:ALL")))
        test.sleep(10)
        test.log.info("CMW500 2G(GSM) cell state: {}".format(test.cmw500.query("SOURce:GSM:SIGN:CELL:STATe:ALL?")))
        test.log.info("CMW500 3G(WCDMA) cell state: {}".format(test.cmw500.query("SOURce:WCDMa:SIGN:CELL:STATe:ALL?")))
        test.log.info("CMW500 4G(FD-LTE) cell state: {}".format(test.cmw500.query("SOURce:LTE:SIGN:CELL:STATe:ALL?")))

        test.sleep(1)

    def run(test):
        """Run method.
        #1, enable the "psinfo" indicatior
        #2, Check the Device support RAT
        #3, Cycle: Change the CMW500 settings and cell on
        #4,         Make the module register on the CMW500
        #5,         Wait for the SIND URC
        #6,         Check the status of indicator "psinfo" with "^SIND" command.
        #7, Reset the CMW500
        #8, Reset the module
        """
        # 1, enable the "psinfo" indicatior
        test.log.step('enable the "psinfo" indicatior')
        test.expect(test.dut.at1.send_and_verify("at^sind?", "OK", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at^sind=\"psinfo\",1", "OK", wait_for="OK"))
        #2 force new network registration
        test.log.info("Disable GSM signaling PS Domain:{}".format(test.cmw500.write("CONFigure:GSM:SIGN:CELL:PSDomain OFF")))


        test.log.step("1. Test GSM Network psinfo indicator")
        # Open GSM signaling on CMW500
        test.log.info("Open GSM signaling on CMW500: {}".format(test.cmw500.write("SOURce:GSM:SIGN:CELL:STATe ON")))
        while "ON,ADJ" not in test.cmw500.query("SOURce:GSM:SIGN:CELL:STATe:ALL?"):
            test.sleep(1)
            test.log.info("check GSM signaling status once per second")
        test.log.info("GSM signaling status is: {}".format(test.cmw500.query("SOURce:GSM:SIGN:CELL:STATe:ALL?")))

        # Make the module register on the CMW500
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+creg=2", "OK", wait_for="OK"))
        if test.dut.at1.send_and_verify("at+cpin?", "SIM PIN", wait_for="OK"):
            test.expect(test.dut.at1.send_and_verify("at+cpin=\"1234\"", "OK", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+CPIN?", "READY", wait_for="OK"))
        test.expect(test.dut.at1.wait_for("\+CREG: 1", timeout=120))
        test.sleep(5)
        # check the 'psinfo' indicator status
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,0", wait_for="OK"))
        test.sleep(5)


        test.log.step("2. Test GPRS Network psinfo indicator")
        #deactive the module from CMW500 signaling
        test.expect(test.dut.at1.send_and_verify("at+cops=2", "OK", wait_for="OK",timeout = 30))
        test.sleep(5)
        #change the CMW500 settings to GPRS supported
        test.log.info("Off GSM signaling on CMW500: {}".format(test.cmw500.write("SOURce:GSM:SIGN:CELL:STATe OFF")))
        test.log.info(
            "Enable GSM signaling PS Domain:{}".format(test.cmw500.write("CONFigure:GSM:SIGN:CELL:PSDomain ON")))
        test.log.info(
            "Change the Network support to GPRS:{}".format(test.cmw500.write("CONFigure:GSM:SIGN:CELL:NSUPport GPRS")))
        test.log.info("Open GSM signaling on CMW500: {}".format(test.cmw500.write("SOURce:GSM:SIGN:CELL:STATe ON")))
        #make the module register on CMW500
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cops=0", "OK", wait_for="OK", timeout = 60))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,2", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=0", "OK", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt?", "CGATT:\s?0", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,1", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=1", "OK", wait_for="OK",timeout = 60))
        test.expect(test.dut.at1.send_and_verify("at+cgatt?", "CGATT:\s?1", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,2", wait_for="OK"))

        test.log.step("3. Test EGPRS Network psinfo indicator")
        #deactive the module from CMW500 signaling
        test.expect(test.dut.at1.send_and_verify("at+cops=2", "OK", wait_for="OK"))
        test.sleep(5)
        #change the CMW500 settings to EGPRS supported
        test.log.info("Off GSM signaling on CMW500: {}".format(test.cmw500.write("SOURce:GSM:SIGN:CELL:STATe OFF")))
        test.log.info(
            "Change the Network support to GPRS:{}".format(test.cmw500.write("CONFigure:GSM:SIGN:CELL:NSUPport EGPRS")))
        test.log.info("Open GSM signaling on CMW500: {}".format(test.cmw500.write("SOURce:GSM:SIGN:CELL:STATe ON")))
        #make the module register on CMW500
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cops=0", "OK", wait_for="OK", timeout=60))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,4", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=0", "OK", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt?", "CGATT:\s?0", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,3", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=1", "OK", wait_for="OK",timeout = 60))
        test.expect(test.dut.at1.send_and_verify("at+cgatt?", "CGATT:\s?1", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "^SIND: psinfo,1,4", wait_for="OK"))



    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
         # please not: restart, but no PIN entering!
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,1", "OK", wait_for="OK", timeout=60))
        test.log.info("Reset CMW500 to default value: {}".format(test.cmw500.write("SYSTem:RESet:ALL")))

if "__main__" == __name__:
    unicorn.main()
