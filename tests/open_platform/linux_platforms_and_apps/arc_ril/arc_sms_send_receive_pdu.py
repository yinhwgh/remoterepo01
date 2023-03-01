# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096514.001 arc_sms_send_receive_pdu.py

import unicorn
import re
from core.basetest import BaseTest
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_preconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_postconditions
from dstl.embedded_system.linux.configuration import dstl_embedded_linux_collect_logcat
from dstl.embedded_system.linux.application import dstl_embedded_linux_prepare_application
from dstl.embedded_system.linux.application import dstl_embedded_linux_run_application
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms import write_sms_to_memory
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory

ver = "1.1"

class ArcSmsSendReceivePdu(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        if not test.dut.sim.sca_pdu:
            test.log.info("Please use a SIM for DUT Card where den Entry sca_pdu exist\n Test abort")
            test.expect(False, critical=True)
        if not test.r1.sim.pdu:
            test.log.info("Please use a SIM for R1 Card where den Entry sim.pdu exist\n Test abort")
            test.expect(False, critical=True)
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r1.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(test.r1.at1.send_and_verify('AT+CNMI=1,1', '.*OK.*'))
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")

    def run(test):

        pdu_content = "0BC8329BFD065DDF723619"
        sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0001" + pdu_content

        test.log.step("0.1 enter PIN if needed")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "PROCEDURE=ARC_GetPinStatus"],
                                                     expect='Arc Library is now open')

        if 'ARC_PIN_STATUS_READY' in test.dut.adb.last_response:
            test.log.info('PIN is already entered.')
            test.sleep(10)
        else:
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=PinPukAPIs",
                                                                 "PROCEDURE=ARC_UnlockPin",
                                                                 "PIN={}".format(test.dut.sim.pin1)],
                                                         expect='PIN_READY')
            test.sleep(30)

        test.log.step("1.1 send SMS PDU mode >Hello World<")
        pdu_content = "0BC8329BFD065DDF723619"
        sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0001" + pdu_content

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SmsAPIs",
                                                             "PROCEDURE=ARC_SendTextMessagePDU",
                                                             "PDU="+sms_pdu],
                                                     expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                     expect_exit_code=0)
        test.log.step("1.2 Receive SMS from dut")
        test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
        test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*Hello World.*OK.*'))

        test.log.step("2.1 send SMS PDU mode >abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop<")
        sms_pdu = test.dut.sim.sca_pdu + "1100" + test.r1.sim.pdu + "0000" + "9F61F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC301"
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SmsAPIs",
                                                             "PROCEDURE=ARC_SendTextMessagePDU",
                                                             "PDU="+sms_pdu],
                                                     expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                     expect_exit_code=0)
        test.log.step("2.2 Receive SMS from dut")
        test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
        test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*OK.*'))

        test.log.step("3.1 send SMS PDU mode without SCA >Hello World<")
        sms_pdu = "001100" + test.r1.sim.pdu + "0001" + pdu_content
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SmsAPIs",
                                                             "PROCEDURE=ARC_SendTextMessagePDU",
                                                             "PDU="+sms_pdu],
                                                     expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                     expect_exit_code=0)
        test.log.step("3.2 Receive SMS from dut")
        test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
        test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*Hello World.*Hello World.*OK.*'))

        test.log.step("4.1 send SMS PDU mode without SCA >abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop<")
        sms_pdu = "001100" + test.r1.sim.pdu + "0000" + "9F61F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC3E5737AFD6EC7E7F561F1985C369FD36A74DBCD7EC301"
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SmsAPIs",
                                                             "PROCEDURE=ARC_SendTextMessagePDU",
                                                             "PDU="+sms_pdu],
                                                     expect='.*Message reference number: [0-9][0-9][0-9].*|.*Message reference number: [0-9][0-9].*|.*Message reference number: [0-9].*',
                                                     expect_exit_code=0)
        test.log.step("4.2 Receive SMS from dut")
        test.expect(test.r1.at1.wait_for("CMTI", timeout=120))
        test.expect(test.r1.at1.send_and_verify('AT+CMGL=\"ALL\"', '.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*abcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnloprstuwvxyzabcdefgijhmnlop.*OK.*'))

        test.log.step("5.1 send SMS from remote to dut")
        index = test.r1.dstl_write_sms_to_memory(sms_text="Hello World 1234567890!", sms_format='text', return_index=True)
        smsstring = 'AT+CMSS=' + str(index[0]) + ",\"" + str(test.dut.sim.int_voice_nr) + "\""
        t1 = test.thread(test.r1.at1.send_and_verify, smsstring, expect='.*OK.*')
        t2 = test.thread(test.dut.dstl_embedded_linux_run_application, "LinuxArcRilEngine",
                         params=["PROCEDURE=ARC_ReadTextMessage",
                                 "timeout=40"],
                         expect='.*Message content: Hello World 1234567890!.*',
                         expect_exit_code=0)
        t1.join()
        t2.join()

        test.sleep(5)
        test.log.info("delete all SMS in DUT")
        result,res = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=SmsAPIs",
                                                             "PROCEDURE=ARC_GetSmsStorageStatus"],
                                                     expect='.*SMS storage status.*',
                                                     expect_exit_code=0)
        if "EXP: Total entries:" in res:
            dut_sms_total_entries = re.sub(".*EXP: Total entries: ", "", res,flags=re.DOTALL)
            dut_sms_total_entries = re.sub("\r.*", "", dut_sms_total_entries,flags=re.DOTALL)
            test.log.info("Count of SMS entries: >" + str(dut_sms_total_entries) + "<" )
        test.log.info("delete all SMS in DUT")
        for n in range (1,int(dut_sms_total_entries)+1):
            test.log.info("delete SMS " + str(n) + " of " + str(dut_sms_total_entries))
            test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                         params=["FEATURE=SmsAPIs",
                                                                 "PROCEDURE=ARC_DeleteTextMessage",
                                                                 "index=" + str(n)],
                                                         expect_exit_code=0)
        test.log.info("delete all SMS in remote device")
        test.expect(dstl_set_preferred_sms_memory(test.r1, "SM"))
        test.expect(dstl_delete_all_sms_messages(test.r1))

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
