# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0102392.001 arc_result_code_fligth_mode_sim_off.py

import unicorn
import re
from core.basetest import BaseTest
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_collect_logcat
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

ver = "1.0"

class ArcResultCodeFligthModeSimOff(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")

    def run(test):

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["flighMode=1",
                                                             "PROCEDURE=ARC_ConfigureFlightMode"],
                                                     expect='.* Radio  off,sim off.*',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["flighMode=1",
                                                             "PROCEDURE=ARC_SetFlightMode"],
                                                     expect='.*Flight mode on.*',
                                                     expect_exit_code=0)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "PROCEDURE=ARC_GetPinStatus"],
                                                     expect='(?s).*ABSENT.*',
                                                     expect_exit_code=0)

        test.log.info ("try to change original PIN2 to 9995")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "oldPIN2={}".format(test.dut.sim.pin2), "newPIN2=9995",
                                                             "PROCEDURE=ARC_ChangePin2",
                                                             ],
                                                     expect='(?s).*missing.*',
                                                     expect_exit_code=3)

        test.log.info ("try to change original PIN from " + str(test.dut.sim.pin1) + " to 9998")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "oldPIN={}".format(test.dut.sim.pin1), "newPIN=9998",
                                                             "PROCEDURE=ARC_ChangePin"],
                                                     expect='(?s).*missing.*',
                                                     expect_exit_code=3)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=GetFdnLockStatus",
                                                             "PROCEDURE=ARC_GetFdnLockStatus"],
                                                     expect='(?s).*missing.*',
                                                     expect_exit_code=3)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SetFdnLockStatus",
                                                             "PROCEDURE=ARC_SetFdnLockStatus", "PIN2=0000"],
                                                     expect='(?s).*missing.*',
                                                     expect_exit_code=3)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=GetIMEI",
                                                             "PROCEDURE=ARC_GetIMEI"],
                                                     expect='.*',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["flighMode=0",
                                                             "PROCEDURE=ARC_SetFlightMode"],
                                                     expect='.*Flight mode off.*',
                                                     expect_exit_code=0)

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
