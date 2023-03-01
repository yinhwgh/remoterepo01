#responsible: lei.chen@thalesgroup.com
#location: Dalian
# TC0091904.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.status_control import sind_parameters
from dstl.status_control import extended_indicator_control
from dstl.network_service import register_to_network
from dstl.configuration import set_sm20_mode
from dstl.status_control import configure_event_reporting
from dstl.auxiliary import check_urc
from dstl.call import setup_voice_call
from dstl.sms import sms_functions
from dstl.sms import sms_configurations
from dstl.status_control import check_sind_simdata
from dstl.status_control import check_sind_psinfo
from dstl.configuration import set_autoattach

import datetime

class Test(BaseTest):
    """
    TC0091904.001 - TpAtSindBasic
    Check implementation and functionality of AT^SIND
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.h3("Tests of 2 loops for without and with pin input.")
        for i in range(1,3):
            if i == 1:
                pin_status = "SIM PIN"
            else:
                test.expect(test.dut.dstl_register_to_network())
                pin_status = "READY"

            test.log.step(f"{i}. {pin_status}: Test and read commands can be executed correctly")
            test.attempt(test.dut.at1.send_and_verify,"at+cpin?", expect=pin_status, retry=5, sleep=2)
            test.sleep(5)
            expected_test_response_dict = test.dut.dstl_get_expected_sind_test_response_dict()
            expected_test_response_string = \
                test.dut.dstl_get_expected_sind_test_response_string(expected_test_response_dict)

            test.log.info(f"{i}.1. {pin_status}: Test command AT^SIND=?")
            test_matched = test.dut.at1.send_and_verify("at^sind=?", expect=expected_test_response_string)
            last_response = test.dut.at1.last_response
            if test_matched:
                test.log.info("Verify test response successfully")
                test.expect(test_matched)
            else:
                actual_test_response_dict = test.dut.dstl_get_sind_test_response_dict(response=last_response)
                test.expect(test.compare_dict(expected_test_response_dict, actual_test_response_dict))

            test.log.step(f"{i}.2 {pin_status}: Read command AT^SIND?")
            expected_read_response_dict = test.dut.dstl_get_expected_sind_parameter_value(
                                                              is_pin_locked=(pin_status=="SIM PIN"))
            actual_read_response_dict = test.dut.dstl_get_sind_read_response_dict()
            test.expect(test.compare_read_response_dict(expected_read_response_dict,
                                                        actual_read_response_dict,
                                                        expected_indicator_mode='0'))

            test.log.step(f"{i}.3 {pin_status}: Read + Write indicator mode for each indicator")
            for indicator in actual_read_response_dict:
                test.log.info(f"****** PIN status: {pin_status} - read + write indicator mode "
                              f"for {indicator} ******")
                expected_indicator_value = expected_read_response_dict[indicator] \
                                         if indicator in expected_read_response_dict else "undefined"
                if indicator == 'prov':
                    test.expect(test.dut.dstl_check_indicator_value(indicator, mode=1,
                                                                    indicator_value=expected_indicator_value))
                    test.expect(test.dut.dstl_disable_one_indicator(indicator, check_result=True,
                                                                   indicator_value=expected_indicator_value))
                    test.expect(test.dut.dstl_enable_one_indicator(indicator, check_result=True,
                                                                   indicator_value=expected_indicator_value))
                elif indicator == 'orpco':
                    test.expect(test.dut.dstl_check_indicator_value(indicator, mode=0,
                                                                    indicator_value=expected_indicator_value))
                else:
                    test.expect(test.dut.dstl_check_indicator_value(indicator, mode=0,
                                                                    indicator_value=expected_indicator_value))
                    test.expect(test.dut.dstl_enable_one_indicator(indicator, check_result=True,
                                                                   indicator_value=expected_indicator_value))
                    test.expect(test.dut.dstl_disable_one_indicator(indicator, check_result=True,
                                                                    indicator_value=expected_indicator_value))
                test.log.info(f"****** ****** ****** ****** ****** ****** ****** ****** ****** ****** ****** ******")

        test.log.info("************* Functionality tests for some of the sub-commands *************")
        actual_read_response_dict = test.dut.dstl_get_sind_read_response_dict()
        functionality_test_list=['service', 'sounder', 'message', 'sendsms', 'call', 'audio',
                                 'psinfo', 'simdriver', 'simdata', 'nitz']
        for func in functionality_test_list:
            if func in actual_read_response_dict:
                test.dut.dstl_configure_common_event_reporting(2,0,0,2,0)
                test.log.info(f"************* Functionality tests for subcommand:  {func} - Start *************")
                # call and audio test need remote module
                if "call" in func or "audio" in func or "sounder" in func:
                    test.dut.dstl_set_sm20_mode(0)
                    eval(f"test.sind_{func}_functionality(remote_module=test.r1)")
                elif "simdata" in func:
                    eval(f"test.dut.dstl_sind_{func}_functionality()")
                else:
                    eval(f"test.sind_{func}_functionality()")
                test.log.info(f"************* Functionality tests for subcommand:  {func} - End *************")
                test.log.info("******************************************************************************")

    def cleanup(test):
        test.expect(test.dut.dstl_disable_all_indicators())
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.dstl_enable_ps_autoattach())

    def compare_dict(test, expected_dict, actual_dict):
        matched = True
        if expected_dict and actual_dict:
            diff_keys_of_expected = {k:v for k,v in expected_dict.items() if k not in actual_dict}
            if diff_keys_of_expected:
                test.log.error(f"Parameters {diff_keys_of_expected} does not exist in actual response.")
                matched &= False
            diff_keys_of_actual = {k:v for k,v in actual_dict.items() if k not in expected_dict}
            if diff_keys_of_actual:
                test.log.error(f"Unexpected parameters {diff_keys_of_actual} was recieved in response.")
                matched &= False
            new_expected_dict = {k:v for k,v in expected_dict.items() if k not in diff_keys_of_expected}
            diff_value_of_expected = {k:f'expected {v}, actual {actual_dict[k]}' for k,v in
                                      new_expected_dict.items() if actual_dict[k] != v and
                                      not re.match(v, actual_dict[k])}
            if diff_value_of_expected:
                test.log.error("Mismatched parameter value {}".format(diff_value_of_expected))
                matched &= False
        elif not expected_dict:
            test.log.error("Expected dictionary is empty")
            matched = False
        else:
            test.log.error("Actual dictionary is empty")
            matched = False
        return matched
    
    def compare_read_response_dict(test, expected_dict, actual_dict, expected_indicator_mode='0'):
        expected_dict_with_mode = {}
        for k, v in expected_dict.items():
            if v:
                if k is 'prov':
                    expected_dict_with_mode[k] = f'1,{v}'
                else:
                    expected_dict_with_mode[k] = f'{expected_indicator_mode},{v}'
            else:
                expected_dict_with_mode[k] = f'{expected_indicator_mode}'

        return test.compare_dict(expected_dict_with_mode, actual_dict)

    def sind_service_functionality(test):
        test.dut.dstl_register_to_network()
        test.expect(test.dut.dstl_enable_one_indicator('service',check_result=True, indicator_value='[01]'))
        test.expect(test.dut.at1.send_and_verify("at+cops=2", expect="OK", timeout=30))
        test.expect(test.dut.at1.wait_for("CIEV: service,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('service', mode=1, indicator_value=0))
        test.expect(test.dut.at1.send_and_verify("at+cops=0", expect="OK", timeout=30))
        test.dut.dstl_check_urc("CIEV: service,1")
        test.expect(test.dut.dstl_check_indicator_value('service', mode=1, indicator_value=1))

    def sind_sounder_functionality(test, remote_module):
        test.dut.at1.send_and_verify("AT+CMER=2,0,0,2")
        test.dut.at1.send_and_verify("AT^SM20=0")
        test.dut.at1.send_and_verify("at^srtc=2", expect="OK")
        test.expect(test.dut.dstl_enable_one_indicator('sounder',check_result=True, indicator_value='[01]'))
        test.expect(test.dut.at1.send_and_verify("atd{};".format(remote_module.sim.nat_voice_nr),
                                               expect=".*", wait_for=".*"))
        test.expect(test.dut.at1.wait_for("CIEV: sounder,1", append=True, timeout=20))
        test.expect(test.dut.dstl_check_indicator_value('sounder', mode=1, indicator_value=1))
        test.sleep(2)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.at1.wait_for("CIEV: sounder,0", append=True, timeout=20))
        test.expect(test.dut.dstl_check_indicator_value('sounder', mode=1, indicator_value=0))

    def sind_message_functionality(test):
        indexes = test.dut.dstl_list_occupied_sms_indexes()
        if indexes:
            for i in indexes:
                test.dut.at1.send_and_verify(f"AT+CMGD={i}")
        test.expect(test.dut.dstl_set_preferred_sms_memory(None, "All"))
        test.expect(test.dut.at1.send_and_verify("at+cmgf=1"))
        test.expect(test.dut.dstl_enable_one_indicator('message',check_result=True, indicator_value='0'))
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.nat_voice_nr,
                                                   "this is a test sms for testing at^sind message - read"))
        test.log.info("SIND: message is 1 after revieving new message")
        test.expect(test.dut.at1.wait_for("CIEV: message,1", append=True))
        test.expect(test.dut.dstl_check_indicator_value('message', mode=1, indicator_value=1))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: message,1,1"))
        test.log.info("SIND: message is 0 after new message is read")
        test.expect(test.dut.dstl_list_sms_messages_from_preferred_memory('ALL'))
        test.expect(test.dut.at1.wait_for("CIEV: message,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('message', mode=1, indicator_value=0))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: message,1,0"))
        test.log.info("Sending another SMS")
        test.expect(test.dut.dstl_enable_sms_urc())
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.nat_voice_nr,
                                                   "this is a test sms for testing at^sind message - delete"))
        test.expect(test.dut.at1.wait_for("CIEV: message,1"))
        new_sms = test.dut.at1.wait_for('\+CMTI: ".*",\d+', append=True)
        new_sms_response = test.dut.at1.last_response
        test.expect(test.dut.dstl_check_indicator_value('message', mode=1, indicator_value=1))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: message,1,1"))
        test.log.info("SIND: message is 0 after new message is deleted")
        if new_sms:
            sms_index = re.findall('\+CMTI: ".*",(\d+)', new_sms_response)
            sms_index = sms_index[0]
            test.dut.at1.send_and_verify(f"AT+CMGD={sms_index}", "OK")
        test.expect(test.dut.at1.wait_for("CIEV: message,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('message', mode=1, indicator_value=0))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: message,1,0"))

    def sind_sendsms_functionality(test):
        test.expect(test.dut.dstl_delete_all_sms_messages())
        test.expect(test.dut.dstl_set_preferred_sms_memory(None, "All"))
        test.expect(test.dut.at1.send_and_verify("at+cmgf=1"))
        test.expect(test.dut.dstl_enable_one_indicator('sendsms',check_result=True, indicator_value='\d+'))
        send_sms_result = test.dut.dstl_send_sms_message(test.dut.sim.nat_voice_nr,
                                                         "this is a test sms for testing at^sind message - read",
                                                         return_number=True)
        sms_index = send_sms_result[1]
        test.log.info("SIND: message is 1 after revieving new message")
        test.expect(test.dut.at1.wait_for(f"CIEV: sendsms,0,{sms_index}"))
        test.expect(test.dut.dstl_check_indicator_value('sendsms', mode=1, indicator_value=f'0,{sms_index}'))
        test.log.info("SIND: message is 0 after new message is read, sendsms keeps")
        test.expect(test.dut.dstl_list_sms_messages_from_preferred_memory('ALL'))
        test.expect(test.dut.dstl_check_indicator_value('sendsms', mode=1, indicator_value=f'0,{sms_index}'))
        test.log.info("Sending another SMS")
        send_sms_result = test.dut.dstl_send_sms_message(test.dut.sim.nat_voice_nr,
                                                         "this is a test sms for testing at^sind message - delete",
                                                         return_number=True)
        sms_index = send_sms_result[1]
        test.expect(test.dut.at1.wait_for(f"CIEV: sendsms,0,{sms_index}"))
        test.expect(test.dut.dstl_check_indicator_value('sendsms', mode=1, indicator_value=f'0,{sms_index}'))
        test.log.info("SIND: message is 0 after new message is deleted, sendsms keeps")
        test.expect(test.dut.dstl_delete_all_sms_messages())
        test.expect(test.dut.dstl_check_indicator_value('sendsms', mode=1, indicator_value=f'0,{sms_index}'))

    def sind_call_functionality(test, remote_module):
        test.log.h3("Before call establishment, indicator value should be ^SIND: call,1,0")
        test.expect(test.dut.at1.send_and_verify("at^sind=call,1", "\^SIND: call,1,0"))
        test.expect(test.dut.dstl_enable_one_indicator('call', check_result=True, indicator_value='0'))
        test.expect(remote_module.at1.send_and_verify("atd{};".format(test.dut.sim.nat_voice_nr)))
        test.expect(test.dut.at1.wait_for("RING"))
        test.log.h3("Before answering call, indicator value should be ^SIND: call,1,0 ")
        test.expect(test.dut.dstl_check_indicator_value('call', mode=1, indicator_value=f'0'))
        test.log.h3("Establish call connection, CIEV: call,1 URC displays.")
        test.expect(test.dut.at1.send_and_verify("ata", expect="CIEV: call,1",
                                                 wait_for="CIEV: call,1", timeout=10))
        test.expect(test.dut.dstl_check_indicator_value('call', mode=1, indicator_value=f'1'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: call,1,1"))
        test.log.h3("Release call connection, CIEV: call,0 URC displays.")
        remote_module.dstl_release_call()
        test.expect(test.dut.at1.wait_for("CIEV: call,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('call', mode=1, indicator_value=f'0'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: call,1,0"))

    def sind_audio_functionality(test, remote_module):
        test.expect(test.dut.dstl_enable_one_indicator('audio', check_result=True, indicator_value='0'))
        test.log.info("*** MT call - start ***")
        test.expect(remote_module.at1.send_and_verify("atd{};".format(test.dut.sim.nat_voice_nr)))
        test.expect(test.dut.at1.wait_for("CIEV: audio,1"))
        test.expect(test.dut.dstl_check_indicator_value('audio', mode=1, indicator_value='1'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: audio,1,1"))
        remote_module.dstl_release_call()
        test.expect(test.dut.at1.wait_for("CIEV: audio,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('audio', mode=1, indicator_value='0'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: audio,1,0"))
        test.log.info("*** MT call - end ***")
        test.sleep(5)
        test.log.info("*** MO call - start ***")
        test.expect(test.dut.at1.send_and_verify("atd{};".format(remote_module.sim.nat_voice_nr),
                                               expect=".*", wait_for=".*"))
        test.expect(test.dut.at1.wait_for("CIEV: audio,1"))
        test.expect(test.dut.dstl_check_indicator_value('audio', mode=1, indicator_value='1'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: audio,1,1"))
        test.dut.dstl_release_call()
        test.expect(test.dut.at1.wait_for("CIEV: audio,0", append=True))
        test.expect(test.dut.dstl_check_indicator_value('audio', mode=1, indicator_value='0'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: audio,1,0"))
        test.log.info("*** MO call - end ***")

    def sind_psinfo_functionality(test):
        test.expect(test.dut.dstl_disable_ps_autoattach())
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=1, status='registered'))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=None, status='registered'))
        test.expect(test.dut.at1.send_and_verify("at+cops=2", "OK", timeout=30))
        test.expect(test.dut.dstl_check_urc_psinfo_status(status='unavailable', append=True))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=2, status='unavailable'))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=None, status='unavailable'))
        test.expect(test.dut.at1.send_and_verify("at+cops=0", "OK", timeout=60))
        test.expect(test.dut.dstl_check_urc_psinfo_status(status='registered', append=True))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=2, status='registered'))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=None, status='registered'))
        test.expect(test.dut.at1.send_and_verify("at+cgatt=1", "OK"))
        test.expect(test.dut.dstl_check_urc_psinfo_status(status='attached', append=True))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=2, status='attached'))
        test.expect(test.dut.dstl_check_sind_psinfo_status(mode=None, status='attached'))
        test.expect(test.dut.dstl_enable_ps_autoattach())

    def sind_simdriver_functionality(test):
        test.expect(test.dut.dstl_enable_one_indicator('simdriver', check_result=True, indicator_value='1'))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1", ".*OK.*"))
        test.expect(test.dut.at1.wait_for("CIEV: simdriver,0"))
        test.expect(test.dut.dstl_check_indicator_value('simdriver', mode=1, indicator_value='0'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: simdriver,1,0"))
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0", ".*OK.*"))
        test.expect(test.dut.at1.wait_for("CIEV: simdriver,1"))
        test.expect(test.dut.dstl_check_indicator_value('simdriver', mode=1, indicator_value='1'))
        test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND: simdriver,1,1"))

    def sind_nitz_functionality(test):
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        test.expect(test.dut.dstl_enable_one_indicator('nitz', check_result=True, indicator_value='"(00/00/00,00:00:00|)",\+00'))
        test.expect(test.dut.dstl_enter_pin())
        current_time = datetime.datetime.now()
        nitz_format = '"(\d{2}/\d{2}/\d{2},\d{2}:\d{2}:\d{2})",([+-])(\d+)'
        sind_nitz_format = nitz_format
        urc_display = test.expect(test.dut.at1.wait_for("\+CIEV: nitz," + nitz_format, timeout=60),
                                  msg="NITZ does not display or not in expected format.")
        if urc_display:
            last_response = test.dut.at1.last_response
            search_results = re.search("\+CIEV: nitz," + nitz_format, last_response)
            sind_nitz_format = f'"{search_results.group(1)}",{search_results.group(2)}' \
                               f'{search_results.group(3)}'.replace('+', '\+')

        sind_nitz = test.expect(test.dut.at1.send_and_verify("AT^SIND?",
                                                             f'\^SIND: nitz,1,{sind_nitz_format}'))
        if sind_nitz:
            search_results = re.search('\^SIND: nitz,1,' + nitz_format, test.dut.at1.last_response)
            time_zone = int(search_results.group(3))
            dif_sign = search_results.group(2)
            register_time = search_results.group(1)
            # Convert time from format "21/01/26,02:05:42" to "2021-01-26 02:05:42"
            f_register_time = '20' + register_time.replace('/', '-').replace(',', ' ')
            f_register_time = datetime.datetime.strptime(f_register_time, r"%Y-%m-%d %H:%M:%S")
            if dif_sign == '+':
                expect_time = current_time - datetime.timedelta(hours=time_zone / 4)
            else:
                expect_time = current_time + datetime.timedelta(hours=time_zone / 4)
            time_dif = (f_register_time - expect_time).seconds
            test.log.info("Time difference is {}".format(time_dif))
            test.expect(time_dif < 60, msg="Time delta is {}, greater than 60 seconds".format(time_dif))


if "__main__" == __name__:
    unicorn.main()