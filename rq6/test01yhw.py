# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107865.001
import time

import unicorn
from core.basetest import BaseTest


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
    print(test.update_sw_url)
    print(f'at^snfota="url","{test.update_sw_url}"')
    print(f'at^snfota="CRC","{test.update_sw_crc}"')


if "__main__" == __name__:
    unicorn.main()
