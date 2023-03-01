# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102488.001 arc_pin_retry_counter.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
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

        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params='PROCEDURE=ARC_GetPinStatus',
            expect='Arc Library is now open')
        if not result:
            test.log.critical("Starting the app failed!")
            test.expect(False, critical=True)
        if 'ARC_PIN_STATUS_READY' in response:
            test.log.info('PIN is already entered. Rebooting.')
            test.dut.dstl_embedded_linux_reboot() 
            test.sleep(30)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ['PROCEDURE=ARC_GetPinRetryCounter', 
                      ''],
            expect='Retry left')
        test.expect('3' in response)    
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_UnlockPin", 
                      "PIN={}".format(int(test.dut.sim.pin1)-1)],
            expect='')
        test.expect('provided is incorrect' in response)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ['PROCEDURE=ARC_GetPinRetryCounter', 
                      ''],
            expect='Retry left')
        test.expect('2' in response)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_UnlockPin", 
                      "PIN={}".format(test.dut.sim.pin1)],
            expect='PIN_READY')
        test.sleep(30)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ['PROCEDURE=ARC_GetPinRetryCounter', 
                      ''],
            expect='Retry left')
        test.expect('3' in response)     
  
  
    def cleanup(test):
        test.dut.dstl_embedded_linux_reboot()
        test.dut.dstl_embedded_linux_postconditions()
        


if "__main__" == __name__:
    unicorn.main()
