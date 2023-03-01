# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107861.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.auxiliary.check_urc import dstl_check_urc
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6.trakmate_download_config_normal_flow import whole_flow, step_list


class Test(BaseTest):
    '''
     The case is intended to test the exceptional flow according to RQ6000074.001
     -- Trakmate - TrackingUnit - DownLoadConfiguration
     GOAL: To get a-gps file from the ublox web site.

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        whole_flow(test, step_list, fail_step=2)
        whole_flow(test, step_list, fail_step=8)
        whole_flow(test, step_list, fail_step=9)
        whole_flow(test, step_list, fail_step=10)
        whole_flow(test, step_list, fail_step=11)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
