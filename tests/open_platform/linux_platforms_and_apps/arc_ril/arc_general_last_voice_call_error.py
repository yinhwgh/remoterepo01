# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0103604.001 arc_general_last_voice_call_error.py

import unicorn
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

ver = "1.0"

class ArcGeneralLastVoiceCallError (BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilAbortSmsCommand")

    def run(test):

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "PROCEDURE=ARC_GetPinStatus"],
                                                     expect='Arc Library is now open')

        if 'ARC_PIN_STATUS_READY' in test.dut.adb.last_response:
            test.log.info('PIN is already entered.')
            test.sleep(5)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=PinPukAPIs",
                                                                 "PROCEDURE=ARC_UnlockPin",
                                                                 "PIN={}".format(test.dut.sim.pin1)],
                                                         expect='PIN_READY')
            test.sleep(5)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=VoiceAPIs",
                                                             "PROCEDURE=ARC_Dial",
                                                             "phoneNo={}".format(test.r1.sim.nat_voice_nr)],
                                                     expect='.*')
        test.sleep(5)
        test.expect(test.r1.at1.send_and_verify("at+CLCC",".*CLCC: .*"))
        test.expect(test.r1.dstl_release_call())
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=LastCallError",
                                                             "PROCEDURE=ARC_GetLastVoiceCallError",
                                                             "cmd=AT"],
                                                     expect='.*EXP: Voice Call Error text: No cause information available.*')
        # Normal call clearing is not display in Germany
        #                                              expect='.*Voice Call Error text: Normal call clearing.*')

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
