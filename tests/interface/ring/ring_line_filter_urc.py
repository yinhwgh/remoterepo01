# responsible: mariusz.znaczko@globallogic.com
# location: Wroclaw
# TC0094204.002

import unicorn
from time import sleep
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_dev_board_urcs
from dstl.auxiliary.init import dstl_detect
from dstl.call.setup_voice_call import dstl_voice_call_by_number, dstl_release_call
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, \
    dstl_set_full_functionality_mode, dstl_set_factory_test_mode \
    , dstl_set_minimum_functionality_mode
from dstl.configuration.network_registration_status import dstl_set_network_registration_urc
from dstl.configuration.scfg_urc_ringline_config import dstl_activate_urc_ringline_to_local, \
    dstl_set_urc_ringline_active_time
from dstl.configuration.scfg_urc_ringline_filter import dstl_scfg_set_urc_ringline_filter
from dstl.hardware.configure_and_read_adc.start_periodic_adc_voltage_measurement import \
    dstl_start_periodic_adc_voltage_measurement
from dstl.hardware.configure_and_read_adc.stop_periodic_adc_voltage_measurement import \
    dstl_stop_periodic_adc_voltage_measurement
from dstl.hardware.set_real_time_clock import dstl_enable_automatic_time_zone_update, \
    dstl_disable_automatic_time_zone_update
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin,\
    dstl_deregister_from_network
from dstl.sms.configure_sms_text_mode_parameters import dstl_configure_sms_event_reporting, \
    dstl_set_sms_text_mode_parameters
from dstl.sms.send_sms_message import dstl_send_sms_message
from dstl.usim.sset_mode_control import dstl_set_sset_mode


