#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0010282.001

import unicorn
import serial
import time
import re
from core.basetest import BaseTest
from random import choice
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.serial_interface import config_baudrate


class  	AtIcf(BaseTest):
    """
        TC0010282.001 - AtIcf
        This procedure tests ICF works correctly with all parameter combinations
        Duration: 51 minutes around
    """

    ICF_RANGE = "\+ICF: \((1,2,3|1-3),5\),\((0,1|0-1)\)"
    ICF_LIST = {
                 "5,1": [serial.SEVENBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE],  # (5,1), 7E1
                 "5,0": [serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE],  # (5,0), 7O1
                 "2,1": [serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE],  # (2,1), 8E1
                 "3": [serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE],  # (3), 8N1, DEFAULT
                 "2,0": [serial.EIGHTBITS, serial.PARITY_ODD, serial.STOPBITS_ONE],  # (2,0), 8O1
                 "1": [serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO]  # (1), 8N2
                }

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.expect(test.dut.at1.send_and_verify("at+icf=?", test.ICF_RANGE))
        # Get current icf stored in user profile
        test.expect(test.dut.at1.send_and_verify("at+icf?", timeout=10))
        current_result = re.search("(ICF:)(.*\d\s)", test.dut.at1.last_response)
        current_icf = ""
        if current_result:
            current_icf = current_result.group(2).strip()
        else:
            test.log.error("Incorrect response of AT+ICF?")
        # Get baund rate values
        ipr_list = test.dut.dstl_get_supported_baudrate_list()
        # Loop for all baund rate
        test.log.info("1. Loop for all icf values with every baud rate")
        for ipr in ipr_list:
            test.log.info("******************* Loop for IPR:" + ipr + " *******************")
            test.dut.at1.send_and_verify("at+ipr={}".format(ipr), "OK", timeout=10)
            test.dut.at1.reconfigure({"baudrate": int(ipr)})
            time.sleep(5)
            test.expect(test.dut.at1.send_and_verify("at+ipr?", "\s+\+IPR: {}".format(ipr), timeout=10))
            # Loop for ICF
            for icf_value in test.ICF_LIST:
                test.log.info("*************** Loop for baud rate: ipr " + ipr + ", icf " + icf_value + " ***************")
                # Set ICF
                test.expect(test.dut.at1.send_and_verify("at+icf={}".format(icf_value), timeout=10))
                # read command should return the value stored in user profile even icf is changed
                test.expect(test.dut.at1.send_and_verify("at+icf?", ".*\+ICF: {}".format(current_icf), timeout=10))
                # save to user profile and restart module to make value take effect
                test.log.info("** save to user profile and restart module to make value take effect **")
                test.dut.at1.send_and_verify("at&w", "OK")
                test.dut.at1.send_and_verify("at+cfun=1,1", "OK")
                test.sleep(0.2)
                test.dut.at1.reconfigure({"baudrate": int(ipr),
                                          "bytesize": test.ICF_LIST[icf_value][0],
                                          "parity": test.ICF_LIST[icf_value][1],
                                          "stopbits": test.ICF_LIST[icf_value][2]})
                test.dut.at1.wait_for("SYSSTART")
                time.sleep(5)
                test.attempt(test.dut.at1.send_and_verify,"at+icf?", f".*\+ICF: {icf_value}",
                             timeout=10, retry=3, sleep=2)
                # when baud rate is slow, need wait more time for information output
                test.expect(test.dut.at1.send_and_verify("at&v", ".*\+ICF: {}".format(icf_value), timeout=10))
                current_icf = icf_value
        # set icf to non-default value
        test.log.info("2. Set icf to non-default value and save in user profile")
        random_icf = '3'
        while random_icf is '3':
            random_icf = choice(list(test.ICF_LIST.keys()))
        test.log.info("Random non-default value is {}".format(random_icf))
        test.expect(test.dut.at1.send_and_verify("at+icf={}".format(random_icf)))
        test.expect(test.dut.at1.send_and_verify("at+icf?", expect="\s*\+ICF: {}\s*".format(current_icf), wait_for="OK"))
        # store non-default icf to user profile
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        # reset to default settings
        test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+icf?", expect="\s*\+ICF: {}\s*".format(random_icf), wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        # restore user profile, ICF value is previous configured one
        test.expect(test.dut.at1.send_and_verify("at+icf?", expect="\s*\+ICF: {}\s*".format('3'), wait_for="OK"))

    def cleanup(test):
        # Reset to default settings
        test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&w", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+ipr=115200", "OK"))
        test.dut.at1.reconfigure({"baudrate": 115200})


if "__main__" == __name__:
    unicorn.main()
