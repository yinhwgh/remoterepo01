# responsible: michal.kopiel@globallogic.com
# location: Wroclaw
# TC0094202.001, TC0094202.002

from typing import Union

import unicorn
from core.basetest import BaseTest
from random import randint

from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.call.setup_voice_call import dstl_release_call
from dstl.configuration.scfg_urc_ringline_config import dstl_set_urc_ringline_active_time, \
    dstl_activate_urc_ringline_to_local
from dstl.configuration.scfg_urc_ringline_filter import dstl_scfg_set_urc_ringline_filter
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
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    I Ring Line Indicator Filter ON
    1. Set Ring Line Indicator Filter for SMS and Call related URCs
    (AT^SCFG="URC/Ringline/SelWUrc","RING","+CMT")
    2. Set "URC/Ringline" to "local"
    3. Set "URC/Ringline/ActiveTime" to "2"
    4. Check if Ring line is activated with incomings URS's:
    a) For incoming SMS
    b) For incoming voice call
    5. Check if Ring line is not activated with others URCs, e.g:
    a) For sradc measurements
    b) For + creg (at+cops=2 and then at+cops=0)
    II. Ring Line Indicator Filter OFF
    1. Set Ring Line Filter for all types of URCs (AT^SCFG= "URC/Ringline/SelWUrc","ALL")
    2. Check if Ring line is activated with all incomings URS's:
    a) For Incoming SMS
    b) For incoming voice call
    c) For sradc measurements
    d) For + creg (at+cops=2 and then at+cops=0)
    III. Repeat scenario I and II 10-20 times
    but in each loop change settings from point 1 in following sequence:
    -1 iteration - AT^SCFG="URC/Ringline/SelWUrc","RING","+CMT")
    -2 iteration - AT^SCFG="URC/Ringline/SelWUrc","RING")
    -3 iteration - AT^SCFG="URC/Ringline/SelWUrc","+CMT")
    -4 iteration - AT^SCFG="URC/Ringline/SelWUrc","RING","+CMT")
    -5 iteration - AT^SCFG="URC/Ringline/SelWUrc","RING")
    -…….
    IV. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc","ALL")
    """

    def setup(test):
        # Set constants values
        test.URC_TIMEOUT = 360
        test.RING_LINE_TIMEOUT = 60
        test.DESTINATION_ADDR = test.dut.sim.int_voice_nr
        test.INTERVAL_TIME_MS = 1000

        test.prepare_module(module=test.dut)
        test.prepare_module(module=test.r1)

    def run(test):
        counter = 1
        commands_sequence = [['RING', '+CMT'], 'RING', '+CMT']
        # Execute sequences
        for i in range(0, 5):
            for sequence in commands_sequence:
                ring_line_filter_param1 = sequence[0] if len(sequence) == 2 else sequence
                ring_line_filter_param2 = sequence[1] if len(sequence) == 2 else None

                test.log.step(f'Iteration number: {(i * 3) + counter}')
                test.execute_ring_line_indicator_filter_on(
                    ring_line_filter_param1=ring_line_filter_param1,
                    ring_line_filter_param2=ring_line_filter_param2)
                test.execute_ring_line_indicator_filter_off()
                counter += 1
                test.log.step('III.Repeat scenario I and II 10 - 20 times')
            counter = 1

    def cleanup(test):
        test.log.step('IV. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc","ALL")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1='ALL', param2=None))
        test.delete_sms_from_memory(test.dut)
        test.delete_sms_from_memory(test.r1)

    def execute_ring_line_indicator_filter_on(test,
                                              ring_line_filter_param1: Union[str, None] = None,
                                              ring_line_filter_param2: Union[str, None] = None):
        test.log.step('I Ring Line Indicator Filter ON')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut,
                                                      param1=ring_line_filter_param1,
                                                      param2=ring_line_filter_param2))

        test.log.step(f'1. Set Ring Line Indicator Filter for SMS and Call related URCs '
                      f'(AT^SCFG="URC/Ringline/SelWUrc")'
                      f'{ring_line_filter_param1},{ring_line_filter_param2}),')
        test.log.step('2. Set "URC/Ringline" to "local"')
        test.expect(dstl_activate_urc_ringline_to_local(device=test.dut))

        test.log.step('3. Set "URC/Ringline/ActiveTime" to "2"')
        test.expect(dstl_set_urc_ringline_active_time(device=test.dut, active_time=2))

        test.log.step('4. Check if Ring line is activated with incomings URS\'s:')
        test.log.step('a) For incoming SMS')
        sms_ring_line_listener_thread = test.thread(lambda: test.expect(
            test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))

        test.expect(dstl_send_sms_message(device=test.r1,
                                          destination_addr=test.DESTINATION_ADDR,
                                          set_sms_format=False, set_sca=False))
        test.expect(dstl_check_urc(test.dut, expect_urc='.*CMTI.*', timeout=test.URC_TIMEOUT))
        sms_ring_line_listener_thread.join()

        test.log.step('b) For incoming voice call')
        call_ring_line_listener_thread = test.thread(lambda: test.expect(
            test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))

        test.make_call(phone_number=test.DESTINATION_ADDR)
        call_ring_line_listener_thread.join()

        test.log.step('5. Check if Ring line is not activated with others URCs, e.g:')
        test.log.step('a) For sradc measurements')
        measurement_ring_line_listener_thread = None
        if ring_line_filter_param1 != '+CMT':
            measurement_ring_line_listener_thread = test.thread(lambda: test.expect(
                test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))
        else:
            measurement_ring_line_listener_thread = test.thread(lambda: test.expect(
                not test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))

        test.execute_measurement()
        measurement_ring_line_listener_thread.join()

        test.log.step('b) For + creg (at+cops=2 and then at+cops=0)')
        test.expect(dstl_deregister_from_network(test.dut))

        test.expect(dstl_register_to_network(test.dut))

    def execute_ring_line_indicator_filter_off(test):
        test.log.step('II. Ring Line Indicator Filter OFF')
        test.log.step('1. Set Ring Line Filter for all types of URCs '
                      '(AT^SCFG= "URC/Ringline/SelWUrc","ALL")')
        test.expect(dstl_scfg_set_urc_ringline_filter(device=test.dut, param1='ALL', param2=None))

        test.log.step('2. Check if Ring line is activated with all incomings URS\'s:')
        test.log.step('a) For incoming SMS')
        sms_ring_line_listener_thread = test.thread(lambda: test.expect(
            test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))

        test.expect(dstl_send_sms_message(device=test.r1,
                                          destination_addr=test.DESTINATION_ADDR,
                                          set_sms_format=False, set_sca=False))
        test.expect(dstl_check_urc(test.dut, expect_urc='.*CMTI.*', timeout=test.URC_TIMEOUT))
        sms_ring_line_listener_thread.join()

        test.log.step('b) For incoming vice call')
        call_ring_line_listener_thread = test.thread(lambda: test.expect(
            test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))

        test.make_call(phone_number=test.DESTINATION_ADDR)
        call_ring_line_listener_thread.join()

        test.log.step('c) For sradc measurements')
        measurement_ring_line_listener_thread = test.thread(lambda: test.expect(
            test.dut.devboard.wait_for('>URC:  RINGline: 1', test.RING_LINE_TIMEOUT)))
        test.execute_measurement()
        measurement_ring_line_listener_thread.join()

        test.log.step('d) For + creg (at+cops=2 and then at+cops=0)')
        test.expect(dstl_deregister_from_network(test.dut))

        test.expect(dstl_register_to_network(test.dut))

    def prepare_module(test, module):
        dstl_detect(module)
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_configure_sms_event_reporting(device=module, mode='2', mt='1'))
        test.delete_sms_from_memory(module)
        dstl_release_call(test.r1)

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def execute_measurement(test):
        for channel_nr in range(3):
            test.expect(dstl_start_periodic_adc_voltage_measurement(device=test.dut,
                                                                    channel=channel_nr,
                                                                    measurement_interval=
                                                                    test.INTERVAL_TIME_MS))
            test.expect(dstl_stop_periodic_adc_voltage_measurement(device=test.dut,
                                                                   channel=channel_nr))

    def make_call(test, phone_number: str = ''):
        test.expect(test.r1.at1.send_and_verify(f'atd{phone_number};'))

        # Wait for 2 call's rings
        test.expect(test.dut.at1.wait_for('RING.*RING'))
        test.expect(dstl_release_call(test.r1))


if "__main__" == __name__:
    unicorn.main()
