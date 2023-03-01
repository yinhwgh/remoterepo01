# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0103432.001 arc_sms_class_0_pdu.py

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

ver = "1.0"

class ArcSmsClass0Pdu(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r1.at1.send_and_verify('AT+CMGF=1', '.*OK.*'))
        test.expect(dstl_set_preferred_sms_memory(test.r1, "ME"))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")

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

        test.log.step("0.2 prepare Remote ")
        test.expect(test.r1.at1.send_and_verify('AT+CSMP=17,167,0,240', '.*OK.*'))

        test.log.step("1.0 send SMS from Remote to DUT")
        index = test.r1.dstl_write_sms_to_memory(sms_text="Hello World 1234567890!", sms_format='text', return_index=True)
        smsstring = 'AT+CMSS=' + str(index[0]) + ",\"" + str(test.dut.sim.int_voice_nr) + "\""

        t1 = test.thread(test.r1.at1.send_and_verify, smsstring, expect='.*OK.*')
        t2 = test.thread(test.dut.dstl_embedded_linux_run_application, "LinuxArcRilEngine",
                                                    params=["PROCEDURE=ARC_WaitForNotification",
                                                             "timeout=60 exp_notification=16"],
                                                    expect='(?s).*',
                                                    expect_exit_code=0)

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.expect(test.r1.at1.send_and_verify('AT+CSMP=17,167,0,0', '.*OK.*'))

        test.dut.dstl_embedded_linux_postconditions()
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
