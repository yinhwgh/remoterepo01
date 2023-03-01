# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102421.001 arc_hardware_module_time.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.embedded_system.linux.arc_ril_engine import dstl_embedded_linux_arc_ril_engine_enter_pin

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.dut.dstl_embedded_linux_arc_ril_engine_enter_pin()
        
    def run(test):
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_SetModuleTime",
                "year=2000",
                "month=1",
                "day=1",
                "hour=0",
                "minute=0",
                "second=0"
            ],
            expect='EXP')
        test.expect('The new time has been set' in response)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_GetModuleTime"
            ],
            expect='.*2000, 1, 1, 0, 0.*')

        test.sleep(60)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_GetModuleTime"
            ],
            expect='.*2000, 1, 1, 0, 1.*')           
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_SetModuleTime",
                "year=2037",
                "month=12",
                "day=31",
                "hour=23",
                "minute=58",
                "second=59"
            ],
            expect='EXP')
        test.expect('The new time has been set' in response)

        test.sleep(10)    
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_GetModuleTime"
            ],
            expect='.*2037, 12, 31, 23, 59.*')         

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
