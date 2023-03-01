# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0103812.001 arc_general_notification_undertemperature.py

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.call.setup_voice_call import dstl_release_call
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_collect_logcat
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board

ver = "1.2"

class ArcGeneralNotificationUndertemperatur (BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEnablePresentUrc")
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilNotifyShutdown")

    def run(test):
        srun_unlock_code = test.dut.software_number
        srun_unlock_code = re.sub("_", "", srun_unlock_code)
        test.dut.devboard.open() # open that IGN is not toggle if the check runs later in the script
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
            params=["PROCEDURE=ARC_AtcTunneling",
                    "cmd=AT^SRUN=\"Fact/SC/Lock\",\"U\"," + str(srun_unlock_code)],
            expect_exit_code=0)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilNotifyShutdown",
                                                     params=["s=1"],
                                                     expect='.*Warning: Undertemperature.*',
                                                     expect_exit_code=0)
        test.sleep(150)
        test.expect(test.dut.devboard.send_and_verify("MC:PWRIND"))
        test.expect(test.dut.devboard.send_and_verify("MC:PWRIND", ".*MC:   PWRIND: 1.*"))
        test.expect(test.dut.dstl_check_if_module_is_on_via_dev_board() == False)
        test.dut.dstl_turn_on_igt_via_dev_board(igt_time=1500, time_to_sleep=60)

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
