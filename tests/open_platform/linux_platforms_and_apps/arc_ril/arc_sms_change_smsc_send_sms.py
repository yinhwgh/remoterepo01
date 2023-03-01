# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096515.001 arc_sms_change_smsc_send_sms.py

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
from dstl.sms import delete_sms, send_sms_message, write_sms_to_memory
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory

ver = "1.0"

class ArcSmsChangeSmscSendSms(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
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

        test.log.step("1.0 Check if SIM PIN is entered")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "PROCEDURE=ARC_GetPinStatus"],
                                                     expect='Arc Library is now open',
                                                     expect_exit_code=0)

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

        test.log.step("2.0 change SCA ")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_GetServiceCenterAddress"],
                                                     expect='(?s).*',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_SetServiceCenterAddress",
                                                             "SMSC=0048000000000"],
                                                     expect='(?s).*',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_GetServiceCenterAddress"],
                                                     expect='.*Service Center Address: 0048000000000.*',
                                                     expect_exit_code=0)
        test.log.step("3.0 write and send SMS from remote to DUT")
        index = test.r1.dstl_write_sms_to_memory(sms_text="Hello World 1234567890!", sms_format='text', return_index=True)
        smsstring = 'AT+CMSS=' + str(index[0]) + ",\"" + str(test.dut.sim.int_voice_nr) + "\""

        t1 = test.thread( test.r1.at1.send_and_verify ,smsstring , expect='.*OK.*')
        t2 = test.thread(test.dut.dstl_embedded_linux_run_application ,"LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_ReadTextMessage",
                                                             "timeout=40"],
                                                     expect='.*Message content: Hello World 1234567890!.*',
                                                     expect_exit_code=0)
        t1.join()
        t2.join()
        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.step("set SCA back to default value")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_SetServiceCenterAddress",
                                                             "SMSC={}".format(test.dut.sim.sca_int) ],
                                                     expect='(?s).*',
                                                     expect_exit_code=0)
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["PROCEDURE=ARC_GetServiceCenterAddress"],
                                                     expect=str(test.dut.sim.sca_int),
                                                     expect_exit_code=0)

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
