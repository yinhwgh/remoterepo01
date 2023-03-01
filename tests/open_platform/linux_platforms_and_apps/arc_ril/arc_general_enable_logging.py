# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096192.001 arc_general_enable_logging.py

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect

from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application

ver = "1.0"

class ArcGeneralEnableLogging(BaseTest):

    log_file = '/home/root/RIL'

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        if test.dut.at1:
            test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")
        resp = test.dut.adb.send_and_receive("rm {}".format(test.log_file))

    def run(test):
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=EnableLogging",
                                                             "zones=2 filename={}".format(test.log_file),
                                                             "PROCEDURE=ARC_EnableLogging"],
                                                     expect='Arc Library is now open')

        resp = test.dut.adb.send_and_receive("cat {}".format(test.log_file))
        if 'ARC: Call: ARC_Close()' in resp and 'ARC: Final response: ID=' in resp:
            test.expect(True)
            test.log.info('expected responses found in RIL log file')
        else:
            test.expect(False)
            test.log.error('content of RIL log file is:')
            test.log.info(resp)

        test.dut.adb.pull("{}".format(test.log_file), test.workspace)

        test.log.info("*** test end here ***")

    def cleanup(test):
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
