# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102356.001 arc_pin_lock_state_pin_status_const.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        

    def run(test):
        PIN1 = test.dut.sim.pin1 if test.dut.sim.pin1 else '9999'
        PUK1 = test.dut.sim.puk1 if test.dut.sim.puk1 else ''
        PIN2 = test.dut.sim.pin2 if test.dut.sim.pin2 else '0000'
        PUK2 = test.dut.sim.puk2 if test.dut.sim.puk2 else ''        

        PIN1_CHANGE = '6666'
        PIN1_BAD = '9876'

        if not PUK1:
            test.fail('Unknown PUK1 number!')        
            
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
            ],
            expect='',
            expect_exit_code=0)
            
        if not 'ARC_PIN_STATUS_PIN' in response:  
            test.dut.dstl_embedded_linux_reboot()    
            
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus",
                "lock=0",
                "PIN={}".format(PIN1_BAD)
            ],
            expect='SIM PIN is required for this operation|is incorrect',
            expect_exit_code=3)
            
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_UnlockPin",
                "PIN={}".format(PIN1),
            ],
            expect='',
            expect_exit_code=0)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus",
                "lock=0",
                "PIN={}".format(PIN1)
            ],
            expect='',
            expect_exit_code=0)

        
        
        test.dut.dstl_embedded_linux_reboot()


        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
            ],
            expect='ARC_PIN_STATUS_READY',
            expect_exit_code=0)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_UnlockPin",
                "PIN={}".format(PIN1),
            ],
            expect='not allowed',
            expect_exit_code=3)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetIMEI"
            ],
            expect='',
            expect_exit_code=0)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus",
                "lock=1",
                "PIN={}".format(PIN1)
            ],
            expect='',
            expect_exit_code=0)



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

if "__main__" == __name__:
    unicorn.main()
