# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0096295.001 arc_sim_get_iccid.py

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
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilDirectSimAccess")
        
    def run(test):
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilDirectSimAccess", 
            params=[
                "test=ARC_GetICCID",
                "pin={}".format(test.dut.sim.pin1)],
            expect='Successfully read ICCID')
  
    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
