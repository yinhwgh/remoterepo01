# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0087759.001 - TpSATRunAtCmd_AR

"""
This testcase is intended to test in Automatic mode the Proactive Command:
RUN AT COMMAND

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

class TpSATRunATCMD(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("***** Disble SIM PIN lock before testing ****")
        test.dut.dstl_unlock_sim()

    def run(test):
        ranatcmd_applet_sstk(test, 'MenuApplet')

    def cleanup(test):
        test.log.info("***** Erase record #2 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(2, '')
        test.dut.dstl_lock_sim()


def ranatcmd_applet_sstk(test,trigger_mode):
    """
         put AT-CMD in atcmd to do test
         such as
                AT+CSCS="GSM"
                AT+CPBS="SM"
                .....
                AT&F
        """
    atcmd = 'AT+CSCS="UCS2"'
    hexatcmd = ''
    for i in atcmd:
        hexatcmd = hexatcmd.__add__(hex(ord(i)))
    hexatcmd = hexatcmd.replace('0x', '').upper()
    lenhexatcmd = int(len(hexatcmd) / 2)
    pacrunatcmd = '810301340082028182050028'
    lenpacrunatcmd = 13
    proactivecmd = 'D0' + hex(lenhexatcmd + lenpacrunatcmd).replace('0x', '').upper() + pacrunatcmd + hex(lenhexatcmd).replace('0x', '').upper().rjust(2, '0') + hexatcmd

    if trigger_mode == 'MenuApplet':
        # initalize SIM : clean n records of EF_2F51
        n = 5
        for i in range(1, n + 1):
            test.dut.dstl_update_record_2f51(i, '')
        test.log.info("***** Update the EF record RUN-ATCMD proactive command ****")
        test.dut.dstl_update_record_2f51(1, proactivecmd[2:])

    test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
    test.dut.dstl_switch_on_sat_urc()

    test.log.info("**** [SSTA=0]: Trigger execution of record #1 RUN-ATCMD proactive command ****")
    if trigger_mode == 'MenuApplet':
        test.dut.dstl_trigger_execution_of_record(1)
        test.expect("+CSIM: 4," in test.dut.at1.last_response)
    else:
        test.expect(test.dut.at1.send_and_verify(trigger_mode + '=' + proactivecmd, ".*OK.*", wait_for=",\"01\""))

    test.expect(proactivecmd in test.dut.at1.last_response)
    test.expect("810301340002028281030100" in test.dut.at1.last_response)



if (__name__ == "__main__"):
    unicorn.main()
