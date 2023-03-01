# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102225.001 arc_network_provider_config_identification.py

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
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_GetPinStatus"
                ],
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
        
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_RegisterToNetworkAutomatic",
                "prefAcT=3",
                "waitForReg=1"
            ],
            expect='access technology')        
        test.expect('LTE' in response)
        
        test.sleep(30)        
        
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=[
                "PROCEDURE=ARC_GetProviderConfigIdentification",
                "prefAcT=2", 
                "waitForReg=1"
            ],
            expect='Provider configuration')
        test.expect('Config identification is correct' in response)
        
        
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params = [
                "PROCEDURE=ARC_AtcTunneling",
                "cmd=AT+cops=0"
            ],
            expect='EXP') 
        test.sleep(30)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
