# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107950.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Intention:
    To check basic SISW and SISR commands behavior

    Description:
    1) Power on Module
    2) Check SISW test command (AT^SISW=?)
    3) Check SISW read command (AT^SISW?)
    4) Check SISW incorrect command (AT^SISW)
    5) Check SISW correct command but without any profile opened (AT^SISW=0,10)
    6) Check SISR test command (AT^SISR=?)
    7) Check SISR read command (AT^SISR?)
    8) Check SISR incorrect command (AT^SISR)
    9) Check SISR correct command but without any profile opened (AT^SISR=0,10)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"

    def run(test):
        test.log.info("TC0107950.001 SiswSisr_basic")
        test.log.step('1) Power on Module')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_enter_pin(test.dut)

        test.log.step('2) Check SISW test command (AT^SISW=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISW=?', expect="OK"))

        test.log.step('3) Check SISW read command (AT^SISW?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISW?', expect=test.error))

        test.log.step('4) Check SISW incorrect command (AT^SISW)')
        test.expect(test.dut.at1.send_and_verify('AT^SISW', expect=test.error))

        test.log.step('5) Check SISW correct command but without any profile opened (AT^SISW=0,10)')
        test.expect(test.dut.at1.send_and_verify('AT^SISW=0,10', expect=test.error))

        test.log.step('6) Check SISR test command (AT^SISR=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISR=?', expect="OK"))

        test.log.step('7) Check SISR read command (AT^SISR?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISR?', expect=test.error))

        test.log.step('8) Check SISR incorrect command (AT^SISR)')
        test.expect(test.dut.at1.send_and_verify('AT^SISR', expect=test.error))

        test.log.step('9) Check SISR correct command but without any profile opened (AT^SISR=0,10)')
        test.expect(test.dut.at1.send_and_verify('AT^SISR=0,10', expect=test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()