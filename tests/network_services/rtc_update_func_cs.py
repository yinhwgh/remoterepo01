#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0094679.002

import unicorn
import datetime
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.network_registration_status import dstl_set_network_registration_urc

class Test(BaseTest):
    """
    Check if internal RTC is updated after NITZ indicator comin. This version of TC is prepared for CS network.
    Original TC has been divided to two parts, because CS part and PS part have different provider restrictions.

    1. Restart module

    --- initial settings: ---

    2. Set RTC in AT+CCLK far in the past
    3. Set AT^SIND=nitz,1
    4. Disable automatic RTC update: AT+CTZU=0
    5. Enable URC for network: AT+CREG=2
    6. Register to the network
    7. Immediately enable URC for PS network: AT+CGREG=2
    8. Wait for URCs: "+CREG: 1", and "+CIEV: nitz"
    9. Query RTC: AT+CCLK?

    --- check if RTC update is possible when NITZ came by re-registering to the network: ---

    10. Enable automatic RTC update: AT+CTZU=1
    // NOTE to Miami: to obtain +CTZU: URC the AT+CTZU=1 should be issued even after restart AT+CTZU? equals 1 (RTC is then updated correctly but no URC issued, report IPIS)
    11. Obtain NITZ from network again by re-registering to network: AT+COPS=2;+COPS=0
    12. Wait for URCs from network: "+CREG: 1", "+CTZU:", "+CIEV: nitz"
    13. Query if RTC has been updated to current UTC time: AT+CCLK?
    14. Set AT+CCLK far in the past again
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"', ".*OK.*"))

    def run(test):
        test.log.step("1. Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("2. Set RTC in AT+CCLK far in the past")
        test.expect(test.dut.dstl_set_real_time_clock(time="15/02/05,11:34:27"))

        test.log.step("3. Set AT^SIND=nitz,1")
        test.expect(test.dut.at1.send_and_verify('AT^SIND="nitz",1', '.*OK.*'))

        test.log.step("4. Disable automatic RTC update: AT+CTZU=0")
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', '.*OK.*'))

        test.log.step("5. Enable URC for network: AT+CREG=2")
        test.expect(test.dut.dstl_set_network_registration_urc(domain="cs"))

        test.log.step("6. Register to the network")
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))

        test.log.step("7. Immediately enable URC for PS network: AT+CGREG=2")
        test.expect(test.dut.dstl_set_network_registration_urc(domain="ps"))

        test.log.step("8. Wait for URCs: '+CREG: 1', and '+CIEV: nitz'")
        test.sleep(120)
        buffer = test.dut.at1.read()
        test.expect("+CREG: 1" in buffer and "+CIEV: nitz" in buffer)

        test.log.step("9. Query RTC: AT+CCLK?")
        test.expect(test.dut.at1.send_and_verify('AT+CCLK?', '.*15/02/05.*', wait_for="OK"))

        test.log.step("10. Enable automatic RTC update: AT+CTZU=1")
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', '.*OK.*'))

        test.log.step("11. Obtain NITZ from network again by re-registering to network: AT+COPS=2;+COPS=0")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', '.*OK.*'))
        test.sleep(30)
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*', timeout=90))

        test.log.step("12. Wait for URCs from network: '+CREG: 1', '+CTZU:', '+CIEV: nitz'")
        test.sleep(120)
        buffer = test.dut.at1.last_response + test.dut.at1.read()
        test.expect("+CREG: 1" in buffer and "+CTZU:" in buffer and "+CIEV: nitz" in buffer)

        test.log.step("13. Query if RTC has been updated to current UTC time: AT+CCLK?")
        test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
        test.expect(datetime.datetime.now().strftime("%y/%m/%d") in test.dut.at1.last_response)

        test.log.step("14. set AT+CCLK far in the past again")
        test.expect(test.dut.dstl_set_real_time_clock(time="15/02/05,11:34:27"))

    def cleanup(test):
        test.expect(test.dut.dstl_set_real_time_clock())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
