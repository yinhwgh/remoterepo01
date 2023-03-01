# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107979.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    Intention:
    To check basic SISE command behavior

    Description:
    1. Power on Module (do not enter PIN)
    2. Check SISE test command (AT^SISE=?)
    3. Check SISE read command (AT^SISE?)
    4. Check SISE incorrect command (AT^SISE)
    5. Check SISE write command without any SISS profile (AT^SISE=1)
    6. Enter PIN
    7. Repeat steps 2-5
    8. Define any IP service (just service type) on previously checked profile
    (AT^SISS=1,srvtype,socket)
    9. Check SISE write command for defined profile (AT^SISE=1)
    10. Check SISE write command for defined profile (AT^SISE=1,0)
    11. Check SISE write command for defined profile (AT^SISE=1,1)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.write_response = '^SISE: 1,0'

    def run(test):
        test.log.info("TC0107979.001 Sise_basic")
        test.log.step('1. Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2. Check SISE test command (AT^SISE=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=?', expect="OK"))

        test.log.step('3. Check SISE read command (AT^SISE?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE?', expect=test.error))

        test.log.step('4. Check SISE write command without any SISS profile (AT^SISE=1)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1', expect=test.error))

        test.log.step('5. Check SISE incorrect command (AT^SISE)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE', expect=test.error))

        test.log.step('6. Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('7. Repeat steps 2-5')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=?', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SISE?', expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1', expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SISE', expect=test.error))

        test.log.step('8. Define any IP service (just service type) on previously checked profile '
                      '(AT^SISS=1,srvtype,socket)')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvtype",socket', expect="OK"))

        test.log.step('9. Check SISE write command for defined profile (AT^SISE=1)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1', expect=test.write_response))

        test.log.step('10. Check SISE write command for defined profile (AT^SISE=1,0)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1,0', expect=test.write_response))

        test.log.step('11. Check SISE write command for defined profile (AT^SISE=1,1)')
        test.expect(test.dut.at1.send_and_verify('AT^SISE=1,1', expect=test.write_response))

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut)


if "__main__" == __name__:
    unicorn.main()