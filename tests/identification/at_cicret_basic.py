# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107931.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, \
    dstl_set_airplane_mode, dstl_set_minimum_functionality_mode
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention:
    To check AT^CICRET command

    Description:
    1) Power on Module (do not enter PIN)
    2) Check AT^CICRET="SWN" command
    3) Enter PIN
    4) Check AT^CICRET="SWN" command
    5) Check AT^CICRET=? command
    6) Check AT^CICRET? command
    7) Check AT^CICRET=1 command
    8) Start Airplane mode on Module (AT+CFUN=4)
    9) Check AT^CICRET="SWN" command
    10) Return to normal mode (AT+CFUN=1)
    11) Check AT^CICRET="SWN" command
    12) Start Minimum Functionality mode on Module (AT+CFUN=0)
    13) Check AT^CICRET="SWN" command
    14) Return to normal mode (AT+CFUN=1)
    15) Check AT^CICRET="SWN" command
    """

    def setup(test):
        dstl_detect(test.dut)
        test.ver = test.dut.at1.last_response.split('"swn"')[1]
        dstl_get_imei(test.dut)
        test.cicret_swn = f'at^cicret="swn"'
        test.cicret_x = f'at^cicret=?'
        test.cicretx = f'at^cicret?'
        test.cicret_1 = f'at^cicret=1'

    def run(test):
        test.log.info("TC0107931.001 AtCicret_basic")
        test.log.step('1) Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))

        test.log.step('3) Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('4) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))

        test.log.step('5) Check AT^CICRET=? command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_x, expect="OK"))

        test.log.step('6) Check AT^CICRET? command')
        test.expect(test.dut.at1.send_and_verify(test.cicretx, expect="+CME ERROR:"))

        test.log.step('7) Check AT^CICRET=1 command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_1, expect="+CME ERROR:"))

        test.log.step('8) Start Airplane mode on Module (AT+CFUN=4)')
        test.expect(dstl_set_airplane_mode(test.dut), critical=True)
        test.sleep(3)

        test.log.step('9) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))

        test.log.step('10) Return to normal mode (AT+CFUN=1)')
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)

        test.log.step('11) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))

        test.log.step('12) Start Minimum Functionality mode on Module (AT+CFUN=0)')
        test.expect(dstl_set_minimum_functionality_mode(test.dut), critical=True)
        test.sleep(3)

        test.log.step('13) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))

    def cleanup(test):
        test.log.step('14) Return to normal mode (AT+CFUN=1)')
        test.expect(dstl_set_full_functionality_mode(test.dut), critical=True)
        test.sleep(3)

        test.log.step('15) Check AT^CICRET="SWN" command')
        test.expect(test.dut.at1.send_and_verify(test.cicret_swn, expect=test.ver, wait_for="OK"))
        test.sleep(1)


if "__main__" == __name__:
    unicorn.main()