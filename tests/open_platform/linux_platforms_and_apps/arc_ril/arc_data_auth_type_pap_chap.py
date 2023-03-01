# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0102404.001 arc_data_auth_type_pap_chap.py

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
# from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_turn_off_emergoff_via_dev_board
from dstl.auxiliary.devboard import devboard

ver = "1.0"

class ArcDataAuthTypePapChap(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilDataAuthTypePapChap")

    def run(test):

        apn_v4 = "internet"
        apn_v6 = "internetipv6"

        try:
            if test.dut.sim.apn_v4: apn_v4 = test.dut.sim.apn_v4
        except KeyError as ex:
            pass
        try:
            if test.dut.sim.apn_v6: apn_v6 = test.dut.sim.apn_v6
        except KeyError as ex:
            pass

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilDataAuthTypePapChap",
                                                     params=["apn={}".format(apn_v4) ],
                                                     expect='EXP',
                                                     expect_exit_code=0)

        test.log.info("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