class Test(BaseTest):
    """
    1. Set Ring Line Indicator Filter for SMS and Call related URCs (AT^SCFG="URC/Ringline/SelWUrc"
        ,"RING","+CMT")
    2. Set "URC/Ringline" to "local"
    3. Set "URC/Ringline/ActiveTime" to "2"
    4. Check if Ring line is activated with incomings URS's:
        a) For incoming SMS - CNMI
        b) For incoming voice call - RING
        c) For sradc measurements
        d) ^sysstart airplane mode
        e) ^sysstart factory test mode
        f) ^sysstart
        g) +CREG
        h) +CTZU
        i) ^SSIM READY
    5. Set Ring Line Indicator Filter for SMS URCs (AT^SCFG="URC/Ringline/SelWUrc","+CMT")
    6. Repeat step 4
    7. Set Ring Line Indicator Filter for SMS URCs (AT^SCFG="URC/Ringline/SelWUrc","RING")
    8. Repeat step 4
    9. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc","ALL")
        a) For incoming SMS - CNMI
        b) For incoming voice call - RING
        c) For sradc measurements
        d) ^sysstart airplane mode
        e) ^sysstart factory test mode
        f) ^sysstart
        g) +CREG
        h) +CTZU
        i) ^SSIM READY
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_register_to_network(test.dut)
        dstl_register_to_network(test.r1)
        dstl_turn_on_dev_board_urcs(test.dut)

    def run(test):
        variants = [['+CMT', 'RING'], ['+CMT', None], ['RING', None], ['ALL', None]]

        test.log.step('1. Set Ring Line Indicator Filter for SMS and Call related URCs (AT^SCFG="'
                      'URC/Ringline/SelWUrc","RING","+CMT")')
        test.log.info("Step will be executed after step 3.")

        test.log.step('2. Set "URC/Ringline" to "local"')
        test.expect(dstl_activate_urc_ringline_to_local(test.dut))

        test.log.step('3. Set "URC/Ringline/ActiveTime" to "2"')
        test.expect(dstl_set_urc_ringline_active_time(test.dut, 2))

        for config_variant in variants:
            if 'ALL' in config_variant:
                all_urc_to_trigger_ringline = True
                sms_to_trigger_ringline = True
                voice_call_to_trigger_ringline = True
                test.log.step('9. Set Ring Line Filter to "ALL" (AT^SCFG= "URC/Ringline/SelWUrc",'
                              '"ALL")')
            elif '+CMT' in config_variant and 'RING' not in config_variant:
                all_urc_to_trigger_ringline = False
                sms_to_trigger_ringline = True
                voice_call_to_trigger_ringline = False
                test.log.step('5. Set Ring Line Indicator Filter for SMS URCs (AT^SCFG="URC/'
                              'Ringline/SelWUrc","+CMT")')
            elif '+CMT' not in config_variant and 'RING' in config_variant:
                all_urc_to_trigger_ringline = False
                sms_to_trigger_ringline = False
                voice_call_to_trigger_ringline = True
                test.log.step('7. Set Ring Line Indicator Filter for SMS URCs (AT^SCFG="URC/'
                              'Ringline/SelWUrc","RING")')
            elif '+CMT' in config_variant and 'RING' in config_variant:
                all_urc_to_trigger_ringline = False
                sms_to_trigger_ringline = True
                voice_call_to_trigger_ringline = True
                test.log.info("Step 1. is executed here.")
            else:
                test.log.error("Wrong ringline filter conifg provided.")

            test.expect(dstl_scfg_set_urc_ringline_filter(test.dut,
                                                          param1=config_variant[0],
                                                          param2=config_variant[1],
                                                          exp_resp='.*OK.*'))
            dstl_set_network_registration_urc(test.dut, urc_mode=0)

            test.log.step('4a. Check if Ring line is activated for incoming SMS - CNMI')
            test.thread(test.check_ringline_activation,
                        sms_to_trigger_ringline, '>ASC0: +CMTI:', 60)
            test.send_sms_from_remote("Test SMS")
            test._threads_join()

            test.log.step('4b. Check if Ring line is activated for incoming Call - RING')
            test.thread(test.check_ringline_activation,
                        voice_call_to_trigger_ringline, ">ASC0: RING", 60)
            test.expect(dstl_voice_call_by_number(test.r1, test.dut, test.dut.sim.nat_voice_nr))
            dstl_release_call(test.r1)
            dstl_release_call(test.dut)
            test._threads_join()

            test.log.step('4c. Check if Ring line is activated for sradc measurements')
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: ^SRADC:', 15)
            dstl_start_periodic_adc_voltage_measurement(test.dut, channel=0,
                                                        measurement_interval=2000)
            test._threads_join()
            dstl_stop_periodic_adc_voltage_measurement(test.dut, channel=0)

            test.log.step('4d. Check if Ring line is activated for: ^sysstart airplane mode')
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: ^SYSSTART AIRPLANE MODE', 15)
            dstl_set_airplane_mode(test.dut)
            test._threads_join()

            test.log.step('4e. Check if Ring line is activated for: ^sysstart factory test mode')
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: ^SYSSTART FACTORY TEST MODE', 15)
            dstl_set_factory_test_mode(test.dut)
            test._threads_join()

            test.log.step('4f. Check if Ring line is activated for: ^sysstart')
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: ^SYSSTART', 15)
            dstl_set_full_functionality_mode(test.dut)
            test._threads_join()

            test.log.step('4g. Check if Ring line is activated for: +CREG')
            dstl_deregister_from_network(test.dut)
            dstl_set_network_registration_urc(test.dut, urc_mode=1)
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: +CREG:', 60)
            dstl_register_to_network(test.dut)
            test._threads_join()
            dstl_set_network_registration_urc(test.dut, urc_mode=0)

            test.log.step('4h. Check if Ring line is activated for: +CTZU')
            test.expect(dstl_enable_automatic_time_zone_update(test.dut))
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: +CTZU', 120)
            dstl_set_airplane_mode(test.dut)
            dstl_set_full_functionality_mode(test.dut)
            test._threads_join()
            test.expect(dstl_disable_automatic_time_zone_update(test.dut))

            test.log.step('4i. Check if Ring line is activated for: ^SSIM READY')
            dstl_set_sset_mode(test.dut, 'enable')
            dstl_set_minimum_functionality_mode(test.dut)
            dstl_set_full_functionality_mode(test.dut)
            test.thread(test.check_ringline_activation,
                        all_urc_to_trigger_ringline, '>ASC0: ^SSIM READY', 60)
            sleep(20)
            dstl_enter_pin(test.dut)
            test._threads_join()

    def cleanup(test):
        pass

    def send_sms_from_remote(test, message_to_sent: str) -> bool:
        dstl_set_sms_text_mode_parameters(test.dut, "17", "167", "0", "0")
        dstl_configure_sms_event_reporting(test.dut, "2", "1")
        return test.expect(dstl_send_sms_message(test.r1,
                                                 test.dut.sim.int_voice_nr, message_to_sent, 'Text',
                                                 set_sca=test.r1.sim.sca_int))

    def check_ringline_activation(test,
                                  expected_active: bool = False, urc: str = '', timeout: int = 10):
        if expected_active:
            if test.expect(test.dut_devboard.wait_for(expect=urc, timeout=timeout)):
                test.expect(test.dut_devboard.wait_for(expect=">URC:  RINGline: 1", timeout=10))
            else:
                test.log.error(f"Expected URC {urc} not found.")
        else:
            if test.expect(test.dut_devboard.wait_for(expect=urc, timeout=timeout)):
                test.expect(not test.dut_devboard.wait_for(expect=">URC:  RINGline: 1", timeout=10))
            else:
                test.log.error(f"Expected URC {urc} not found.")


if "__main__" == __name__:
    unicorn.main()
