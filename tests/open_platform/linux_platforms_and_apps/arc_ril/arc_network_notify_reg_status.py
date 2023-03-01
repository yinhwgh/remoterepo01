# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096408.001 arc_network_notify_reg_status.py

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

        test.log.step("1. Prepare module. Reboot if registered.")
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')        
        if 'ARC_PIN_STATUS_READY' in response:
            test.log.info('PIN is already entered - rebooting.')
            test.dut.dstl_embedded_linux_reboot()    
        
        test.log.step("2. Enter PIN. Check if notification was registered.")
        
        test.sleep(15)
        
        response_all = ''
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')  
        response_all += response
        
        if 'ARC_PIN_STATUS_READY' in response:
            test.log.info('PIN is unlocked')
        else:
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
        response_all += response
        
        test.sleep(15)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')  
        response_all += response
        
        test.expect('NOTIFICATION: registration status' in response_all)

            
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
