# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# arc_general_clear_reset_loop_counter.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_boot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application



class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()

        AT1_STATUS = None
        AT2_STATUS = None
        try:
            AT1_STATUS = test.dut.at1.send_and_verify('at')
        except Exception:
            AT1_STATUS = False
        try:
            AT2_STATUS = test.dut.at2.send_and_verify('at')
        except Exception:
            AT2_STATUS = False
        
        AT_COMMAND1 = 'AT^SCFG="MEopMode/CoreDump","0","1","Restart"'
        AT_COMMAND2 = 'AT^SEXIT="exitLoop/getCfg"'
        if AT1_STATUS:
            test.dut.at1.send_and_verify(AT_COMMAND1)
            test.dut.dstl_restart(interface=test.dut.at1)
            test.dut.at1.send_and_verify(AT_COMMAND2)
        elif AT2_STATUS:
            test.dut.at2.send_and_verify(AT_COMMAND1)
            test.dut.dstl_restart(interface=test.dut.at2)
            test.dut.at2.send_and_verify(AT_COMMAND2)
        else:
            raise RuntimeError('No AT channel available!')

        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilResetLoop')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()


    def run(test):
        
        test.log.step('Checking reset loop configuration')
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["GetResetLoopInformation"],
            expect='')       
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ConfigureResetLoop", "t=4", "m=1"],
            expect='Reset loop configured as expected')       
       
        test.log.step('Clearing reset loop configuration')
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ClearResetLoop"],
            expect='')
        if 'DIF' in response:
            test.fail('Cannot clear reset loop!')       
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["GetResetLoopInformation"],
            expect='counter: 0')
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_AtcTunneling", "cmd=AT^SEXIT=2"],
            expect='',
            expect_exit_code=None)          
       
        test.sleep(30)
        test.expect(test.dut.dstl_embedded_linux_boot(60), critical=True)
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["GetResetLoopInformation"],
            expect='counter: 1')
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ClearResetLoop"],
            expect='')
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["GetResetLoopInformation"],
            expect='counter: 0')
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ConfigureResetLoop", "t=0"],
            expect='Reset loop configured as expected')   
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetFlightMode"],
            expect='off',
            expect_exit_code=None)   
       
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions('external')


if "__main__" == __name__:
    unicorn.main()
