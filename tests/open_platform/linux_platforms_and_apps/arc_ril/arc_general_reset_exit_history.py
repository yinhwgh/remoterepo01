# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103939.001 arc_general_reset_exit_history.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilExitHistory')
        
    def run(test):
        test.log.step("Reset EXIT history")
        test.sleep(50)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_AtcTunneling", "cmd=AT^SEXIT=1"],
            expect='',
            expect_exit_code=None)   
        
        test.sleep(50)
        
        test.dut.devboard.send_and_verify('MC:IGT=200')
        
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilExitHistory",
            params='GetExitHistory',
            expect='exit')

        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilExitHistory",
            params='ResetExitHistory',
            expect='reset')           

        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilExitHistory",
            params='GetExitHistory',
            expect='Error History')
        
        test.expect('Exit history is empty' in response)
        
        
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
