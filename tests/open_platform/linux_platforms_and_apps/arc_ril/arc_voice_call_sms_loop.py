# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096356.001 arc_voice_call_sms_loop.py.py
#
# run in a loop
# normal loop is 5, can be changed via parameter
# send SMS
# make a outgoing voice call
# send sms
# r1 hang up the call
# r1 call DUT
# DUT accept the call
# send SMS
# r1 end the call
#

import unicorn
import re
import random
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
from dstl.sms import write_sms_to_memory
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory

ver = "1.0"
loop_count = 5

class ArcVoiceCallSmsLoop (BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r1.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
        test.expect(test.r1.at1.send_and_verify('AT+CNMI=1,1', '.*OK.*'))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilSupplementaryServiceFunctional")

    def run(test):

        global loop_count
        if loop_count == "":
            loop_count = test.loop_count
        if loop_count == "":
            test.expect(False)

        test.sleep(5)
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

        test.log.step("0.2 activate Call waiting")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_SET"],
                                                     expect='EXP: Set call waiting to 1',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilSupplementaryServiceFunctional",
                                                     params=["CW_GET"],
                                                     expect='EXP: Call waiting - setting: 1',
                                                     expect_exit_code=0)
        ## loop start
        for n in range(1, loop_count + 1):
            test.log.step("Step " + str(n) + ".0 of " + str(loop_count + 1) + " loops\n####################################")
            test.log.step("Step " + str(n) + ".1 send SMS PDU mode")
            sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0000" + "9F61F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC301"
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=SmsAPIs",
                                                                 "PROCEDURE=ARC_SendTextMessagePDU",
                                                                 "PDU="+sms_pdu],
                                                         expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                         expect_exit_code=0)
            test.log.step("Step " + str(n) + ".2 Receive SMS from dut")
            test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
            test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*OK.*'))
            test.expect(test.r1.at1.send_and_verify('AT+CMGD=1', '.*OK.*'))

            test.log.step("Step " + str(n) + ".3 DUT call remote 1 and remote 1 accept the call")
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=VoiceAPIs",
                                                                 "PROCEDURE=ARC_Dial",
                                                                 "phoneNo={}".format(test.r1.sim.int_voice_nr)],
                                                         expect='.*',
                                                         expect_exit_code=0)
            test.log.step("Step " + str(n) + ".4 Wait for Ring on Remote1 and accept the call")
            test.expect(test.r1.at1.wait_for("RING", timeout=120))
            test.expect(test.r1.at1.send_and_verify('ATA', '.*OK.*'))
            test.sleep(random.randint(1, 30))
            test.log.step("Step " + str(n) + ".5 send SMS PDU mode during call")
            sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0000" + "9F61F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC301"
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=SmsAPIs",
                                                                 "PROCEDURE=ARC_SendTextMessagePDU",
                                                                 "PDU="+sms_pdu],
                                                         expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                         expect_exit_code=0)
            test.log.step("Step " + str(n) + ".6 Receive SMS from dut")
            test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
            test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*OK.*'))
            test.expect(test.r1.at1.send_and_verify('AT+CMGD=1', '.*OK.*'))
            test.sleep(random.randint(1, 100))
            test.log.step("Step " + str(n) + ".7 Remote1 ends the calls")
            test.expect(test.r1.at1.send_and_verify("at+chup", "OK"))

            test.sleep(random.randint(5, 100))
            test.log.step("Step " + str(n) + ".8 Remote1 calls DUT")
            test.expect(test.r1.at1.send_and_verify("atd" + str(test.dut.sim.int_voice_nr) + ";", "OK"))
            test.sleep(5)
            test.log.step("Step " + str(n) + ".9 DUT accept the call")
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=VoiceAPIs",
                                                                 "PROCEDURE=ARC_Answer"],
                                                         expect='.*',
                                                         expect_exit_code=0)
            test.sleep(random.randint(1, 20))
            test.log.step("Step " + str(n) + ".10 send SMS PDU mode during call")
            sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0000" + "9F61F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC301"
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=SmsAPIs",
                                                                 "PROCEDURE=ARC_SendTextMessagePDU",
                                                                 "PDU="+sms_pdu],
                                                         expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                         expect_exit_code=0)
            test.log.step("Step " + str(n) + ".11 Receive SMS from dut")
            test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
            test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*OK.*'))
            test.expect(test.r1.at1.send_and_verify('AT+CMGD=1', '.*OK.*'))

            test.sleep(random.randint(10, 100))
            test.log.step("Step " + str(n) + ".12 remote 1 end the call")
            test.expect(test.r1.at1.send_and_verify("at+chup", "OK"))

            test.sleep(random.randint(5, 30))
        ## loop end

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
