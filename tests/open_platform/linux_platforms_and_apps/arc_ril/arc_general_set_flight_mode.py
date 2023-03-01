# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096189.001 arc_general_set_flight_mode.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        
    def run(test):
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_SetFlightMode", 
                "flightMode=1"
            ],
            expect='Flight mode on')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_UnlockPin", 
                "PIN={}".format(test.dut.sim.pin1)
            ],
            expect='(DIF:)(.*)(Error: SIM card is missing or defective)',
            expect_exit_code = None)
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_SetFlightMode", 
                "flightMode=0"
            ],
            expect='Flight mode off')

        test.sleep(10)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params=[
                "PROCEDURE=ARC_UnlockPin", 
                "PIN={}".format(test.dut.sim.pin1)
            ], 
            expect='PIN_READY')
        
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

if "__main__" == __name__:
    unicorn.main()
