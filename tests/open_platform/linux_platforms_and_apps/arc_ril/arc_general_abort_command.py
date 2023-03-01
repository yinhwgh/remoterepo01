# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102440.001 arc_general_abort_command.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application('arc_ril\\LinuxArcRilAbortCommand')
        
    def run(test):
        result, response = test.dut.dstl_embedded_linux_run_application("LinuxArcRilAbortCommand",
            params='',
            expect='EXP')
        test.expect('Abort completed' in response or 'compl' in response)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()