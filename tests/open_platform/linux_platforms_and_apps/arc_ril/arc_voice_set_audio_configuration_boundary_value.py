# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103582.001 arc_voice_set_audio_configuration_boundary_value.py

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
            params = ["PROCEDURE=ARC_GetPinStatus"],
                expect='Arc Library is now open')
        
        if 'ARC_PIN_STATUS_READY' in test.dut.adb.last_response:
            test.log.info('PIN is already entered.')
            test.sleep(5)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
            test.sleep(30)
            
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_SetAudioConfiguration",
                      "volume=10",
                      "cfg=10"],
            expect='non-existing index',
            expect_exit_code=3)            
            
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
