# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0103476.001 - TpSATSelectItem

"""
This testcase is intended to test in Automatic Mode, the Proactive Command:
SELECT ITEM

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

class TpSATSelectItem(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("*** Disble SIM PIN lock before testing ***")
        test.dut.dstl_unlock_sim()


    def run(test):
        selectitem_applet_sstk(test, 'MenuApplet')


    def cleanup(test):
        # erase Proactive command in record 1#
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()


def selectitem_applet_sstk(test,trigger_mode):
    # *** set Proactive_Command and Terminal_Response
    proactive_cmd = 'D040010305240402028182050C596F75722063686F6963653A0F0A6148616D6275726765720F06624779726F730F06634B656261620F0B645665676574617269616E'
    terminal_response = '810305240482028281830130100100'

    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')
        test.log.info("***** Update the EF record #1 with Select Item proactive command ****")
        test.dut.dstl_update_record_2f51(1, proactive_cmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    test.log.info("**** [SSTA=0]: Trigger execution of record #1 Select Item ****")
    if trigger_mode == 'MenuApplet':
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactive_cmd, ".*OK.*", wait_for=",\"01\""))
    test.expect(proactive_cmd in test.dut.at1.last_response)
    test.expect(terminal_response in test.dut.at1.last_response)


if (__name__ == "__main__"):
    unicorn.main()