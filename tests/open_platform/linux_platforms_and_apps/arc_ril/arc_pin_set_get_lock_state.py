# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096151.001 arc_pin_set_get_lock_state.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()

    def run(test):

        test.log.step("1. Unlock PIN")
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')
        if not result:
            test.log.critical("Starting the app failed!")
            test.expect(False, critical=True)
        if 'ARC_PIN_STATUS_READY' in response:
            test.log.info('PIN is already entered.')
            test.sleep(5)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
            test.sleep(30)

        
        test.log.step("2. Get PIN status")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='ARC_PIN_STATUS_READY')         
        
        
        test.log.step("3. Deactivate PIN lock")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus", 
                "lock=0", 
                "PIN={}".format(test.dut.sim.pin1)
            ],
            expect='PIN lock has been deactivated')         


        test.log.step("4. Check PIN lock status after deactivation")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinLockStatus"
            ],
            expect='PIN lock is inactive') 


        test.log.step("5. Activate PIN lock")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus", 
                "lock=1",
                "PIN={}".format(test.dut.sim.pin1)
            ],
            expect='PIN lock has been activated') 


        test.log.step("6. Check PIN lock status after activation")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinLockStatus"],
            expect='PIN lock is active') 


        test.log.step("7. Dectivate PIN lock to revert changes")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_SetPinLockStatus", 
                "lock=0",
                "PIN={}".format(test.dut.sim.pin1)
            ],
            expect='PIN lock has been deactivated') 


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
