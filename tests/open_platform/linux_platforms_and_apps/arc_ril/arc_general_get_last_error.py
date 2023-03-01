# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096198.001 arc_general_get_last_error.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.call.setup_voice_call import dstl_voice_call_by_number




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
        elif 'ARC_PIN_STATUS_ABSENT' in response:
            test.fail('Incorrect SIM PIN status!')
        else:
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
            test.sleep(10)        


        number = test.dut.sim.nat_voice_nr
        test.log.step("2. Start voice call from remote: call number {}".format(number))
        test.r1.at1.send_and_verify("atd{};".format(number))
        
        test.sleep(7)

        test.log.step("3. Answer call")
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_Answer"
                ],
            expect='answer') 

        test.sleep(1)
        
        test.log.step("4. End call")
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_Hangup"
                ],
            expect='Hang up call') 


        test.log.step("5. Check and verify last error")
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetLastError",
                "paramLen=255"
                ],
            expect='Error text') 
        test.expect('client ended call' in response.lower())
        


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
