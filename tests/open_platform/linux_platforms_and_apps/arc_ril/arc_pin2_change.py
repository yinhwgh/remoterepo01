# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096153.001 arc_pin2_change.py

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

class ArcPin2Change(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")

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
        test.log.info ("change original PIN2 to 6666")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "oldPIN2={}".format(test.dut.sim.pin2), "newPIN2=6666",
                                                             "PROCEDURE=ARC_ChangePin2",
                                                             ],
                                                     expect='(?s).*EXP: Pin 2 changed.*')
        test.log.info ("change PIN2 from 6666 to original PIN2")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "newPIN2={}".format(test.dut.sim.pin2), "oldPIN2=6666",
                                                             "PROCEDURE=ARC_ChangePin2",
                                                             ],
                                                     expect='(?s).*EXP: Pin 2 changed.*')

        test.log.info ("change original PIN2 to 6666")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "oldPIN2={}".format(test.dut.sim.pin2), "newPIN2=6666",
                                                             "PROCEDURE=ARC_ChangePin2",
                                                             ],
                                                     expect='(?s).*EXP: Pin 2 changed.*')

        test.log.info ("*** test end here ***")


    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.info ("cleanup change PIN2 from 6666 to original PIN2")
        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=PinPukAPIs",
                                                             "newPIN2={}".format(test.dut.sim.pin2), "oldPIN2=6666",
                                                             "PROCEDURE=ARC_ChangePin2",
                                                             ],
                                                     expect='(?s).*EXP: Pin 2 changed.*')

        # test.dut.dstl_embedded_linux_run_application("/home/cust/LinuxArcRilEngine",
        #                                              params=["FEATURE=NetworkSimAPIs",
        #                                                      "prefAcT=0 waitForReg=1",
        #                                                      "PROCEDURE=ARC_RegisterToNetworkAutomatic"],
        #                                              expect='.*COM: Preferred access technology is set to auto, the highest available.*')

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
