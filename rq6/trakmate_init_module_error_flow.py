# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107872.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from tests.rq6 import trakmate_init_module_normal_flow as uc_init


class Test(BaseTest):
    '''
     TC0107872.001 - Trakmate_TrackingUnit_InitModule_EF
     This case mainly test the RQ6000076.001 exceptional flow

    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        for i in range(1, 36):
            test.log.info(f'Start check when occur error happen in step{i}')
            uc_init.whole_flow(test, uc_init.step_list, fail_step=i)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
