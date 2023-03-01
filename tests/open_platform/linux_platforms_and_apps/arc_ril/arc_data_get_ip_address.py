# responsible: tomasz.witka@globallogic.com
# christian.gosslar@thalesgroup.com
# location: Wroclaw
# TC0096176.001 arc_data_get_ip_address.py

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

class ArcDataGetIpAddress(BaseTest):

    def setup(test):
        test.log.com ('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com ('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_embedded_linux_preconditions('internal')
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilEngine")
        test.dut.dstl_embedded_linux_prepare_application("arc_ril\\LinuxArcRilRegisterToNetworkManual")

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
            test.sleep(10)

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=NetworkSimAPIs",
                                                             "prefAcT=2 waitForReg=1",
                                                             "PROCEDURE=ARC_RegisterToNetworkAutomatic"],
                                                     expect='(?s)3G.*')

        result,res = test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=DataAPIs",
                                                             "Int_Data_Nr={}".format(test.dut.sim.int_data_nr),
                                                             "apn={}".format(test.dut.sim.gprs_apn),
                                                             "user={}".format(test.dut.sim.gprs_user),
                                                             "authType=0 protocol=0",
                                                             "PROCEDURE=ARC_StartDataConnection"],
                                                     expect='(?s).*')
        if "EXP: Data connection started on context:" in res:
            act_cid = re.sub(".*EXP: Data connection started on context: ", "", res,flags=re.DOTALL)
            act_cid = re.sub("\r.*", "", act_cid,flags=re.DOTALL)
            test.log.info("Active context is >" + str(act_cid) + "<" )
        else:
            test.expect(False)
            test.log.info("No active context found")

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=DataAPIs",
                                                             "cid=" + str(act_cid),
                                                             "PROCEDURE=ARC_GetIpAddress"],
                                                     expect='(?s).*')

        test.log.info ("*** test end here ***")

    def cleanup(test):
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.dut.dstl_embedded_linux_run_application("LinuxArcRilEngine",
                                                     params=["FEATURE=NetworkSimAPIs",
                                                             "prefAcT=0 waitForReg=1",
                                                             "PROCEDURE=ARC_RegisterToNetworkAutomatic"],
                                                     expect='.*COM: Preferred access technology is set to auto, the highest available.*')

        test.dut.dstl_embedded_linux_collect_logcat()
        test.dut.dstl_embedded_linux_postconditions()

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')

if "__main__" == __name__:
    unicorn.main()
