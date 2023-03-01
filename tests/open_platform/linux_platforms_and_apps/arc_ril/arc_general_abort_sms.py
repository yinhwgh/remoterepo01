# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# arc_general_abort_sms.py
# TC0104045.001 arc_general_abort_sms.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilAbortSmsCommand')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        
    def run(test):
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='')
        
        if 'ARC_PIN_STATUS_READY' in response:
            test.log.info('PIN is already entered.')
            test.sleep(5)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
            test.sleep(30)
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilAbortSmsCommand",
            params = ["text=Hello", "phone_no={}".format(test.r1.sim.nat_voice_nr), "pin={}".format(test.dut.sim.pin1)],
            expect='cmdCancelled',
            expect_exit_code=0)
       
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()

