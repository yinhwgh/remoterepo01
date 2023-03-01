# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103755.001 arc_gnss_start_raw.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application_arc_ril_engine()
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilGnssStartRaw')
        
    def run(test):
        test.log.step("Run GNSS test application")
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilGnssStartRaw",
            params='',
            expect='B OF RAW DATA RECEIVED')
           
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
