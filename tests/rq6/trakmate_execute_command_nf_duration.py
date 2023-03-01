# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107842.001
import time

import re
import random
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.configuration import scfg_urc_ringline_config
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms import configure_sms_text_mode_parameters
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6 import trakmate_execute_command_nf as execute_cmd


duration_time=7*24*60*60

class Test(BaseTest):
    '''
    TC0107842.001 - 	Trakmate_TrackingUnit_ExecuteCommand_NormalFlow_DurationTest
    Subscriber: 2
    Duration : 1 week
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r1.dstl_configure_sms_event_reporting("2","1")
        uc_init.whole_flow(test, uc_init.step_list)
        test.dut.dstl_activate_urc_ringline_to_local()
        test.dut.dstl_set_urc_ringline_active_time('2')
        test.expect(test.dut.at1.send_and_verify('AT^SPOW=2,1000,3'))

    def run(test):
        start_time=time.time()
        while(time.time()-start_time<duration_time):
            for i in range(3):
                execute_cmd.cmd_flow(test,i)
                time.sleep(60*60)


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT^SPOW=1,0,0'))



if "__main__" == __name__:
    unicorn.main()
