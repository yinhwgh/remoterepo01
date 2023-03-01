# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0103701.001 - TpSATSetupCall_AR

"""
This testcase is intended to test in Automatic Mode, the Proactive Command:
SETUP CALL

SAT applet: Menu applet loaded on SIM

EF 2F51 test file on SIM for storing proactive commands.

Registration to network.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance
from dstl.call import setup_voice_call

class TpSATSetupCall(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()


    def run(test):
        setupcall_applet_sstk(test, 'MenuApplet')
       

    def cleanup(test):
        test.log.info("***** Erase record #2 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(2, '')
        test.dut.dstl_lock_sim()


def setupcall_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactive_cmd = 'D0230103011000020281830511546573746E65747A2D303938323430303006058190280400'
    if (test.dut.project == 'VIPER'):
        terminal_response = '010301100002028281030100'
    else:
        terminal_response = '01030110000202828103022004'
    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')
        test.log.info("***** Update the EF record #2 with SETUP CALL proactive command ****")
        test.dut.dstl_update_record_2f51(2, proactive_cmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    test.log.info("**** [SSTA=0]: Register to network ****")
    test.dut.dstl_register_to_network()

    if trigger_mode == 'MenuApplet':
        test.log.info("**** [SSTA=0]: Trigger execution of record #2 Set UP Call ****")
        test.dut.dstl_trigger_execution_of_record(2)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactive_cmd, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactive_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)

    test.log.info("**** Check the call list ****")
    test.expect(test.dut.at1.send_and_verify('AT+CLCC', ".*\+CLCC: 1.*", timeout=30))
    test.log.info("**** [SSTA=0]: Terminate call ****")
    test.expect(test.dut.at1.send_and_verify('AT+CHUP', ".*OK.*", timeout=30))
    test.log.info("**** [SSTA=0]: Check the call list ****")
    #        test.dut.dstl_check_voice_call_status_by_clcc(True)
    test.expect(test.dut.at1.send_and_verify('AT+CLCC', ".*OK.*", timeout=30))


if (__name__ == "__main__"):
    unicorn.main()
