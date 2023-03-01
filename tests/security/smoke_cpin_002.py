# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0095389.002

import re
import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import  dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_enter_puk1
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1
from dstl.supplementary_services.lock_unlock_facility import dstl_lock_unlock_facility
from dstl.usim.sset_mode_control import dstl_wait_for_sim_ready


class Test(BaseTest):
    """
    1. Check enter wrong PIN.
    1.1. check PIN (AT+CPIN?)
    1.2. enter wrong PIN (AT+CPIN=1234)
    1.3. enter correct PIN (AT+CPIN=9999)

    2. Check disabling PIN lock with CLCK.
    2.1. deactivate PIN with clck (AT+CLCK="SC",0,9999)
    2.2. restart (AT+CFUN=1,1)
    2.3. check PIN (AT+CPIN?)

    3. Check enabling PIN lock with CLCK.
    3.1. activate PIN with clck (AT+CLCK="SC",1,9999)
    3.2. restart (AT+CFUN=1,1)
    3.3. check PIN (AT+CPIN?)
    3.4. enter PIN (AT+CPIN=9999)

    4. Check block and restore PIN.
    4.1. check PIN (AT+CPIN?)
    4.2. restart (AT+CFUN=1,1)
    4.3. enter wrong PIN 3 times (AT+CPIN=2345)
    4.4. check PIN (AT+CPIN?)
    4.5. enter PUK and PIN (AT+CPIN=<PUK>,9999)
    4.6. check PIN (AT+CPIN?)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)

    def run(test):
        test.log.info('1. Check enter wrong PIN.')
        test.log.step('1.1. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*OK.*"))

        test.log.step('1.2. enter wrong PIN (AT+CPIN=1234)')

        class WrongPin:
            def __init__(self, pin1):
                self.pin1 = pin1

        wrongpin = WrongPin("1234")
        test.expect(not dstl_enter_pin(test.dut, device_sim=wrongpin, wait_till_ready=False))
        test.expect(re.search(r".*CME ERROR: incorrect password.*", test.dut.at1.last_response))

        test.log.step('1.3. enter correct PIN (AT+CPIN=9999)')
        test.expect(dstl_enter_pin(test.dut))

        test.log.info('2. Check disabling PIN lock with CLCK.')
        test.log.step('2.1. deactivate PIN with clck (AT+CLCK="SC",0,9999)')
        test.expect(dstl_lock_unlock_facility(test.dut, facility="SC", lock=False))

        test.log.step('2.2. restart (AT+CFUN=1,1)')
        test.expect(dstl_restart(test.dut))
        time.sleep(10)

        test.log.step('2.3. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*READY.*"))

        test.log.info('3. Check enabling PIN lock with CLCK.')
        test.log.step('3.1. activate PIN with clck (AT+CLCK="SC",1,9999)')
        test.expect(dstl_lock_unlock_facility(test.dut, facility="SC", lock=True))

        test.log.step('3.2. restart (AT+CFUN=1,1)')
        test.expect(dstl_restart(test.dut))
        time.sleep(10)

        test.log.step('3.3. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*CPIN: SIM PIN.*"))

        test.log.step('3.4. enter PIN (AT+CPIN=9999)')
        test.expect(dstl_enter_pin(test.dut))

        test.log.info('4. Check block and restore PIN.')
        test.log.step('4.1. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*READY.*"))

        test.log.step('4.2. restart (AT+CFUN=1,1)')
        test.expect(dstl_restart(test.dut))
        time.sleep(10)

        test.log.step('4.3. enter wrong PIN 3 times (AT+CPIN=2345)')
        wrongpin = WrongPin("2345")
        test.expect(not dstl_enter_pin(test.dut, device_sim=wrongpin, wait_till_ready=False))
        test.expect(re.search(r".*CME ERROR: incorrect password.*", test.dut.at1.last_response))
        test.expect(not dstl_enter_pin(test.dut, device_sim=wrongpin, wait_till_ready=False))
        test.expect(re.search(r".*CME ERROR: incorrect password.*", test.dut.at1.last_response))
        test.expect(not dstl_enter_pin(test.dut, device_sim=wrongpin, wait_till_ready=False))
        test.expect(re.search(r".*CME ERROR: SIM PUK required.*", test.dut.at1.last_response))

        test.log.step('4.4. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*SIM PUK.*"))

        test.log.step('4.5. enter PUK and PIN (AT+CPIN=<PUK>,9999)')
        test.expect(dstl_enter_puk1(test.dut, puk1=test.dut.sim.puk1, pin1=test.dut.sim.pin1))

        test.log.step('4.6. check PIN (AT+CPIN?)')
        test.expect(dstl_wait_for_sim_ready(test.dut, exp_resp=".*READY.*"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
