# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107943.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import \
    dstl_check_no_internet_profiles_defined
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention:
    To check basic SISS command behavior

    Description:
    1) Power on Module (do not enter PIN)
    2) Check SISS test command (AT^SISS=?)
    3) Check SISS read command (AT^SISS?)
    4) Check SISS incorrect command (AT^SISS)
    5) Enter PIN
    6) Repeat steps 2-4
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"

    def run(test):
        test.log.info("TC0107943.001 Siss_basic")
        test.log.step('1) Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2) Check SISS test command (AT^SISS=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=?', expect="OK"))

        test.log.step('3) Check SISS read command (AT^SISS?)')
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step('4) Check SISS incorrect command (AT^SISS)')
        test.expect(test.dut.at1.send_and_verify('AT^SISS', expect=test.error))

        test.log.step('5) Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('6) Repeat steps 2-4')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=?', expect="OK"))
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT^SISS', expect=test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()