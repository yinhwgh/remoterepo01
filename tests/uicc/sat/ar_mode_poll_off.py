# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0104271.001 - TpSATPollingOff_AR

"""
This testcase is intended to test in Automatic mode the Proactive Command:
POLLING OFF

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

class TpSATPollOff(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.log.info("***Disble SIM PIN lock before testing *** ")
        test.dut.dstl_unlock_sim()


    def run(test):
        polloff_applet_sstk(test,'MenuApplet')


    def cleanup(test):
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()


def polloff_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactivecmdoff = 'D009810301040082028182'
    terminaloff='810301040002028281030100'
    proactivecmdinterval = 'D00D81030103008202818284020114'
    terminalinterval = '81030103000202828103010004020114'

    if trigger_mode == 'MenuApplet':
        test.log.info("***** initialize SIM instance  ****")
        test.dut.dstl_sim_instance_init()
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')

        test.log.info("***** Update the EF record #1 with Poll Off proactive command ****")
        test.dut.dstl_update_record_2f51(1, proactivecmdoff[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    #test.log.info("**** [SSTA=0]: Register to network ****")
    #test.dut.dstl_register_to_network()

    test.log.info("**** [SSTA=0]: Trigger execution of record #1 Send Poll off ****")
    if trigger_mode == 'MenuApplet':
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactivecmdoff, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactivecmdoff in test.dut.at1.last_response)
    test.expect(terminaloff in test.dut.at1.last_response)


    test.log.info("***** Update the EF record #1 with Poll Interval proactive command ****")
    test.log.info("***** Restore the POLL_INTERVAL ****")
    if trigger_mode == 'MenuApplet':
        test.dut.dstl_update_record_2f51(1, proactivecmdinterval[2:])
        test.log.info("**** [SSTA=0]: Trigger execution of record #2 Send Poll Interval ****")
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.log.info("**** [SSTA=0]: Trigger execution : Send Poll Interval ****")
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactivecmdinterval, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactivecmdinterval in test.dut.at1.last_response)
    test.expect(terminalinterval in test.dut.at1.last_response)





if (__name__ == "__main__"):
    unicorn.main()
