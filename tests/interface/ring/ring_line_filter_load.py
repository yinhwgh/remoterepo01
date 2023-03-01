# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0094203.001, TC0094203.002

import random
import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_set_urc
from dstl.auxiliary.init import dstl_detect
from dstl.call.setup_voice_call import dstl_voice_call_by_number, dstl_release_call
from dstl.configuration.network_registration_status import dstl_set_network_registration_urc
from dstl.configuration.reset_to_factory_default_state import \
    dstl_reset_settings_to_factory_default_values
from dstl.configuration.scfg_urc_ringline_config import dstl_activate_urc_ringline_to_local, \
    dstl_set_urc_ringline_active_time
from dstl.configuration.scfg_urc_ringline_filter import dstl_scfg_set_urc_ringline_filter
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile
from dstl.hardware.configure_and_read_adc.start_periodic_adc_voltage_measurement import \
    dstl_start_periodic_adc_voltage_measurement
from dstl.hardware.configure_and_read_adc.stop_periodic_adc_voltage_measurement import \
    dstl_stop_periodic_adc_voltage_measurement
from dstl.network_service.register_to_network import dstl_register_to_network, \
    dstl_deregister_from_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.send_sms_message import dstl_send_sms_message


class Triggers:
    sms = True
    call = True
    network = True
    sradc = True


