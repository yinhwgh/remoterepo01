#responsible: michal.jastrzebski@globallogic.com
#location: Wroclaw
#TC0105154.002

import unicorn
import datetime
import random
from time import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.configuration.network_registration_status import dstl_set_network_registration_urc


class Test(BaseTest):
    """
    Check basic functionality Time Zone Reporting.

    1. Enter SIM PIN.
    2. Enable time zone reporting by CTZV: URC via AT+CTZR=1 and automatic update AT+CTZU=1.
    3. Set random time and time zone e.g. AT+CCLK="22/01/01,01:00:00-02"
    4. Check time AT+CCLK?
    5. Unregister from network via AT+COPS=2
    6. Register to network by AT+COPS=0 and wait for  CTZU and CTZV: URC.
    7. Enable extended time zone reporting via AT+CTZR=2
    8. Set random time and time zone e.g. AT+CCLK="22/01/01,01:00:00-02"
    9. Check time AT+CCLK?
    10. Unregister from network via AT+COPS=2
    11. Register to network by AT+COPS=0 and wait for  CTZU and CTZE: URC.
    12. Check time AT+CCLK?
    13. Disable time zone reporting via AT+CTZR=0 and disable automatic update via AT+CTZU=0.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"', ".*OK.*"))
        test.DATE_MARGIN_IN_SECONDS = 10

    def run(test):

        test.log.step("1. Enter SIM PIN.")
        test.dut.dstl_enter_pin()
        test.expect('OK')

        test.log.step("2. Enable time zone reporting by CTZV: URC via AT+CTZR=1 and automatic update AT+CTZU=1.")
        test.expect(test.dut.at1.send_and_verify('AT+CTZR=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=1', 'OK'))

        test.log.step("3. Set random time and time zone e.g. 22/01/01,01:00:00-02")
        random_date = prepare_random_date()
        test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

        test.log.step("4. Check time AT+CCLK?")
        check_time(test, random_date)

        test.log.step("5. Unregister from network via AT+COPS=2")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))

        test.log.step("6. Register to network by AT+COPS=0 and wait for  CTZU and CTZV: URC.")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))
        test.sleep(45)
        buffer = test.dut.at1.last_response + test.dut.at1.read()
        test.expect("+CTZU:" in buffer and "+CTZV:" in buffer)

        test.log.step("7. Enable extended time zone reporting via AT+CTZR=2")
        test.expect(test.dut.at1.send_and_verify('AT+CTZR=2', 'OK'))

        test.log.step("8. Set random time and time zone e.g. 22/01/01,01:00:00-02")
        random_date = prepare_random_date()
        test.expect(test.dut.dstl_set_real_time_clock(time=format_date(random_date)))

        test.log.step("9. Check time AT+CCLK?")
        check_time(test, random_date)

        test.log.step("10. Unregister from network via AT+COPS=2")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))

        test.log.step("11. Register to network by AT+COPS=0 and wait for  CTZU and CTZE: URC.")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))
        test.sleep(45)
        buffer = test.dut.at1.last_response + test.dut.at1.read()
        test.expect("+CTZU: " in buffer and "+CTZE: " in buffer)

        test.log.step("12. Check time AT+CCLK?")
        test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
        test.expect(datetime.datetime.now().strftime("%y/%m/%d") in test.dut.at1.last_response)

        test.log.step("13. Disable time zone reporting via AT+CTZR=0 and disable automatic update via AT+CTZU=0.")
        test.expect(test.dut.at1.send_and_verify('AT+CTZR=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CTZU=0', 'OK'))


    def cleanup(test):
        test.expect(test.dut.dstl_set_real_time_clock())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', ".*OK.*"))

def format_date(date):
    return date.strftime("%y/%m/%d,%H:%M:%S")

def add_time_to_date(date, seconds_to_add):
    return date + datetime.timedelta(seconds=seconds_to_add)

def check_time(test,date):
    test.expect(test.dut.at1.send_and_verify("AT+CCLK?", ".*OK.*"))
    current_date = test.dut.at1.last_response
    expected_date = False
    for second in range(test.DATE_MARGIN_IN_SECONDS):
        if format_date(add_time_to_date(date, second)) in current_date:
            expected_date = True
            break
    test.expect(expected_date)

def prepare_random_date():
    start_date = datetime.datetime(2020, 10, 1)
    end_date = datetime.datetime(2030, 12, 31)
    return start_date + datetime.timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())),)

if "__main__" == __name__:
    unicorn.main()
