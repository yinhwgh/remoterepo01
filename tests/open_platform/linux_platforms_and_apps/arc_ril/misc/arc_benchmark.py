# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0096312.001
# jira: KRAKEN-516
# feature:
#
#

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

testcase_id = "arc_ril_misc_benchmark"
ver = "1.0"


class Test(BaseTest):

    def setup(test):
        test.pin1 = test.dut.sim.pin1
        test.dut.dstl_detect()
        test.dut.dstl_embedded_linux_preconditions()
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\misc\\ARC_Benchmark")
        test.expect(True)

    def run(test):
        ret, resp = test.dut.dstl_embedded_linux_run_application("ARC_Benchmark",
                                                        params="PIN={}".format(test.pin1),
                                                        expect=".*return: 0.*")
        if ret and 'elapsed time:' in resp:
            test.expect(True)
        else:
            test.log.critical("Starting the app failed!")
            test.expect(False)


    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

if "__main__" == __name__:
  unicorn.main()