class Test(BaseTest):
    """
    1. Set "URC/Ringline" to "local"
    2. Set "URC/Ringline/ActiveTime" to "2"
    3. Enable SMS reporting URCs with "AT+CNMI=2,1"
    4. Enable network registration URCs with "AT+CREG=1"

    "RING","+CMT" - Block

    5. Set Ring Line Indicator Filter for SMS and Call related URCs (AT^SCFG="URC/Ringline/SelWUrc",
    "RING","+CMT")
    6. Delete 1 SMS to free the memory with "AT+CMGD=1"
    7. Check and log Ring line behavior for followings URCs:
    a) For incoming SMS
    b) For incoming voice call
    c) For sradc measurements
    d) + creg (at+cops=2 and then at+cops=0)
    8. Repeat whole "RING","+CMT" - Block during, e.g. 2h with random time (1-60sec) between points
    a, b, c, d and with random order/sequence of points a, b, c, d.

    "+CMT" - Block

    5.  Set Ring Line Indicator Filter for SMS URCs (AT^SCFG="URC/Ringline/SelWUrc","+CMT")
    6. Delete 1 SMS to free the memory with "AT+CMGD=1"
    7. Check and log Ring line behavior for followings URCs:
    a) For incoming SMS
    b) For incoming voice call
    c) For sradc measurements
    d) + creg (at+cops=2 and then at+cops=0)
    8. Repeat whole "+CMT" - Block during, e.g. 2h with random time (1-60sec) between points a, b,
    c, d and with random order/sequence of points a, b, c, d.

    "RING" - Block

    5.  Set Ring Line Indicator Filter for call related URCs (AT^SCFG="URC/Ringline/SelWUrc","RING")
    6. Delete 1 SMS to free the memory with "AT+CMGD=1"
    7. Check and log Ring line behavior for followings URCs:
    a) For incoming SMS
    b) For incoming voice call
    c) For sradc measurements
    d) + creg (at+cops=2 and then at+cops=0)
    8. Repeat whole "RING" - Block during, e.g. 2h with random time (1-60sec) between points a, b,
    c, d and with random order/sequence of points a, b, c, d.


    9. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc","ALL")
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_register_to_network(test.dut)
        dstl_register_to_network(test.r1)
        test.expect(dstl_set_urc(test.dut, urc_str="Off, RING"))

    def run(test):
        test.log.step('1. Set "URC/Ringline" to "local"')
        test.expect(dstl_activate_urc_ringline_to_local(test.dut))

        test.log.step('2. Set "URC/Ringline/ActiveTime" to "2"')
        test.expect(dstl_set_urc_ringline_active_time(test.dut, active_time="2"))

        test.log.step('3. Enable SMS reporting URCs with "AT+CNMI=2,1"')
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="2", mt="1"))

        test.log.step('4. Enable network registration URCs with "AT+CREG=1"')
        test.expect(dstl_set_network_registration_urc(test.dut, urc_mode=1))

        test.log.step('5.  Set Ring Line Indicator Filter for SMS URCs '
                      '(AT^SCFG="URC/Ringline/SelWUrc","+CMT")')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1="RING", param2="+CMT"))
        Triggers.network = False
        Triggers.sradc = False

        test.log.step('6. Delete 1 SMS to free the memory with "AT+CMGD=1"')
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('7. Check and log Ring line behavior for followings URCs:'
                      'a) For incoming SMS'
                      'b) For incoming voice call'
                      'c) For sradc measurements'
                      'd) + creg (at+cops=2 and then at+cops=0)')

        test.log.step('8. Repeat whole "RING","+CMT" - Block during, e.g. 2h with random '
                      'time (1-60sec) between points a, b, c, d and with random order/sequence '
                      'of points a, b, c, d.')
        test.test_functionalities_in_random_order()

        test.log.step('5.  Set Ring Line Indicator Filter for SMS URCs '
                      '(AT^SCFG="URC/Ringline/SelWUrc","+CMT")')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1="+CMT"))
        Triggers.call = False

        test.log.step('6. Delete 1 SMS to free the memory with "AT+CMGD=1"')
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('7. Check and log Ring line behavior for followings URCs:'
                      'a) For incoming SMS'
                      'b) For incoming voice call'
                      'c) For sradc measurements'
                      'd) + creg (at+cops=2 and then at+cops=0)')

        test.log.step('8. Repeat whole "RING","+CMT" - Block during, e.g. 2h with random '
                      'time (1-60sec) between points a, b, c, d and with random order/sequence '
                      'of points a, b, c, d.')
        test.test_functionalities_in_random_order()

        test.log.step('5.  Set Ring Line Indicator Filter for call related URCs '
                      '(AT^SCFG="URC/Ringline/SelWUrc","RING")')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1="RING"))
        Triggers.call = True
        Triggers.sms = False

        test.log.step('6. Delete 1 SMS to free the memory with "AT+CMGD=1"')
        test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('7. Check and log Ring line behavior for followings URCs:'
                      'a) For incoming SMS'
                      'b) For incoming voice call'
                      'c) For sradc measurements'
                      'd) + creg (at+cops=2 and then at+cops=0)')

        test.log.step('8. Repeat whole "RING" - Block during, e.g. 2h with random time (1-60sec) '
                      'between points a, b, c, d and with random order/sequence of '
                      'points a, b, c, d.')
        test.test_functionalities_in_random_order()

        test.log.step('9. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc","ALL")')
        test.expect(dstl_scfg_set_urc_ringline_filter(test.dut, param1="ALL"))

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_reset_settings_to_factory_default_values(test.r1))
        test.expect(dstl_store_user_defined_profile(test.r1))

    def test_functionalities_in_random_order(test):
        total_time = 1800
        passed_time = 0
        while passed_time < total_time:
            start_time = time.time()
            interval = random.randint(1, 60)
            time.sleep(interval)
            random_functionality = random.randint(0, 3)
            if random_functionality == 0:
                test.send_sms()
            elif random_functionality == 1:
                test.make_call()
            elif random_functionality == 2:
                test.check_sradc()
            elif random_functionality == 3:
                test.reattach_to_network()
            end_time = time.time()
            passed_time += end_time - start_time

    def check_ringline(test, is_ringline_activated):
        if is_ringline_activated:
            test.expect(test.dut.devboard.wait_for(expect=">URC:  RINGline: 0", timeout=60))
            test.expect(test.dut.devboard.wait_for(expect=">URC:  RINGline: 1", timeout=60))
        else:
            test.expect(not test.dut.devboard.wait_for(expect=">URC:  RINGline: 0", timeout=60))

    def send_sms(test):
        test.thread(test.check_ringline, Triggers.sms)
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                          sms_text="New message"))
        test._threads_join()

    def make_call(test):
        test.thread(test.check_ringline, Triggers.call)
        test.expect(dstl_voice_call_by_number(test.r1, test.dut, test.dut.sim.int_voice_nr))
        test.expect(dstl_release_call(test.dut))
        test._threads_join()

    def check_sradc(test):
        test.thread(test.check_ringline, Triggers.sradc)
        test.expect(dstl_start_periodic_adc_voltage_measurement(test.dut, 0))
        test.expect(dstl_stop_periodic_adc_voltage_measurement(test.dut, 0))
        test._threads_join()

    def reattach_to_network(test):
        test.thread(test.check_ringline, Triggers.network)
        test.expect(dstl_deregister_from_network(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test._threads_join()


if "__main__" == __name__:
    unicorn.main()
