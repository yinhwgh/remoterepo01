# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0103911.001 arc_set_notification_method.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

ver = "1.0"

class Test(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.dut.dstl_detect()
        
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilSetNotificationMethod")


    def run(test):

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSetNotificationMethod",
                                                     expect='.*SetNotificationMethod works as expected.*')

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
