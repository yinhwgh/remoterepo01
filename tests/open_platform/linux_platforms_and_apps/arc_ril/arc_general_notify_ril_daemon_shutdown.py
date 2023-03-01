# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102494.001 arc_general_notify_ril_daemon_shutdown.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.dut.dstl_embedded_linux_prepare_application('src/testware/arc_ril/LinuxArcRilDaemonShutdown')


    def run(test):
    
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilDaemonShutdown",
            params='',
            expect='stopping RIL daemon')

        test.expect('NOTIFICATION: DAEMON SHUTDOWN' in response)
       
            
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
