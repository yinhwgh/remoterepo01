# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0102219.001 arc_supplementary_service_call_waiting_ext.py

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

ver = "1.0"

class arc_supplementary_service_call_waiting_ext (BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.r2.dstl_detect()
        test.expect(test.r2.dstl_register_to_network())
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilSupplementaryServiceFunctional")

    def run(test):

        test.log.step("0.1 enter PIN if needed")
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

        test.log.step("Step 1.0 Test with active call waiting")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_SET"],
                                                     expect='EXP: Set call waiting to 1',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_GET"],
                                                     expect='EXP: Call waiting - setting: 1',
                                                     expect_exit_code=0)

        test.log.step("Step 1.1 DUT call remote2")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=VoiceAPIs",
                                                             "PROCEDURE=ARC_Dial",
                                                             "phoneNo={}".format(test.r2.sim.int_voice_nr)],
                                                     expect='.*',
                                                     expect_exit_code=0)
        test.log.step("1.2 Wait for Ring on Remote2 and accept the call")
        test.expect(test.r2.at1.wait_for("RING", timeout=120))
        test.expect(test.r2.at1.send_and_verify('ATA', '.*OK.*'))

        test.sleep(5)
        test.log.step("1.3 Remote1 calls DUT")
        test.expect(test.r1.at1.send_and_verify("atd" + str(test.dut.sim.int_voice_nr) + ";", "OK"))

        test.log.step("1.4 DUT check if call is waiting call")
        test.sleep(5)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CS_GET"],
                                                     expect='ID: 1, DIR: OUTGOING, STATUS: ACTIVE.*ID: 2, DIR: INCOMING, STATUS: WAITING',
                                                     expect_exit_code=0)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CS_GET"],
                                                     expect='.*ID: 1, DIR: OUTGOING, STATUS: ACTIVE\r.*',
                                                     expect_exit_code=0)

        test.expect(test.r1.at1.send_and_verify("at+chup", "OK"))
        test.expect(test.r2.at1.send_and_verify("at+chup", "OK"))

        test.sleep(10)

        test.log.step("Step 2.0 Test with disabled call waiting")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_RST"],
                                                     expect='EXP: Set call waiting to 0',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_GET"],
                                                     expect='EXP: Call waiting - setting: 0',
                                                     expect_exit_code=0)
        test.log.step("Step 2.1 DUT call remote2")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=VoiceAPIs",
                                                             "PROCEDURE=ARC_Dial",
                                                             "phoneNo={}".format(test.r2.sim.int_voice_nr)],
                                                     expect='.*',
                                                     expect_exit_code=0)
        test.log.step("2.2 Wait for Ring on Remote2 and accept the call")
        test.expect(test.r2.at1.wait_for("RING", timeout=120))
        test.expect(test.r2.at1.send_and_verify('ATA', '.*OK.*'))

        test.sleep(5)
        test.log.step("2.3 Remote1 calls DUT")
        test.expect(test.r1.at1.send_and_verify("atd" + str(test.dut.sim.int_voice_nr) + ";", "OK"))

        test.log.step("2.4 DUT check that only one call is active, no call is waiting")
        test.sleep(5)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CS_GET"],
                                                     expect='.*ID: 1, DIR: OUTGOING, STATUS: ACTIVE\r\r\n------ CLEAN UP ------.*',
                                                     expect_exit_code=0)

        test.expect(test.r1.at1.send_and_verify("at+chup", "OK"))
        test.expect(test.r2.at1.send_and_verify("at+chup", "OK"))

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_SET"],
                                                     expect='EXP: Set call waiting to 1',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
