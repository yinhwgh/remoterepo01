#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105060.001

import unicorn

from core.basetest import BaseTest

from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.configuration import dual_sim_operation

class Test(BaseTest):
    '''
    TC0105060.001 - CheckCopnWithDualSim
    1.Use at+copn read operator names on first port

    2.At the moment,on the second port change dual sim

    3.Check module state
    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1. Enable dual sim mode")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/FNS\",\"std\""))
        test.expect(test.dut.dstl_enable_dual_sim_mode())
        test.log.step("2. Switch sim to slot 1")
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.dut.at2.send_and_verify("AT+CIMI")
        sim1_imsi = test.dut.at2.last_response
        test.log.step("3. Executing command AT+COPN and switch sim to slot 2")
        test.expect(test.dut.dstl_enter_pin())
        test.log.info("COPN function works well")
        test.expect(test.dut.at2.send_and_verify("AT+COPN", 'OK'))
        test.log.info("Interrupt COPN response by switching SIM")
        t1 = test.thread(test.dut.at2.send_and_verify, "AT+COPN")
        t1.join(1.0)
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.expect(test.dut.dstl_enter_pin())
        while "OK" not in test.dut.at2.last_response:
            test.sleep(2)
        else:
            test.log.info("OK response of AT+COPN has displayed.")        
        test.attempt(test.dut.at1.send_and_verify,"AT+CIMI", "OK", retry=3, sleep=1)
        sim2_imsi = test.dut.at1.last_response
        test.expect(sim1_imsi != sim2_imsi)
        
    def cleanup(test):
        test.sleep(2)
        test.expect(test.dut.dstl_switch_to_sim_slot1())
    
   
if __name__=='__main__':
    unicorn.main()     