# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107878.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.auxiliary.check_urc import dstl_check_urc
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6.trakmate_send_trackingdata_normal_flow import whole_flow, step_list


class Test(BaseTest):
    '''
    This case mainly test the RQ6000079.001 exceptional flow
    Trakmate_TrackingUnit_SendTrackingData_MQTT_EF03

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        whole_flow(test, step_list, fail_step=30)
        # whole_flow(test, step_list, fail_step=32)
        whole_flow(test, step_list, fail_step=33)
        whole_flow(test, step_list, fail_step=34)
        whole_flow(test, step_list, fail_step=35)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
