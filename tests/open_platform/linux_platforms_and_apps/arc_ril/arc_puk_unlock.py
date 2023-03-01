# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096150.001 arc_puk_unlock.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()

    def run(test):
        test.dut.dstl_embedded_linux_reboot()
        
        test.sleep(10)
        wrong_pin = str(int(test.dut.sim.pin1) - 1)
        test.log.step("1. Enter wrong PIN x3")
        for i in range(3):
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = [
                    "PROCEDURE=ARC_UnlockPin", 
                    "PIN={}".format(wrong_pin)],
                expect='',
                expect_exit_code=None)
            test.expect('cannot unlock pin' in response.lower(), critical=True)
            test.sleep(3)
        
        test.log.step("2. Check if PIN is blocked and PUK is required")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='ARC_PIN_STATUS_PUK')         
        
        test.log.step("3. Unlock PUK")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_UnlockPuk",
                "PUK={}".format(test.dut.sim.puk1),
                "PUK2={}".format(test.dut.sim.puk2),
                "newPIN={}".format(test.dut.sim.pin1)
            ],
            expect='ARC_PIN_STATUS_READY')        
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='.*')         
        
        test.expect('ARC_PIN_STATUS_READY' in response)

            
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
