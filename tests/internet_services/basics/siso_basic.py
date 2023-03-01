# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107941.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention:
    To check basic SISO command behavior

    Description:
    1) Power on Module (do not enter PIN)
    2) Check SISO test command (AT^SISO=?)
    3) Check SISO read command (AT^SISO?)
    4) Check SISO incorrect command (AT^SISO)
    5) Enter PIN
    6) Repeat steps 2-4
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.expexted_response = '^SISO: 0,""\r\n^SISO: 1,""\r\n^SISO: 2,""\r\n^SISO: 3,""\r\n' \
                                 '^SISO: 4,""\r\n^SISO: 5,""\r\n^SISO: 6,""\r\n^SISO: 7,""\r\n' \
                                 '^SISO: 8,""\r\n^SISO: 9,""'

    def run(test):
        test.log.info("TC0107941.001 Siso_basic")
        test.log.step('1) Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2) Check SISO test command (AT^SISO=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=?', expect="OK"))

        test.log.step('3) Check SISO read command (AT^SISO?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISO?', expect=test.expexted_response))

        test.log.step('4) Check SISO incorrect command (AT^SISO)')
        test.expect(test.dut.at1.send_and_verify('AT^SISO', expect=test.error))

        test.log.step('5) Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('6) Repeat steps 2-4')
        test.expect(test.dut.at1.send_and_verify('AT^SISO=?', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SISO?', expect=test.expexted_response))
        test.expect(test.dut.at1.send_and_verify('AT^SISO', expect=test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()