#responsible: fang.liu@thalesgroup.com
#location: Berlin
#TC0092490.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.security.lock_unlock_sim import *

class Test(BaseTest):

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_register_to_network()

    def run(test):

        test.log.step("1. Check the syntax of the AT command \"at^sgapn\".")
        test.log.info("***********************************************************************************************")
        test.dut.at1.send_and_verify("at+cgdcont?", ".*OK.*")
        res = test.dut.at1.last_response
        pattern1 = r'\+CGDCONT: (\d+),("IP"|"IPV4V6"|"IPV6"),".*",.*'

        it = re.finditer(pattern1, res)
        num = 0
        for item in it:
            test.log.info(f"{item.group()}")
            num = num+1

        test.dut.at1.send_and_verify("at^sgapn?", ".*,.*,.*,.*,.*,.*,.*")
        res2 = test.dut.at1.last_response
        pattern2 = r'\^SGAPN: (\d+),(\d+),("IP"|"IPV4V6"|"IPV6"),".*",("GSM"|"WCDMA"|"LTE"|"ANY"),("Enabled"|"Disabled"),(\d+)'

        it2 = re.finditer(pattern2, res2)
        num2 = 0
        for item in it2:
            test.log.info(f"{item.group()}")
            num2 = num2+1

        test.expect(num == num2, critical=True)

        test.log.step("2. Check the command is not pin protected.")
        test.log.info("***********************************************************************************************")

        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("at^sgapn?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^sgapn=?", ".*OK.*"))

        test.log.step("3. Check the test command and the rang of parameter values.")
        test.log.info("***********************************************************************************************")

        test.dut.at1.send_and_verify("at^sgapn=?", ".*OK.*")
        res3 = test.dut.at1.last_response

        test.log.info("The range of PDP context ID is 1-16.")
        test.expect("^SGAPN: (1-16)" in res3)

        test.log.info("The range of APN class is 0-16.")
        test.expect("(0-16)" in res3)

        test.log.info("The type of PDP context should be in the range of (\"IP\",\"PPP\",\"IPV6\",\"IPV4V6\").")
        test.expect("(\"IP\",\"PPP\",\"IPV6\",\"IPV4V6\")" in res3)

        test.log.info("The range of APN bearer is (\"GSM\",\"WCDMA\",\"LTE\",\"ANY\").")
        test.expect("(\"GSM\",\"WCDMA\",\"LTE\",\"ANY\")" in res3)

        test.log.info("The range of inactivity timeout value.")
        test.expect("(0-122820)" in res3)


        test.log.step("4. Check the rules for the classed.")

        pattern3 = r'\^SGAPN: \d+,1,.*'
        res4 = re.search(pattern3, res3, re.I | re.U)

        if not res4:
            test.log.info("APN class range is 0-16, only 1 is not supported.")
            test.expect(True)

        test.log.step("5. Check some illegal values.")
        test.dut.at1.send_and_verify("at^sgapn=1,17", "ERROR")
        test.dut.at1.send_and_verify("at^sgapn=9,0", "ERROR")
        test.dut.at1.send_and_verify("at^sgapn=1,2,\"wsx\"", "ERROR")
        test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",""", "ERROR")
        #The two command will cause module crash.
        #test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",\"123\"", "ERROR")
        #test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",\"abc\"", "ERROR")
        test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",\"ANY\"," "", "ERROR")
        #test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",\"ANY\",\"Disabled\"", "ERROR")

        pattern4 = r'\^SGAPN: 3,.*,"Enabled",0'
        it3 = re.search(pattern4, res2)
        if it3:
            test.log.info("0  Inactivity timer disabled.\n"
                          "If enabled, then for connections without data transfer the connection will be terminated after the timer expires.")

            test.dut.at1.send_and_verify("at^sgapn=3,0,\"IPV4V6\","",\"ANY\",,123", "ERROR")


    def cleanup(test):
        """
        < Test postconditions >
        """
        pass


if "__main__" == __name__:
    unicorn.main()
