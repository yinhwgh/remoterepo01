# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0103821.001 - TpSATSendUSSD_AR


"""
This testcase is intended to test in Automatic mode the Proactive Command:
SEND USSD

Registration to network.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from dstl.network_service import network_access_type

class TpSATSendUSSD(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()

    def run(test):
        sendussd_applet_sstk(test, 'MenuApplet')


    def cleanup(test):
        test.log.info("***** Erase record #2 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(2, '')
        test.dut.dstl_lock_sim()


def sendussd_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactive_cmd = 'D01381030112008202818385008A060F2A1A0C3602'
    if (test.dut.project == 'VIPER'):
        terminal_response = '810301120002028281030100'
    else:
        terminal_response = '010301120002028281030130'
    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')

        test.log.info("***** Update the EF record #2 with Send USSD command ****")
        test.dut.dstl_update_record_2f51(2, proactive_cmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    test.log.info("**** [SSTA=0]: Register to network ****")
    test.dut.dstl_register_to_network()
    test.dut.dstl_set_network_single_mode("umts")
    test.sleep(5)

    if trigger_mode == 'MenuApplet':
        test.log.info("**** [SSTA=0]: Trigger execution of record #2 Send USSD ****")
        test.dut.dstl_trigger_execution_of_record(2)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactive_cmd, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactive_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)


if (__name__ == "__main__"):
    unicorn.main()
