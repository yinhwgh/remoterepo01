# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0103477.001 - TpSATGetInput
from dstl.usat import sim_instance

"""
This test case is intended to test the SIM proactive command "Get Input"

SAT applet: Menu applet loaded on SIM

EF 2F51 test file on SIM for storing proactive commands.
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *

class TpSATGetInput(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()

    def run(test):
        getinput_applet_sstk(test, 'MenuApplet')


    def cleanup(test):
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()

def getinput_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactive_cmd = 'D0250103022304020281820D16005076393C2F83CA6E7A590E9ABFDB653A3AED3EEB1A1102010F'
    terminal_response = '010302230402028281030100'
    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')

        test.log.info("***** Update the EF record #1 Get Input command ****")
        test.dut.dstl_update_record_2f51(1, proactive_cmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    if trigger_mode == 'MenuApplet':
        test.log.info("**** [SSTA=0]: Trigger execution of record #1 Get Input command ****")
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactive_cmd, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactive_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)


if (__name__ == "__main__"):
    unicorn.main()
