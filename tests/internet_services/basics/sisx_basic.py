# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107951.001

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
    To check basic SISX commands behavior

    Description:
    1) Power on Module (do not enter PIN)
    2) Check SISX test command (AT^SISX=?)
    3) Check SISX read command (AT^SISX?)
    4) Check SISX incorrect command (AT^SISX)
    5) Check SISX correct command (AT^SISX="ping",1,"8.8.8.8")
    6) Enter PIN
    7) Check SISX test command (AT^SISX=?)
    8) Check SISX read command (AT^SISX?)
    9) Check SISX incorrect command (AT^SISX)
    10) Check SISX correct command but without SICA activated (AT^SISX="ping",1,"8.8.8.8")
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error_pin = "+CME ERROR: SIM PIN required"
        test.error = "+CME ERROR:"
        test.sisx_resp = '^SISX: "Ping",(1-16),,(1-30),(200-10000)\r\n' \
                         '^SISX: "HostByName",(1-16)\r\n' \
                         '^SISX: "Ntp",(1-16)'

    def run(test):
        test.log.info("TC0107951.001 Sisx_basic")
        test.log.step('1) Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2) Check SISX test command (AT^SISX=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX=?', expect=test.error_pin))

        test.log.step('3) Check SISX read command (AT^SISX?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX?',
                                                 expect=test.error_pin))

        test.log.step('4) Check SISX incorrect command (AT^SISX)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX', expect=test.error_pin))

        test.log.step('5) Check SISX correct command (AT^SISX="ping",1,"8.8.8.8")')
        test.expect(test.dut.at1.send_and_verify('AT^SISX="ping",1,"8.8.8.8"',
                                                    expect=test.error_pin))

        test.log.step('6) Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('7) Check SISX test command (AT^SISX=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX=?', expect=test.sisx_resp))

        test.log.step('8) Check SISX read command (AT^SISX?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX?', expect=test.error))

        test.log.step('9) Check SISX incorrect command (AT^SISX)')
        test.expect(test.dut.at1.send_and_verify('AT^SISX', expect=test.error))

        test.log.step('10) Check SISX correct command but without SICA activated '
                      '(AT^SISX="ping",1,"8.8.8.8")')
        test.expect(test.dut.at1.send_and_verify('AT^SISX="ping",1,"8.8.8.8"', expect=test.error))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()