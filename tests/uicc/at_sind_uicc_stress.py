#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0092876.001 - StressQueryUICCeUICCID

"""
This test case is to check stress testing of reading UICC/eUICC ID by SIND command.

"""


import unicorn
import time
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(2)

    def run(test):
        test.log.info('**** TpAtSindUiccid - Start ****')

        test.log.info('**** 1. Enable ICCID & EUICCID ****')
        test.expect(test.dut.at1.send_and_verify("AT^SIND=iccid,1", "\^SIND: iccid,1.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=euiccid,1", "\^SIND: euiccid,1.*OK.*"))

        test.log.info('**** 2. Plug out/in SIM card and check URC for 5000 times ****')
        b_flag = 0
        n = 5000
        for i in range(1, n + 1):
            test.dut.dstl_remove_sim()
            test.log.info('**** Waiting for "iccid" URC ****')
            if not test.expect("+CIEV: iccid,\"\"" in test.dut.at1.last_response):
                b_flag = 1
            test.log.info('**** Waiting for "euiccid" URC ****')
            if not test.expect("+CIEV: euiccid,\"\"" in test.dut.at1.last_response):
                b_flag = 1
            time.sleep(2)
            test.dut.dstl_insert_sim()
            iccid_urc = "\+CIEV: iccid,\"(\w{16,20})\""
            euiccid_urc = "\+CIEV: euiccid,\"(\w{32})\""
            test.log.info('**** Waiting for "iccid" URC ****')
            if not test.expect(re.search(iccid_urc, test.dut.at1.last_response)):
                b_flag = 1
            test.log.info('**** Waiting for "euiccid" URC ****')
            if not test.expect(re.search(euiccid_urc, test.dut.at1.last_response)):
                b_flag = 1
            #test.log.info(test.dut.at1.last_response)
            if b_flag:
                test.log.info('*** Loops Break in {} times'.format(i))
                break

        test.log.info('**** Test end ***')


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK*."))





if (__name__ == "__main__"):
    unicorn.main()
