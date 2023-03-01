# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096511.001 arc_daemon.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_reboot
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions()

    def run(test):
        test.dut.adb.send_and_receive('find /usr/lib -name libArcRilD.so')
        test.expect('libArcRilD.so' in test.dut.adb.last_response)
        
        test.dut.adb.send_and_receive('find /usr/lib -name libril-cwm-lte.so')
        test.expect('libril-cwm-lte.so' in test.dut.adb.last_response)

        test.dut.adb.send_and_receive('ps | grep rild')
        test.expect('gto-rild' in test.dut.adb.last_response)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

if "__main__" == __name__:
    unicorn.main()
