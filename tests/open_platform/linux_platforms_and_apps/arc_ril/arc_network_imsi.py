# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096401.001 arc_network_imsi.py

import re

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
        
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine", 
            params=["PROCEDURE=ARC_GetIMSI"],
            expect='.*IMSI.*')
        test.expect('of curent SIM card' in response)
        imsi_value = re.search('of curent SIM card:\s?(\d+)', response)
        test.expect(imsi_value)
  
  
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
