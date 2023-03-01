# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102337.001 arc_cbm_configuration.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
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

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='')
        
        if 'ARC_PIN_STATUS_READY' in response:
            test.dut.dstl_embedded_linux_reboot()

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_AddCbmConfig",
                "msgIDs=\"0-65535\"",
                "dcss=\"0-255\""],
            expect='SIM PIN is required',
            expect_exit_code = 3)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_GetCbmConfig"],
            expect='SIM PIN is required',
            expect_exit_code = 3)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_RemoveCbmConfig",
                "msgIDs=\"0-65535\"",
                "dcss=\"0-255\""],
            expect='SIM PIN is required',
            expect_exit_code = 3
            )

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_GetCbmConfig"],
            expect_exit_code = 3,
            expect='SIM PIN is required')

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

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_AddCbmConfig",
                "msgIDs=\"0-65535\"",
                "dcss=\"0-255\""],
            expect='The new CBM config has been added')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_GetCbmConfig"],
            expect='DCSs currently selected: 0-255')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_RemoveCbmConfig",
                "msgIDs=\"0-65535\"",
                "dcss=\"0-255\""],
            expect='CBM config has been removed')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_GetCbmConfig"],
            expect='DCSs currently selected: 0-255')

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
