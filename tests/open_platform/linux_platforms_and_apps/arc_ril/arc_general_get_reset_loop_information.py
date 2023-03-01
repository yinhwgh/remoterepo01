# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0103968.001 arc_general_get_reset_loop_information.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application_arc_ril_engine
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('src/testware/arc_ril/LinuxArcRilResetLoop')

    def run(test):
        result,response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilResetLoop", 
            params=[
                'GetResetLoopInformation'
            ],
            expect='ARC library Open')

        test.expect('threshold' in response)
        test.expect('mode' in response)
        test.expect('status' in response)
        test.expect('counter' in response)
        
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()

