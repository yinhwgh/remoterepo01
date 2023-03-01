#responsible: tomasz.witka@globallogic.com
#location: Wroclaw
#TC0000000.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.attach_to_network import dstl_enter_pin
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


"""
To collect KPI:
https://confluence.gemalto.com/display/GMVTIB/linux_arc_open_status+KPI+definition
https://confluence.gemalto.com/display/GMVTIB/linux_arc_open_time+KPI+definition

"""

class Test(BaseTest):
    
    def setup(test):
        test.require_plugin('adb')
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()


    def run(test):
        test.expect(test.dut.dstl_embedded_linux_reboot())
        test.kpi.timer_start("linux_arc_open_time", device=test.dut)
        arc_open = False
        for i in range(60):
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
               params=["PROCEDURE=ARC_Open"],
               expect='.*',
               expect_exit_code=None)        
            if 'This API is temporary not available' in response or 'Cannot open ARC' in response:
                test.sleep(1)
            elif 'Arc Library is now open' in response or 'ARC was opened successfully' in response:
                arc_open = True
                test.log.info('ARC was opened successfully - stop loop.')
                test.kpi.timer_stop("linux_arc_open_time")
                break
            else:
                test.log.warning('Unknown state. Trying again.')

        test.kpi.store(name="linux_arc_open_status", type="bin", value=arc_open, device=test.dut)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if __name__ == "__main__" :
    unicorn.main()