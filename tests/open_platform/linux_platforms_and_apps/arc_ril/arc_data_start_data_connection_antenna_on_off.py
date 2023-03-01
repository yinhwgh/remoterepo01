# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102492.001 arc_data_start_data_connection_antenna_on_off.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_get_dev_board_version
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilDataStartDataConnectionAntennaOnOff')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        
    def run(test):
        
        def antenna_on_off(test):
            test.sleep(120)
            test.dut.devboard.send_and_verify('MC:ant1=off1')
            test.dut.devboard.send_and_verify('MC:ant2=off2')
            test.sleep(120)
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_GetSignalQuality"],
                expect='[1-4]')
            test.dut.devboard.send_and_verify('MC:ant1=on1')
            test.dut.devboard.send_and_verify('MC:ant2=on2')
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                params = ["PROCEDURE=ARC_GetSignalQuality"],
                expect='[2-5]')

        def app_run(test):
            result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilDataStartDataConnectionAntennaOnOff",
                params = ["apn=internet", "apn2=internetipv6"],
                expect='EXP',
                expect_exit_code=None)
        
        test.expect(test.dut.devboard, critical=True)
        test.dut.dstl_get_dev_board_version()
        test.thread(antenna_on_off, test)
        test.thread(app_run, test)

       
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()
        

if "__main__" == __name__:
    unicorn.main()
