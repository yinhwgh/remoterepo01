#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0091748.001 TC0091749.001, TC0010801.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.configuration import character_set
from dstl.phonebook import phonebook_handle

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        """
        start_check: bool type. A switch controling whether finishing writing PB and need to check.
        It is added for checking PB like "ON" whose max location is shorter than total characters count.
        """
        test.expect(test.dut.dstl_enter_pin())
        characters_ucs2 = test.dut.dstl_get_all_ucs2_characters()
        characters_gsm = test.dut.dstl_get_all_gsm_characters()

        test.log.step(f"1. Setting phone book memory to {test.pb_mem}")
        test.sleep(3)
        mem_max_location = test.dut.dstl_get_pb_storage_max_location(test.pb_mem)

        test.log.step("2. Set TE character to UCS2 and check result")
        test.expect(test.dut.dstl_set_character_set("UCS2"))
        test.sleep(2)
        
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
                test.log.step(f"3. Write all special characters and all specific letters into the {test.pb_mem} phonebook in UCS2 character set")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={pb_index},\"{char_num}\",,\"{ucs2_char}\""))
                ucs2_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{ucs2_char}\"")
                gsm_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{characters_gsm[char_num]}\"")
                pb_index += 1
            if start_check == True and pb_index > 1:
                test.log.info(f"Phone book index is {pb_index}, character number is {char_num}")
                test.log.step(f"4. Check how many phonebook entries are supported and written in (AT+CPBR=?)")
                max_location = pb_index - 1
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=ucs2_cpbr_expect_resp, char_set="ucs2", set_charset=False)
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=gsm_cpbr_expect_resp, char_set="gsm")

                test.log.step(f"5. Clear phonebook memory {test.pb_mem}")
                for i in range(max_location):
                    test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i+1}"))
                # Init variables
                start_check = False
                ucs2_cpbr_expect_resp.clear()
                gsm_cpbr_expect_resp.clear()
                pb_index = 1
                test.expect(test.dut.dstl_set_character_set("UCS2"))

        pb_index = 1
        char_num = -1
        ucs2_cpbr_expect_resp = []
        gsm_cpbr_expect_resp = []
        start_check = False
        test.log.step(f"6. Write all special characters and all specific letters into the {test.pb_mem} phonebook in GSM character set")
        test.expect(test.dut.dstl_set_character_set("GSM"))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS?', expect='\+CSCS: "GSM"'))
        for gsm_char in characters_gsm:
            char_num += 1
            if pb_index == mem_max_location or char_num == len(characters_gsm) - 1:
                start_check = True
            if gsm_char != 255:
                if isinstance(gsm_char,int):
                    gsm_char = chr(gsm_char)
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={pb_index},\"{char_num}\",,\"{gsm_char}\""))
                gsm_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{gsm_char}\"")
                ucs2_cpbr_expect_resp.append(f"+CPBR: {pb_index},\"{char_num}\",129,\"{characters_ucs2[char_num]}\"")
                pb_index += 1

            if start_check == True and pb_index > 1:
                test.log.info(f"Phone book index is {pb_index}, character number is {char_num}")
                test.log.step(f"7. Read out ON phonebook (AT+CPBR=1, x x=Maximum location number)")
                max_location = pb_index-1
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=gsm_cpbr_expect_resp, char_set="gsm", set_charset=False)
                test.check_cpbr_result(read_index=f"1,{max_location}", expect_list=ucs2_cpbr_expect_resp, char_set="ucs2")

                test.log.step(f"8. Clear phonebook memory {test.pb_mem}")
                for i in range(max_location):
                    test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i+1}"))  
                # init variables
                start_check = False
                ucs2_cpbr_expect_resp.clear()
                gsm_cpbr_expect_resp.clear()
                pb_index = 1
                test.expect(test.dut.dstl_set_character_set("GSM"))
                test.expect(test.dut.at1.send_and_verify('AT+CSCS?', expect='\+CSCS: "GSM"'))
   
    def cleanup(test):
        test.expect(test.dut.dstl_set_character_set("GSM"))
        test.dut.dstl_clear_select_pb_storage(test.pb_mem)

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


if '__main__' == __name__:
    unicorn.main()
