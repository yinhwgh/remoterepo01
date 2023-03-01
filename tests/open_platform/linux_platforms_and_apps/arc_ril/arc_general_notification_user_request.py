# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103823.001 arc_general_notification_user_request.py



import unicorn
from core.basetest import BaseTest

import re

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_ignite_module
from dstl.auxiliary.devboard.devboard import dstl_get_dev_board_version
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilNotifyShutdown')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        
    def run(test):
        
        test.expect(test.dut.devboard, critical=True)
        test.dut.dstl_get_dev_board_version()
        
        srun_lock_code = re.sub('\D', '', test.dut.software)
        test.log.info("SRUN lock code: {}".format(srun_lock_code))
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_AtcTunneling", "cmd=AT^SRUN=\"Fact/SC/Lock\",\"U\",{}".format(srun_lock_code)],
            expect='',
            expect_exit_code=None)   
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilNotifyShutdown",
            params = ["s=3"],
            expect='as expected')
        
        test.sleep(80)
        
        test.dut.dstl_ignite_module()
       
       
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
