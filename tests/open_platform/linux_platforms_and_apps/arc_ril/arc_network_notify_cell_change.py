# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096409.001 arc_network_notify_cell_change.py

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
        
        def pin_unlock(test):
        
            result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params='PROCEDURE=ARC_GetPinStatus',
                expect='Arc Library is now open')
            if not result:
                test.log.critical("Starting the app failed!")
                test.expect(False, critical=True)
            if 'ARC_PIN_STATUS_READY' in response:
                test.log.info('PIN is already entered.')
                test.sleep(5)
            elif 'ARC_PIN_STATUS_ABSENT' in response:
                test.fail('Incorrect SIM PIN status!')
            else:
                result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                    params = ["PROCEDURE=ARC_UnlockPin", 
                              "PIN={}".format(test.dut.sim.pin1)],
                    expect='PIN_READY')
                test.sleep(10)        
            return result,response
        
        pin_unlock(test)
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='ARC_PIN_STATUS_READY') 

        test.log.step("2. Deactivate and activate network with flight mode")
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_SetFlightMode", "flightMode=1"],
            expect='Flight mode on')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_SetFlightMode", "flightMode=0"],
            expect='Flight mode off')



        test.log.step("3. Unlock PIN and verify cell change")
        
        result,response = pin_unlock(test)
        test.expect('Cell Changed' in response)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
