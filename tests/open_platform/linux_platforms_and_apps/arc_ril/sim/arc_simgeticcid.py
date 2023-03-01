# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0096295.001.001
# jira: KRAKEN-516
# feature: LM0006234.001 (Bobcat01,04,06), LM000xyz.001 (Kraken01)
#
#

import unicorn
from core.basetest import BaseTest
import dstl.embedded_system.linux.configuration
from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
import time

testcase_id = "arc_ril_sim_geticcid"
ver = "1.0"
filename_short_file = "hello_world.txt"
filename_big_file = "hello_world100.txt"


class Test(BaseTest):

    def setup(test):
        test.pin1 = test.dut.sim.pin1
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions()
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\sim\\ARC_SimGetIccid", "/home/cust/demo")

    def run(test):
        test.expect(test.dut.dstl_embedded_linux_run_application("/home/cust/demo/ARC_SimGetIccid",
                                                                 params="PIN={}".format(test.pin1),
                                                                 expect=".*return: 0.*"))
        # test.expect('success' in output)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
