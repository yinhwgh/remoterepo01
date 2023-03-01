# responsible: michal.rydzewski@globallogic.com
# location: Wroclaw
# TC0094206.001

import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.call.enable_call_ind_ext_format import dstl_enable_call_ind_ext_format, \
    dstl_disable_call_ind_ext_format
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
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.send_sms_message import dstl_send_sms_message


class Triggers:
    sms = True
    call = True
    network = True
    sradc = True


class Test(BaseTest):
    """
    1. Set Ringline Filter to "all" (AT^SCFG="URC/Ringline/SelWUrc","all")
    2. Set "URC/Ringline" to "local"
    3. Set "URC/Ringline/ActiveTime" to "2"
    4. Check if RING line is activated with incoming SMS
    5. Check if RING line is activated with VOICE CALL
    6. Check if RING line is activated with +CREG (AT+COPS=2 and then AT+COPS=0)
    7. Check if RING line is activated with SRADC
    8. Set Ringline Filter to "+CMT","RING" (AT^SCFG="URC/Ringline/SelWUrc","+CMT","RING")
    9. Check if RING line is activated with incoming SMS
    10.  Check if RING line is activated with VOICE CALL
    11. Check if RING line is activated with +CREG (AT+COPS=2 and then AT+COPS=0)
    12. Check if RING line is activated with SRADC
    13. Set Ringline Filter to "+CMT" (AT^SCFG="URC/Ringline/SelWUrc","+CMT")
    14. Check if RING line is activated with incoming SMS
    15.  Check if RING line is activated with VOICE CALL
    16.  Check if RING line is activated with +CREG (AT+COPS=2 and then AT+COPS=0)
    17. Check if RING line is activated with SRADC
    18. Set Ringline Filter to "RING" (AT^SCFG="URC/Ringline/SelWUrc","RING")
    19. Check if RING line is activated with incoming SMS
    20.  Check if RING line is activated with VOICE CALL
    21.  Check if RING line is activated with +CREG (AT+COPS=2 and then AT+COPS=0)
    22. Check if RING line is activated with SRADC
    Perform steps 1-22 with (AT+CRC=1 and AT+CRC=0)
    23. Disable +CMT URC
    24. Set Ringline Filter to "all" (AT^SCFG="URC/Ringline/SelWUrc","all")
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_register_to_network(test.dut)
        dstl_register_to_network(test.r1)
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="2", mt="1"))
        test.expect(dstl_set_network_registration_urc(test.dut, urc_mode=0))
        test.expect(dstl_select_sms_message_format(test.r1, sms_format="Text"))

    def run(test):
        test.execute_functionalities_for_variuus_urc_filters()

        test.log.step("Perform steps 1-22 with (AT+CRC=1 and AT+CRC=0)")
        test.expect(dstl_enable_call_ind_ext_format(test.dut))
        test.execute_functionalities_for_variuus_urc_filters()
        test.expect(dstl_disable_call_ind_ext_format(test.dut))
        test.execute_functionalities_for_variuus_urc_filters()

        test.log.step('23. Disable +CMT URC')
        test.expect(dstl_configure_sms_event_reporting(test.dut, mode="0"))
        test.log.step('24. Set Ringline Filter to "all" (AT^SCFG="URC/Ringline/SelWUrc","all")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1="ALL"))

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_reset_settings_to_factory_default_values(test.dut))
        test.expect(dstl_store_user_defined_profile(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.expect(dstl_reset_settings_to_factory_default_values(test.r1))
        test.expect(dstl_store_user_defined_profile(test.r1))

    def execute_functionalities_for_variuus_urc_filters(test):
        """
        Executes sequence of tested functionalities for following urc filters variants:
        - "ALL"
        - "+CMT","RING"
        - "+CMT"
        - "RING"
        """

        test.log.step('1. Set Ringline Filter to "all" (AT^SCFG="URC/Ringline/SelWUrc","all")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1="ALL"))

        test.log.step('2. Set "URC/Ringline" to "local"')
        test.expect(dstl_activate_urc_ringline_to_local(test.dut))

        test.log.step('3. Set "URC/Ringline/ActiveTime" to "2"')
        test.expect(dstl_set_urc_ringline_active_time(test.dut, active_time="2"))

        test.log.step('4. Check if RING line is activated with incoming SMS')
        test.log.info('It will be checked in step 7')

        test.log.step('5. Check if RING line is activated with VOICE CALL')
        test.log.info('It will be checked in step 7')

        test.log.step('6. Check if RING line is activated with +CREG (AT+COPS=2 and then '
                      'AT+COPS=0)')
        test.log.info('It will be checked in step 7')

        test.log.step('7. Check if RING line is activated with SRADC')
        test.execute_functionalities()

        test.log.step('8. Set Ringline Filter to "+CMT","RING" (AT^SCFG="URC/Ringline/SelWUrc",'
                      '"+CMT","RING")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1="+CMT",
                                                      param2="RING"))
        Triggers.network = False
        Triggers.sradc = False

        test.log.step('9. Check if RING line is activated with incoming SMS')
        test.log.info('It will be checked in step 12')

        test.log.step('10.  Check if RING line is activated with VOICE CALL')
        test.log.info('It will be checked in step 12')

        test.log.step('11. Check if RING line is activated with +CREG (AT+COPS=2 and then '
                      'AT+COPS=0)')
        test.log.info('It will be checked in step 12')

        test.log.step('12. Check if RING line is activated with SRADC')
        test.execute_functionalities()

        test.log.step('13. Set Ringline Filter to "+CMT" (AT^SCFG="URC/Ringline/SelWUrc","+CMT")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1="+CMT"))
        Triggers.call = False

        test.log.step('14. Check if RING line is activated with incoming SMS')
        test.log.info('It will be checked in step 17')

        test.log.step('15.  Check if RING line is activated with VOICE CALL')
        test.log.info('It will be checked in step 17')

        test.log.step('16.  Check if RING line is activated with +CREG (AT+COPS=2 and then '
                      'AT+COPS=0)')
        test.log.info('It will be checked in step 17')

        test.log.step('17. Check if RING line is activated with SRADC')
        test.execute_functionalities()

        test.log.step('18. Set Ringline Filter to "RING" (AT^SCFG="URC/Ringline/SelWUrc","RING")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1="RING"))
        Triggers.sms = False
        Triggers.call = True

        test.log.step('19. Check if RING line is activated with incoming SMS')
        test.log.info('It will be checked in step 22')

        test.log.step('20.  Check if RING line is activated with VOICE CALL')
        test.log.info('It will be checked in step 22')

        test.log.step('21.  Check if RING line is activated with +CREG (AT+COPS=2 and then '
                      'AT+COPS=0)')
        test.log.info('It will be checked in step 22')

        test.log.step('22. Check if RING line is activated with SRADC')
        test.execute_functionalities()

        Triggers.sms = True
        Triggers.call = True
        Triggers.network = True
        Triggers.sradc = True

    def execute_functionalities(test):
        test.send_sms()
        time.sleep(3)
        test.make_call()
        time.sleep(3)
        test.reattach_to_network()
        time.sleep(3)
        test.check_sradc()
        time.sleep(3)

    def check_ringline(test, is_ringline_activated):
        if is_ringline_activated:
            test.expect(test.dut.devboard.wait_for(expect=">URC:  RINGline: 0", timeout=30))
            test.expect(test.dut.devboard.wait_for(expect=">URC:  RINGline: 1", timeout=30))
        else:
            test.expect(not test.dut.devboard.wait_for(expect=">URC:  RINGline: 0", timeout=30))

    def send_sms(test):
        test.thread(test.check_ringline, Triggers.sms)
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr,
                                          sms_text="New message", set_sms_format=False))
        test._threads_join()

    def make_call(test):
        test.thread(test.check_ringline, Triggers.call)
        test.expect(dstl_voice_call_by_number(test.r1, test.dut, test.dut.sim.int_voice_nr))
        test.expect(dstl_release_call(test.dut))
        test._threads_join()

    def check_sradc(test):
        test.thread(test.check_ringline, Triggers.sradc)
        test.expect(dstl_start_periodic_adc_voltage_measurement(test.dut, 0))
        time.sleep(1)
        test.expect(dstl_stop_periodic_adc_voltage_measurement(test.dut, 0))
        test._threads_join()

    def reattach_to_network(test):
        test.expect(dstl_set_network_registration_urc(test.dut, urc_mode=1))
        test.thread(test.check_ringline, Triggers.network)
        test.expect(dstl_deregister_from_network(test.dut))
        test._threads_join()
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_network_registration_urc(test.dut, urc_mode=0))


if "__main__" == __name__:
    unicorn.main()
