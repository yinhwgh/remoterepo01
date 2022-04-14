# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107879.001
import time

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6.trakmate_send_trackingdata_normal_flow import whole_flow, step_list

duration_time = 8 * 60 * 6


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000079.001
     -- Trakmate_TrackingUnit_SendTrackingData_LoadTest_NF

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def main_process(test):
    start_time = time.time()
    test.log.info('Start duration test 8h.')
    while (time.time() - start_time < duration_time):
        whole_flow(test, step_list)
        test.sleep(20)

    test.log.info('Duration test end.')


if "__main__" == __name__:
    unicorn.main()
