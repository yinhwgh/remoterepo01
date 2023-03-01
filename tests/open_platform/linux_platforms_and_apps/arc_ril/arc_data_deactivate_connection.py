# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096174.001 arc_data_deactivate_connection.py

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
        
        apn = ""
        apn_v4 = ""
        gprs_apn = ""
        try:
            apn_v4 = test.dut.sim.apn_v4
        except Exception as ex:
            pass    
        try:
            gprs_apn = test.dut.sim.gprs_apn
        except Exception as ex:
            pass  
        apn = apn_v4 if apn_v4 else gprs_apn
        
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = ["PROCEDURE=ARC_GetPinStatus"],
            expect='')
        
        if 'ARC_PIN_STATUS_READY' in test.dut.adb.last_response:
            test.log.info('PIN is already entered.')
            test.sleep(5)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_UnlockPin", 
                          "PIN={}".format(test.dut.sim.pin1)],
                expect='PIN_READY')
            test.sleep(10)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_DeactivateDataConnection",
                    "cid=1"],
            expect="deactivated") 
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_RegisterToNetworkAutomatic", 
                    "prefAcT=2",
                    "waitForReg=1"],
            expect='Arc Library is now open')
        
        test.sleep(30)
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_StartDataConnection", 
                    "authType=0",
                    "protocol=0", 
                    "apn={}".format(apn)],
            expect='Data connection started')

        if 'Cannot start data connection' in response:
            test.abort('Cannot start data connection!')
            
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["FEATURE=DataAPIs", 
                    "PROCEDURE=ARC_DeactivateDataConnection",
                    "cid=1"],
            expect="deactivated")    
        

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
