# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0104216.001 arc_sim_fplmn_list.py

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

class ArcSimFplmnList(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilDirectSimAccess")

    def run(test):

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilDirectSimAccess",
                                                     params=["PIN={}".format(test.dut.sim.pin1),
                                                             "test=ARC_DeleteFPLMNList"],
                                                     expect="(?s).*Successfully deleted FPLMN list.(?s).*",
                                                     expect_exit_code=0)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilDirectSimAccess",
                                                     params=["PIN={}".format(test.dut.sim.pin1),
                                                             "test=ARC_ReadFPLMNList"],
                                                     expect="(?s).*Successfully read FPLMN list:(?s).*Proper list format(?s).*\(empty list\)(?s).*",
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
