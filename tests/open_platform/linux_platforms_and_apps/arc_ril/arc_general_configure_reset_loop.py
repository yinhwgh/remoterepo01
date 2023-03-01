# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103967.001 arc_general_configure_reset_loop.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


'''
Manual steps to reproduce scenarion on the module when application is deployed:

AT^SCFG="MEopMode/CoreDump","0","1","Restart"
AT^SEXIT="exitLoop/getCfg"

GET_RESET_LOOP_INFO

cd /home/cust/testware

./LinuxArcRilResetLoop GetResetLoopInformation
./LinuxArcRilResetLoop ClearResetLoop

/home/cust/testware # ./LinuxArcRilResetLoop GetResetLoopInformation
COM: ARC library Open
COM: threshold: 4
COM: mode: 1
COM: status: 0
COM: counter: 0

./LinuxArcRilResetLoop ConfigureResetLoop t=4 m=1

'''


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
        
        test.log.step('Setting reset loop configuration with custom values')
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ConfigureResetLoop", "t=1", "m=1"],
            expect='Reset loop configured as expected')        
        test.expect('DIF' not in response, critical=True)
        
        test.log.step('Clearing reset loop counter')
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ClearResetLoop"],
            expect='')
        test.expect('DIF' not in response, critical=True)        
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_AtcTunneling", "cmd=AT^SEXIT=2"],
            expect='',
            expect_exit_code=None)         
       
        test.sleep(60)
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetFlightMode"],
            expect='off|on',
            expect_exit_code=None)  
       
        test.log.step('Setting reset loop configuration with zero value')
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop",
            params = ["ConfigureResetLoop", "t=0"],
            expect='Reset loop configured as expected')
       
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetFlightMode"],
            expect='',
            expect_exit_code=None)  
       
       
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
