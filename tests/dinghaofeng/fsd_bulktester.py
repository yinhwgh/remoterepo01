# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107865.001
import time

import unicorn
from core.basetest import BaseTest
import re


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000079.001
     -- Trakmate_TrackingUnit_SendNotification_NormalFlow
     at1: ASC0 at2: USBM

    '''

    def setup(test):
        pass

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def main_process(test):
    for lp in range(10):
        test.log.step(f'***this is {lp + 1} loop***')
        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(3)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.num_of_modules = 5
        test.check_duts = [False for i in range(test.num_of_modules)]
        test.dut.devboard.send_and_verify("mc:igt=555")
        test.sleep(60)
        test.dut.devboard.wait_for(".*SYSSTART.*")
        sysstart_count = re.findall(".*SYSSTART.*", test.dut.devboard.last_response)
        print('sysstart_count: ', sysstart_count)
        for i in sysstart_count:
            index = int(i[4])
            test.check_duts[index - 1] = True
        for i in range(test.num_of_modules):
            if test.check_duts[i] == True:
                test.log.info("DUT " + str(i + 1) + " lives")
            else:
                test.log.error("DUT " + str(i + 1) + " did not send SYSSTART")


if "__main__" == __name__:
    unicorn.main()
