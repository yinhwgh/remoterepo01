#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091781.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.configuration import functionality_modes
from dstl.sms import sms_functions
from dstl.sms import delete_sms
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.auxiliary.write_json_result_file import *


class TpAtCfunBasic(BaseTest):
    """
    TC0091781.001 -  TpAtCfunBasic
    Subscribers: 1 dut, 1 remote, 1 MCTest
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        set_result, test.original_scfg_meop_mode = test.dut.dstl_set_scfg_volatile_cfun_mode(1)
        test.expect(set_result, msg="Fail to setup MEopMode/CFUN to 1.")
        test.expect(test.dut.dstl_restart())
        test.sleep(5)

        test.valid_cfun_modes = []
        test.write_mem = 'SM'
        test.is_voice_call_supported = test.dut.dstl_is_voice_call_supported()

    def run(test):
        test.log.step("1. check commands with SIM PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.test_read_write_cfun_modes()

        test.log.step("2. check commands with PIN ready")
        test.expect(test.dut.dstl_enter_pin())
        test.test_read_write_cfun_modes()

        test.log.step("3. pin is required when switch back to normal mode")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))

        test.log.step("4. Write/Read Phonebook when CFUN: 1")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "CFUN: 1"))
        if test.is_voice_call_supported:
            test.pb_storage = test.dut.dstl_get_current_pb_storage()
            test.expect(test.dut.dstl_set_pb_memory_storage(test.write_mem))
            test.expect(test.dut.dstl_write_pb_entries(location=1, number=test.r1.sim.nat_voice_nr,
                                                       type='129', text='remote'))
            test.expect(test.dut.dstl_read_pb_entry(location=1, number=test.r1.sim.nat_voice_nr,
                                                    type='129', text='remote'))
        else:
            test.log.step(f"Skipped this step for {test.dut.project} who does not support voice call.")

        test.log.step("5. Setup voice call when CFUN: 1")
        if test.is_voice_call_supported:
            test.test_setup_voice_call()
        else:
            test.log.step(f"Project {test.dut.project} is configured as not support voice call, "
                          f"change to verify SMS instead.")
            test.test_send_sms()

        if test.dut.dstl_set_non_cyclic_sleep_mode():
            test.log.step("Step 6. cfun 0: module enters non-cyclic sleep mode,"
                          "establishing voice call and checking the CTS line (goes from low to high)")
            test.test_setup_voice_call(check_cts=True, cyclic_sleep=False)
        else:
            test.log.step("Step 6. cfun 0: run sim need commands got error \"SIM not inserted\"")
            test.dut.at1.send_and_verify("AT+CMEE=2", "OK")
            test.expect(test.dut.dstl_set_minimum_functionality_mode())
            test.log.info('*** Run commands that need PIN, "SIM not inserted" is returned. ***')
            pin_need_commands = ("AT+CEREG?", "AT+COPN", "AT+CGATT?", "AT+CMGF=1")
            for command in pin_need_commands:
                test.expect(test.dut.at1.send_and_verify(command, "\+(CMS|CME) ERROR: SIM not inserted",
                                                         wait_for="ERROR"))
            test.log.info("*** Run commands that do not need PIN, OK is returned. ***")
            pin_no_need_commands = ("AT+CGSN", "AT+CMEE?", "AT^SXRAT?", "AT+CCLK?")
            for command in pin_no_need_commands:
                test.expect(test.dut.at1.send_and_verify(command, "OK", wait_for="OK"))

        test.expect(test.dut.dstl_set_full_functionality_mode())

        if test.is_voice_call_supported:
            test.log.step("Step 10. cfun 4:  sim can be ready and reading from the phone-book is "
                          "possible, but the call is not supported")
            test.expect(test.dut.dstl_set_airplane_mode())
            test.expect(test.dut.dstl_enter_pin())
            test.sleep(8)
            test.expect(test.dut.dstl_read_pb_entry(location=1, number=test.r1.sim.nat_voice_nr,
                                                    type='129', text='remote'))
            test.expect(not test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
        else:
            test.log.step("Step 10. cfun 4: sim can be ready, sms can be written, but cannot be sent.")
            test.expect(test.dut.dstl_set_airplane_mode())
            test.expect(test.dut.dstl_enter_pin())
            test.sleep(5)
            test.expect(test.dut.dstl_write_sms_to_memory(sms_text='SMS can be written when cfun 4',
                                                          sms_format='text'))
            test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                                     expect="\+(CMS|CME) ERROR", wait_for="ERROR"))


        test.log.step("11. cfun 7: establishing the voice call and checking the CTS line "
                      "(temporary goes from low to high)")
        if 7 in test.valid_cfun_modes:
            test.expect(False, msg="Not implemented yet, please contact author.")
        else:
            test.log.info(f"Module does not support CFUN:7, skipped step.")

        test.log.step("12. cfun 9: establishing the voice call and checking the CTS line "
                      "(temporary goes from low to high)")
        if 9 in test.valid_cfun_modes:
            test.expect(False, msg="Not implemented yet, please contact author.")
        else:
            test.log.info(f"Module does not support CFUN:7, skipped step.")

    def cleanup(test):
        test.expect(test.dut.dstl_set_scfg_volatile_cfun_mode(test.original_scfg_meop_mode))
        test.expect(test.dut.dstl_set_full_functionality_mode(1))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        indexes = test.dut.dstl_list_occupied_sms_indexes()
        if indexes:
            test.expect(test.dut.dstl_delete_sms_message_from_index(indexes[0]))
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

    def test_read_write_cfun_modes(test):
        test.log.info("****** Test, Read commands of AT+CFUN ******")
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "[+]CFUN: 1"))
        test.valid_cfun_modes = test.dut.dstl_read_supported_functionality_modes()

        test.log.info(f"****** Read supported cfun modes: {test.valid_cfun_modes} ******")
        test.log.info(f"****** Loop for all valid CFUN modes ******")
        for valid_value in test.valid_cfun_modes:
            if valid_value != '1':
                test.expect(test.dut.dstl_set_functionality_mode(valid_value))
                test.sleep(2)
                test.expect(test.dut.dstl_set_full_functionality_mode())  # back to normal mode
                test.sleep(2)

        invalid_value_list = ["1a", "#", "255,1", "-1"]
        test.log.info(f"****** Test invalid value: {invalid_value_list}******")
        for invalid_value in invalid_value_list:
            test.expect(
                test.dut.at1.send_and_verify("AT+CFUN={}".format(invalid_value),
                                             "+CME ERROR: invalid index"))

    def test_send_sms(test):
        indexes = test.dut.dstl_list_occupied_sms_indexes()
        if indexes:
            test.expect(test.dut.dstl_delete_sms_message_from_index(indexes[0]))
        test.expect(test.dut.dstl_enable_sms_urc())
        test.expect(test.dut.dstl_send_sms_message(test.dut.sim.nat_voice_nr))
        test.expect(test.dut.at1.wait_for("\+CMTI:"))

    def test_setup_voice_call(test, check_cts=False, cyclic_sleep=False):
        if check_cts:
            test.expect(not test.dut.at1.connection.cts)
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
        test.sleep(2)
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc())
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        if check_cts:
            if not test.expect(test.dut.at1.connection.cts):
                test.expect(test.dut.dstl_exit_sleep_mode(cyclic=cyclic_sleep), critical=True,
                            msg="Fail to recover module from non-cyclic sleep mode.")


if __name__ == "__main__":
    unicorn.main()
