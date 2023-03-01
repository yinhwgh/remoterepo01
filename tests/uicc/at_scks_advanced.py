#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0092087.001 - TpAtScksAdvanced


import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *
from dstl.call import setup_voice_call
from dstl.network_service import register_to_network



class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        time.sleep(5)
        test.r1.dstl_restart()
        test.sleep(5)
        test.r1.dstl_register_to_network()

    def run(test):
        test.log.info('**** TpAtScksAdvanced - Start ****')
        test.dut.dstl_insert_sim()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("AT^SCKS?", ".*SCKS: 1,1\s+OK\s+"))
        count = 2  # remove/insert sequence loop count
        c_test = False  # call related test flag

        for j in range(0, 2):  # for with or without pin
            test.log.info('**** '+('a) 'if (j == 0) else 'b) ') +'Check of SIM-Status, if Modul start with' +('out' if (j == 0) else'')+' PIN (sequence insert/remove/insert/remove) ****')
            for i in range(count):  # for remove/insert loop
                test.log.info('**** remove/insert Sequence run: {}'.format(i+1) +' of {}'.format(count) +' ****')
                test.scks_sim_remove_insert(c_test)
            if (j == 0):
                test.expect(test.dut.dstl_enter_pin())
                test.dut.dstl_unlock_sim()

        test.log.info('**** c) remove the SIM during a MO/MT call, insert after some seconds ****')
        c_test = True
        test.dut.dstl_register_to_network()
        for j in range(0, 2):  # for MO or MT call loop
            test.log.info('**** remove/insert Sequence with'+(' MO 'if (j == 0) else ' MT ') +'call ****')
            for i in range(0, count):
                test.log.info('loop: {}'.format(i+1) +' of {}'.format(count))
                if j == 0:
                    t = test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_sim.nat_voice_nr))
                else:
                    t = test.expect(test.dut.dstl_mt_voice_call_by_number(test.r1, test.dut_sim.nat_voice_nr))
                if t:
                    test.scks_sim_remove_insert(t)
                else:
                    test.expect(test.dut.at1.send_and_verify("AT+CHUP", ".*OK*."))

        test.log.info('**** d) remove SIM during incoming call ****')
        c_test = True
        for i in range(0, count):
            test.log.info('loop: {}'.format(i + 1) + ' of {}'.format(count))
            test.expect(test.r1.at1.send_and_verify("ATD" + test.dut_sim.nat_voice_nr + ";", ".*OK*."))
            if test.dut.at1.wait_for('RING', timeout=20):
                time.sleep(2)
                test.scks_sim_remove_insert(c_test)
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CHUP", ".*OK*."))
                test.log.error("******* incoming call failed")

        test.log.info('**** e) remove SIM during GPRS attach ****')
        c_test = False
        for i in range(0, count):
            test.log.info('loop: {}'.format(i + 1) + ' of {}'.format(count))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1"))
            test.scks_sim_remove_insert(c_test)

        test.log.info('**** Test end ***')

    def cleanup(test):
        test.dut.dstl_unlock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


    def scks_sim_remove_insert(test,call_flag):
        test.dut.dstl_remove_sim()
        test.log.info('**** Wating for "^SCKS: 0" ****')
        test.expect("^SCKS: 0" in test.dut.at1.last_response)
        if call_flag:
            test.log.info('**** Wating for "NO CARRIER" ****')
            test.expect("NO CARRIER" in test.dut.at1.last_response)
            time.sleep(2)
        test.dut.dstl_insert_sim()
        test.log.info('**** Wating for "^SCKS: 1" URC ****')
        test.expect("^SCKS: 1" in test.dut.at1.last_response)
        time.sleep(2)


if (__name__ == "__main__"):
    unicorn.main()
