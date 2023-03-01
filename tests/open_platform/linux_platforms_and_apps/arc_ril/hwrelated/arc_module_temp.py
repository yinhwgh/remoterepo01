# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0102212.001
# jira: KRAKEN-516
# feature:
#


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import dstl.embedded_system.linux.configuration
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application


testcase_id = "arc_ril_test_HW_Temp"
ver = "1.0"
filename_short_file = "hello_world.txt"
filename_big_file = "hello_world100.txt"


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions()
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\hwrelated\\ARC_HwModuleTemp", "/home/cust/demo")

    def run(test):
        test.expect(test.dut.dstl_embedded_linux_run_application("/home/cust/demo/ARC_HwModuleTemp",
                                                                 expect=".*return: 0.*"))
        # test.expect('success' in output)

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()


if "__main__" == __name__:
    unicorn.main()
