# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102363.001 arc_pin2_change_pin_status_const.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        

    def run(test):
    
        PIN1 = test.dut.sim.pin1 if test.dut.sim.pin1 else '9999'
        PUK1 = test.dut.sim.puk1 if test.dut.sim.puk1 else ''
        PUK2 = test.dut.sim.puk2 if test.dut.sim.puk2 else ''
        PIN2_ORIG = test.dut.sim.pin2 if test.dut.sim.pin2 else '0000'
        PIN2_CHANGE = '6666'
        PIN1_BAD = '9876'
        
        if not PUK1:
            test.fail('Unknown PUK1 number!')        
        if not PUK2:
            test.fail('Unknown PUK2 number!')   
            
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
            ],
            expect='',
            expect_exit_code=None)
        
        if 'ARC_PIN_STATUS_READY' in response or 'ARC_PIN_STATUS_PUK' in response or 'SIM PUK is required' in response:
            test.dut.dstl_embedded_linux_reboot()        
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
            ],
            expect='ARC_PIN_STATUS_PIN',
            expect_exit_code=None)
      
      
      
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_ChangePin2",
                "oldPIN2={}".format(PIN2_ORIG),
                "newPIN2={}".format(PIN2_CHANGE)
                ],
            expect='PIN',
            expect_exit_code=3)  


        for i in range(3):
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = [
                    "PROCEDURE=ARC_UnlockPin",
                    "PIN={}".format(PIN1_BAD)
                    ],
                expect='is incorrect',
                expect_exit_code=None)  
                
                
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
                ],
            expect='ARC_PIN_STATUS_PUK',
            expect_exit_code=0)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_ChangePin2",
                "PIN1={}".format(PIN1),
                "PUK1={}".format(PUK1),
                "oldPIN2={}".format(PIN2_ORIG),
                "newPIN2={}".format(PIN2_CHANGE)
                ],
            expect='',
            expect_exit_code=None)


        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_UnlockPuk",
                "newPIN={}".format(PIN1),
                "PUK1={}".format(PUK1),
                "PUK2={}".format(PUK2),
                "PUK={}".format(PUK1)
                ],
            expect='',
            expect_exit_code=0)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_ChangePin2",
                "oldPIN2={}".format(PIN2_ORIG),
                "newPIN2={}".format(PIN2_CHANGE),
                "PIN1={}".format(PIN1),
                "PUK1={}".format(PUK1),
                "PUK2={}".format(PUK2),
                "PUK={}".format(PUK1)
                ],
            expect='EXP',
            expect_exit_code=0)

        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_ChangePin2",
                "oldPIN2={}".format(PIN2_CHANGE),
                "newPIN2={}".format(PIN2_ORIG),
                "PIN1={}".format(PIN1),
                "PUK1={}".format(PUK1),
                "PUK={}".format(PUK1),
                "PUK2={}".format(PUK2)
                ],
            expect='EXP',
            expect_exit_code=0)



    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

if "__main__" == __name__:
    unicorn.main()
