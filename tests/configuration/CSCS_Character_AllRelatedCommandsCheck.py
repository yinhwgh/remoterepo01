# responsible vaibhav.jain@thalesgroup.com
# Berlin
#TC0096101.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import *
from dstl.auxiliary import init
from dstl.security.lock_unlock_sim import *
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.configuration import character_set
from dstl.phonebook import phonebook_handle
from datetime import datetime
import time
import re


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):
        test.log.step("Detect module")
        test.dut.dstl_detect()

    def run(test):

        test.log.step("Get supported CSCS mode and check result : Test command")
        test.dut.dstl_get_supported_character_sets()

        test.log.step("Read existing CSCS mode and check result")
        test.dut.dstl_read_character_set()
        test.expect(test.dut.dstl_enter_pin())
        characters_ucs2 = test.dut.dstl_get_all_ucs2_characters()
        characters_gsm = test.dut.dstl_get_all_gsm_characters()

        test.log.step("Set CSCS mode to UCS2 and check result")
        test.expect(test.dut.dstl_set_character_set("UCS2"))
        test.sleep(2)

        test.log.step("Verifying UCS2 characters in phonebooks related commands")
        test.log.step(f"Setting phone book memory to {test.pb_mem}")
        test.sleep(3)
        mem_max_location = test.dut.dstl_get_pb_storage_max_location(test.pb_mem)

        pb_index = 1
        char_num = -1
        ucs2_cpbr_expect_resp = []
        gsm_cpbr_expect_resp = []
        start_check = False
        for ucs2_char in characters_ucs2:
            char_num += 1
            if pb_index == mem_max_location or char_num == len(characters_ucs2) - 1:
                start_check = True
            if ucs2_char != "":
                test.log.step(f"Write all special characters and all specific letters into the {test.pb_mem} phonebook in UCS2 character set")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={pb_index},\"{char_num}\",,\"{ucs2_char}\""))
                ucs2_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{ucs2_char}\"")
                gsm_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{characters_gsm[char_num]}\"")
                pb_index += 1

                """
                start_check: bool type. A switch controling whether finishing writing PB and need to check.
                It is added for checking PB like "FD" whose max location is shorter than total characters count.
                """

            if start_check == True and pb_index > 1:
                test.log.info(f"Phone book index is {pb_index}, character number is {char_num}")
                test.log.step("Check how many phonebook entries are supported and written in (AT+CPBR=?)")
                max_location = pb_index - 1
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=ucs2_cpbr_expect_resp,
                                       char_set="ucs2", set_charset=False)
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=gsm_cpbr_expect_resp, char_set="gsm")

                test.log.step(" Clear phonebook memory {test.pb_mem}")
                for i in range(max_location):
                    test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i + 1}"))
                # Init variables
                start_check = False
                ucs2_cpbr_expect_resp.clear()
                gsm_cpbr_expect_resp.clear()
                pb_index = 1
                test.expect(test.dut.dstl_set_character_set("UCS2"))

        test.dut.dstl_read_character_set()

    def cleanup(test):
        """
        # test cleanup - for example reboot module
        resp = test.dut.at1.send_and_verify("at+cfun=1,1")
        test.dut.at1.wait_for(".*SYSSTART.*|.*SYSLOADING.*", timeout = 90)
        """
        test.expect(test.dut.dstl_set_character_set("GSM"))
        pass

    def check_cpbr_result(test, read_index, expect_list, char_set='GSM', set_charset=True):
        # for gsm "127", character is not printable, need use binary data for verification
        test.log.info(f"***** Checking {test.pb_mem} phonebook with character set {char_set} *****")
        if char_set.lower()=="gsm":
            if set_charset == True:
                test.expect(test.dut.dstl_set_character_set("GSM"))
            actual_response = test.dut.at1.send_and_read_binary(f"AT+CPBR={read_index}")
            actual_response = str(actual_response, encoding="UTF-8")
        else:
            if set_charset == True:
                test.expect(test.dut.dstl_set_character_set("UCS2"))
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={read_index}"))
            actual_response = test.dut.at1.last_response
        # Remove ATC echo and OK and blank lines
        actual_list = actual_response.split('\n')[1:-2]
        error_message = ""
        index = 0
        # Checking actual list count with expect list count
        if len(expect_list) != len(actual_list):
            error_message = f"Actual item count {len(actual_list)} is different from expect item count {len(expect_list)}."
        # Checking each item in lists
        try:
            for expect in expect_list:
                if expect.strip() != actual_list[index].strip():
                    error_message += f"Actual row \"{actual_list[index].strip()}\" does not match with expected \"{expect}\"\n"
                index += 1
        except IndexError as e:
            test.log.error(f"Index Error: {index}")
        return error_message=="", error_message

if "__main__" == __name__:
    unicorn.main()
