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
    for lp in range(1000):
        test.log.step(f'***this is {lp+1} loop***')
        test.dut.at1.wait_for(".*RING.*")
        print('>>>>>>>>>>>>>>>>>', test.dut.at1.last_response)
        test.sleep(30)


if "__main__" == __name__:
    unicorn.main()
