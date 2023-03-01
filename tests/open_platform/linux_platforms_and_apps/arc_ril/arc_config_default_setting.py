# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0102612.001 arc_config_default_setting.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect

from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions

from dstl.embedded_system.linux.application import dstl_embedded_linux_upload_script
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_script


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions()
        test.dut.dstl_embedded_linux_upload_script(
            'src\scripts\sup\LinuxArcRilConfigDefaultCheck\LinuxArcRilConfigDefaultSetting.sh',
            flags='x')

    def run(test):
        test.dut.dstl_embedded_linux_run_script("LinuxArcRilConfigDefaultSetting.sh",
            params=[],
            expect='EXP',
            expect_exit_code=0)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
