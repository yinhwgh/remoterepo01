# author: mariusz.znaczko@globallogic.com
# location: Wroclaw
# TC0095319.002

# feature: LM0002573.001, LM0002573.002, LM0002573.003, LM0003209.001, LM0003209.002, LM0003209.004, LM0003359.001,
#   LM0003359.002, LM0004421.001, LM0004421.002, LM0004421.003, LM0004421.004, LM0004421.005


import re
import unicorn
from dstl.auxiliary.check_urc import dstl_check_urc
from time import sleep
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, \
    dstl_is_device_in_airplane_mode, dstl_set_full_functionality_mode
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.hardware.set_real_time_clock import check_cclk_type, dstl_set_real_time_clock, \
    dstl_enable_automatic_time_zone_update, dstl_disable_automatic_time_zone_update
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    def close_port_if_usb(test):
        if "usb" in test.dut.at1.name:
            test.dut.at1.close()

    def wait_for_sysstart_or_delay(test, wait_before_opening_port: int = 30):
        if "usb" in test.dut.at1.name:
            sleep(wait_before_opening_port)
            test.dut.at1.open()
            ret = dstl_check_urc(test.dut, "SYSSTART")
            if not ret:
                test.expect(test.dut.at1.send_and_verify("AT^SQPORT?", ".*OK.*"))
                test.log.info(" URC SYSSTART not found over USB")
            else:
                test.log.info(" URC SYSSTART found over USB")
        else:
            test.expect(dstl_check_urc(test.dut, "SYSSTART"))


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_disable_automatic_time_zone_update(test.dut)

    def run(test):
        """
        Intention:
        Simple check of the ati command with all parameters
        The Test will do the following checks:
        1. Clock check without PIN (Airplane):
            1.1. Check time with (AT+CCLK?) and assure its display format,
            1.2. Set manually defined time (AT+CCLK="20/12/31,12:30:00+00"),
            1.3. Check if time was defined correctly with (AT+CCLK?),
            1.4. Reset module using (AT+CFUN)
            1.5. Check if time was saved correctly after module restart with (AT+CCLK?),
        2. Clock check with PIN:
            2.1. Enter PIN
            2.2. Check if time is displayed correctly after network connection with (AT+CCLK?),
            2.3. Set manually defined time (AT+CCLK="20/12/31,12:30:00+00") and wait 60 sec,
            2.4. Check time (AT+CCLK?) and assure that time incremented for at last 60sec,
            2.5. Switch off module (AT+SMSO),
            2.6. Turn module on and check if time was correctly saved and displayed after module
                 turn off/on (mc:igt=1000, AT+CCLK?)
        """
        time_used_for_test = '20/12/31,12:30:00'
        test.log.step('Step 1: Clock check without PIN (Airplane Mode):')
        test.expect(dstl_set_airplane_mode(test.dut))

        test.log.step('Step 1.1: Check time with (AT+CCLK?) and assure its display format):')
        test.expect(check_cclk_type(test.dut.at1) == '')

        test.log.step('Step 1.2. Set manually defined time (AT+CCLK="20/12/31,12:30:00)')
        test.expect(dstl_set_real_time_clock(test.dut, time=time_used_for_test))

        test.log.step('Step 1.3. Check if time was defined correctly with (AT+CCLK?)')
        if check_cclk_type(test.dut.at1) == '':
            test.expect(re.search('20/12/31,12:30:0[0-9]', test.dut.at1.last_response))
        else:
            test.log.error("Real Time Clock was not set!")

        test.log.step('Step 1.4. Reset module using (AT+CFUN)')
        dstl_restart(test.dut)

        test.log.step('Step 1.5. Check if time was saved correctly after module restart with (AT+CCLK?)')
        if check_cclk_type(test.dut.at1) == '':
            test.expect(re.search('20/12/31,12:30:[0-5][0-9]', test.dut.at1.last_response))
        else:
            test.log.error("Real Time Clock was not set!")

        test.log.step('Step 2. Clock check with PIN')
        sleep(10)

        test.log.step('Step 2.1. Enter PIN')
        if dstl_is_device_in_airplane_mode(test.dut):
            dstl_set_full_functionality_mode(test.dut)
        test.expect(dstl_register_to_network(test.dut))

        test.log.step('Step 2.2. Check if time is displayed correctly after network connection'
                      ' with (AT+CCLK?)')
        if check_cclk_type(test.dut.at1) == '':
            test.expect(re.search('20/12/31,12:3[0-5]:[0-5][0-9]', test.dut.at1.last_response))
        else:
            test.log.error("Real Time Clock was not set!")

        test.log.step('Step 2.3. Set manually defined time (AT+CCLK="20/12/31,12:30:00")'
                      ' and wait 60 sec')
        test.expect(dstl_set_real_time_clock(test.dut, time=time_used_for_test))
        sleep(60)

        test.log.step('Step 2.4. Check time (AT+CCLK?) and assure that time'
                      ' incremented for at last 60 sec')
        if check_cclk_type(test.dut.at1) == '':
            test.expect(re.search('20/12/31,12:31:[0-5][0-9]', test.dut.at1.last_response))
        else:
            test.log.error("Real Time Clock was not set!")

        test.log.step('Step 2.5. Switch off module (AT+SMSO)')
        test.expect(dstl_shutdown_smso(test.dut))
        test.close_port_if_usb()
        sleep(120)
        test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
        test.wait_for_sysstart_or_delay()
        test.log.step('Step 2.6. Turn module on and check if time was correctly'
                      ' saved and displayed after module turn off/on')
        if check_cclk_type(test.dut.at1) == '':
            test.expect(re.search('20/12/31,12:3[3-5]:[0-5][0-9]', test.dut.at1.last_response))
        else:
            test.log.error("Real Time Clock was not set!")

    def cleanup(test):
        dstl_enable_automatic_time_zone_update(test.dut)


if "__main__" == __name__:
    unicorn.main()
