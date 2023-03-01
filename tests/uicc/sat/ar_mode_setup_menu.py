# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104275.001 - TpSATSetupMenu_AR


"""
This testcase is intended to test in Automatic mode the Proactive Command:
SET-UP MENU

SAT applet: Menu applet loaded on SIM

EF 2F51 test file on SIM for storing proactive commands.

"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import *
from dstl.usat import sim_instance

class TpSATSetUpMenu(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()

    def run(test):
        setupmenu_applet_sstk(test, 'MenuApplet')


    def cleanup(test):
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()


def setupmenu_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactive_cmd = 'D03D81030125008202818205094D794F776E4D656E758F0A0148616D6275726765728F06024779726F738F06034B656261628F0B045665676574617269616E'
    pac_restore_cmd = 'D081B381030125008202818205085341542D4D454E558F0E014546324635312D5245434F52448F0E024546324635312D5245434F52448F0E034546324635312D5245434F52448F0E044546324635312D5245434F52448F0E054546324635312D5245434F52448F0E064546324635312D5245434F52448F0E074546324635312D5245434F52448F0E084546324635312D5245434F52448F0E094546324635312D5245434F52448F0E0A4546324635312D5245434F5244'
    terminal_response = '810301250002028281030100'
    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')

        test.log.info("***** Update the EF record #1 with setup menu command ****")
        test.dut.dstl_update_record_2f51(1, proactive_cmd[2:])
        test.log.info("***** Update the EF record #2 with restore setup menu command ****")
        test.dut.dstl_update_record_2f51(2, pac_restore_cmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    if trigger_mode == 'MenuApplet':
        test.log.info("**** [SSTA=0]: Trigger execution of record #1 Set Up Menu ****")
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
        test.sleep(2)
        test.log.info("**** [SSTA=0]: Trigger execution of record #2 Restore Set Up Menu ****")
        test.dut.dstl_trigger_execution_of_record(2)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
        test.sleep(2)
    else:
        test.log.info("**** [SSTA=0]: Trigger execution of Set Up Menu ****")
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactive_cmd, ".*OK.*", wait_for=",\"01\""))
        test.log.info("**** [SSTA=0]: Trigger execution of restore Set Up Menu ****")
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + pac_restore_cmd, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactive_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)
    test.expect(pac_restore_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)


if (__name__ == "__main__"):
    unicorn.main()
