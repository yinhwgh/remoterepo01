# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107942.001

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
    To check basic SIPS command behavior

    Description:
    1) Power on Module (do not enter PIN)
    2) Check SIPS test command (AT^SIPS=?)
    3) Check SIPS read command (AT^SIPS?)
    4) Check SIPS incorrect command (AT^SIPS)
    5) Enter PIN
    6) Repeat steps 2-4
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.sips_answer = '^SIPS: ("service","all"),("reset","save","load"),(0-9)'
        test.error = "+CME ERROR:"

    def run(test):
        test.log.info("TC0107942.001 Sips_basic")
        test.log.step('1) Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2) Check SIPS test command (AT^SIPS=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SIPS=?', expect=test.sips_answer,
                                                 wait_for="OK"))

        test.log.step('3) Check SIPS read command (AT^SIPS?)')
        test.expect(test.dut.at1.send_and_verify('AT^SIPS?', expect=test.error))

        test.log.step('4) Check SIPS incorrect command (AT^SIPS)')
        test.expect(test.dut.at1.send_and_verify('AT^SIPS', expect=test.error))

        test.log.step('5) Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('6) Repeat steps 2-4')
        test.expect(test.dut.at1.send_and_verify('AT^SIPS=?', expect=test.sips_answer,
                                                 wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SIPS?', expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SIPS', expect=test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()