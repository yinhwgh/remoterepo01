# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107972.001

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
    To check basic SISI command behavior

    Description:
    1. Power on Module (do not enter PIN)
    2. Check SISI test command (AT^SISI=?)
    3. Check SISI read command (AT^SISI?)
    4. Check SISI write command without any SISS profile (AT^SISI=1)
    5. Check SISI incorrect command (AT^SISI)
    6. Enter PIN
    7. Repeat steps 2-5
    8. Define any IP service (just service type) on previously checked profile
    (at^siss=1,srvtype,socket)
    9. Check SISI write command for defined profile (AT^SISI=1)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.error = "+CME ERROR:"
        test.test_response = '^SISI: (0-9)'
        test.read_response = '^SISI: 0,""\r\n^SISI: 1,""\r\n^SISI: 2,""\r\n^SISI: 3,""\r\n' \
                                 '^SISI: 4,""\r\n^SISI: 5,""\r\n^SISI: 6,""\r\n^SISI: 7,""\r\n' \
                                 '^SISI: 8,""\r\n^SISI: 9,""'
        test.write_response = '^SISI: 1,2,0,0,0,0'

    def run(test):
        test.log.info("TC0107972.001 Sisi_basic")
        test.log.step('1. Power on Module (do not enter PIN)')
        dstl_restart(test.dut)
        test.sleep(5)
        dstl_set_sim_waiting_for_pin1(test.dut)

        test.log.step('2. Check SISI test command (AT^SISI=?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISI=?', expect=test.test_response))

        test.log.step('3. Check SISI read command (AT^SISI?)')
        test.expect(test.dut.at1.send_and_verify('AT^SISI?', expect=test.read_response))

        test.log.step('4. Check SISI write command without any SISS profile (AT^SISI=1)')
        test.expect(test.dut.at1.send_and_verify('AT^SISI=1', expect=test.error))

        test.log.step('5. Check SISI incorrect command (AT^SISI)')
        test.expect(test.dut.at1.send_and_verify('AT^SISI', expect=test.error))

        test.log.step('6. Enter PIN')
        dstl_enter_pin(test.dut)

        test.log.step('7. Repeat steps 2-5')
        test.expect(test.dut.at1.send_and_verify('AT^SISI=?', expect=test.test_response))
        test.expect(test.dut.at1.send_and_verify('AT^SISI?', expect=test.read_response))
        test.expect(test.dut.at1.send_and_verify('AT^SISI=1', expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SISI', expect=test.error))

        test.log.step('8. Define any IP service (just service type) on previously checked profile '
                      '(at^siss=1,srvtype,socket)')
        test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvtype",socket', expect="OK"))

        test.log.step('9. Check SISI write command for defined profile (AT^SISI=1)')
        test.expect(test.dut.at1.send_and_verify('AT^SISI=1', expect=test.write_response))

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut)


if "__main__" == __name__:
    unicorn.main()