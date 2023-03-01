# responsible: Yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0103807.001 - TpSATSendSMS

"""
This testcase is intended to Verify if an SMS Command message can be sent or not.
SEND_SMS capable SIM Card
SAT applet: Menu applet loaded on SIM (mugurel.florea@gemalto.com)
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
from dstl.sms import sms_center_address
from dstl.sms import sms_configurations
from dstl.sms import select_sms_format

class TpSATSendSMS(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("***** Disble SIM PIN lock before testing ****")
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/IMS","0"', ".*OK.*", timeout=30))
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_unlock_sim()


    def run(test):
        sendsms_applet_sstk(test, 'MenuApplet')


    def cleanup(test):
        # erase Proactive command in record 1#
        test.log.info("***** Erase record #1 of 3F00/2F51 ****")
        test.dut.dstl_update_record_2f51(1, '')
        test.dut.dstl_lock_sim()



def sendsms_applet_sstk(test,trigger_mode):
        # *** set Proactive_Command and Terminal_Response ********
        proactive_cmd = 'D02B01030113000202818305000B1E11000C919471320432110000CC10D3E614242CCBD96937885A9ED39D653A'
        terminal_response = '010301130002028281030100'
        if trigger_mode == 'MenuApplet':
            # initalize SIM : clean n records of EF_2F51
            n = 5
            for i in range(1, n + 1):
                test.dut.dstl_update_record_2f51(i, '')

            test.log.info("***** Update the EF record #1 with SEND SMS proactive command ****")
            test.dut.dstl_update_record_2f51(1, proactive_cmd[2:])

        test.log.info("**** [SSTA=0]: Switch on SAT/URC ****")
        test.dut.dstl_switch_on_sat_urc()

        test.log.info("**** [SSTA=0]: Register to network ****")
        test.dut.dstl_register_to_network()

        test.log.info("**** [SSTA=0]: Set SCA to BEI Testnet ****")
        test.dut.dstl_select_sms_message_format()
        test.dut.dstl_set_sms_center_address(test.dut_sim.sca_int, '145')

        test.log.info("**** [SSTA=0]: Set SMS storage to SIM ****")
        test.dut.dstl_set_preferred_sms_memory('SM', )

        test.log.info("**** [SSTA=0]: Set reception of SMS to index-indication ****")
        test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', ".*OK.*", timeout=30))

        test.log.info("**** [SSTA=0]: Trigger execution of record #1 Send SMS ****")
        if trigger_mode == 'MenuApplet':
            test.dut.dstl_trigger_execution_of_record(1)
            test.expect("+CSIM: 4," in test.dut.at1.last_response)
        else:
            test.expect(test.dut.at1.send_and_verify(trigger_mode+'='+proactive_cmd, ".*OK.*", wait_for=",\"01\""))
        test.expect(proactive_cmd in test.dut.at1.last_response)
        test.expect(terminal_response in test.dut.at1.last_response)



if (__name__ == "__main__"):
    unicorn.main()
