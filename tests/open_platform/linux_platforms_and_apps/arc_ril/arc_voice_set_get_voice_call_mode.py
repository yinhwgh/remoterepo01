# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0104236.001 arc_voice_set_get_voice_call_mode.py

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
        
    def run(test):
        test.dut.dstl_embedded_linux_arc_ril_engine_enter_pin()
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_SetVoiceCallMode", 
                      "mode=2"],
            expect='Voice call mode set as expected')
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetVoiceCallMode"],
            expect='Current voice call mode')       
    
        test.expect('voice call mode: 2' in response)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
