# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107874.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6.trakmate_send_alert_normal_flow import whole_flow, step_list


class Test(BaseTest):
    '''
     TC0107874.001 - Trakmate_TrackingUnit_SendAlert_EF
     This case mainly test the RQ6000077.001 exceptional flow
     need 2 module with SIM card

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        for i in range(1, 4):
            test.log.info(f'Start check when occur error happen in step{i}')
            whole_flow(test, step_list, fail_step=i)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
