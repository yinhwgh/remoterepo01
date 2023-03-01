# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103737.001 arc_voice_dial.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.r1.dstl_enter_pin()
        
        
    def run(test):
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')
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

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_Dial", 
                      "phoneNo={}".format(test.r1.sim.int_voice_nr)],
            expect='')
        test.sleep(10) 

        test.r1.at1.wait_for('RING')
        test.sleep(0.5)
        test.r1.at1.send_and_verify('at+chup')

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
