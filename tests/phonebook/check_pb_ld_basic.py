# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091812.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.auxiliary import generate_data
import re


class Test(BaseTest):
    """
    TC0091812.001 -  TpCheckPbLdBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        pass

    def run(test):
        # not necessary for VIPER01+02, see VPR02-909 and IPIS100358124: not to fix!
        if test.dut.project is 'VIPER' and int(test.dut.step) <= 2:
            test.dut.at1.send_and_verify(f'AT+CPBS=?', ".*O.*")
            if '"LD"' not in test.dut.at1.last_response:
                test.log.warning("LD-PB not implemented, defect was accepted, see VPR02-909 and IPIS100358124:"
                                 " not to fix - ABORT now with PASSed")
                test.expect(True)
                return

        # Variables should be designed into DSTL if value are different for products
        ld_storage = "LD"
        clear_ld_atc = "AT+CPBS"
        non_exit_number = "0152340"
        test.log.step("1. Check if SIM is ready (and not busy)")
        test.expect(test.dut.dstl_enter_pin())

        test.log.step("2. Check command when PIN is ready")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", retry=3, sleep=2)
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=?", ld_storage))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS={ld_storage}"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", ld_storage))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=?"))
        match_resp = re.findall("\+CPBR: \((\d+)-(\d+)\),(\d+),(\d+)", test.dut.at1.last_response)
        if match_resp:
            # min_index = int(match_resp[0][0])
            max_index = int(match_resp[0][1])
            max_num_len = int(match_resp[0][2])
            max_name_len = int(match_resp[0][3])
        else:
            test.log.error("Cannot read minimum index and maximum index number from response of AT+CPBR=?,\
                using default value to continue test: min_index-1, max_index-10, max_num_len=20, max_num_len=14")
            # min_index = 1
            max_index = 10
            max_num_len = 20
            max_name_len = 14
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=", "\+CME ERROR"))

        test.log.step("3. Read empty phonebook: LD ")
        test.log.info("Clear LD phonebook entries")
        test.expect(test.dut.at1.send_and_verify(clear_ld_atc))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",0,{max_index}"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_index}", "\+CME ERROR: not found"))

        test.log.step("4. Read phonebook: LD with invalid index")
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=0", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=-1", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={ld_storage}", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={max_index + 1}", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=0,{max_index}", "\+CME ERROR: invalid index"))

        test.log.step("5. Fill phonebook: LD")
        for i in range(1, max_index + 1):
            test.log.info(f"Writing the {i}th entry")
            test.expect(test.dut.at1.send_and_verify(f"ATD{non_exit_number}{max_index - i};",
                                                     expect='OK|ERROR'))
            test.sleep(0.2)
            test.dut.at1.send_and_verify("AT+CEER")
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",{max_index},{max_index}"))

        expect_resp = ""
        for i in range(1, max_index + 1):
            test.log.info(f"Reading the {i}th item in LD")
            expect = f"\+CPBR: {i},\"{non_exit_number}{i - 1}\",129,\"\"\s+"
            expect_resp += expect
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={i}", expect + "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_index}", expect_resp + "OK"))

        test.log.step("6. Clear phonebook: LD")
        test.expect(test.dut.at1.send_and_verify(clear_ld_atc))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",0,{max_index}"))

        test.log.step("7. Check if identical entries are saved")
        # DSTL may be needed if different products behave not the same
        for i in range(1, 3):
            test.expect(test.dut.at1.send_and_verify(f"ATD{non_exit_number};"))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",2,{max_index}"))
        expect_resp = ""
        for i in range(1, 3):
            expect = f"\+CPBR: {i},\"{non_exit_number}\",129,\"\"\s+"
            expect_resp += expect
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={i}", expect + "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_index}", expect_resp + "OK"))

        test.log.step("8. Clear phonebook: LD")
        test.expect(test.dut.at1.send_and_verify(clear_ld_atc))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",0,{max_index}"))

        test.log.step("9. Check if data call number is stored or not")
        test.log.step("10. Clear phonebook: LD")
        support_data_call = test.dut.dstl_is_data_call_supported()
        if support_data_call:
            test.log.error("Data call test was not implemented.")
        else:
            test.log.info(f"{test.dut.product} does not support data call, skip step 9 & 10.")

        test.log.step("11. Check behaviour of dialing number with different length")
        dial_number_length = 2 * max_num_len + 5
        dial_number = test.generate_number(prefix=non_exit_number, number_length=dial_number_length)
        test.log.info(f"11.1 Try with dialing string with length of <max number length - 1> : {max_num_len - 1}")
        test.dial_number_and_check_ld(max_index, dial_number[:max_num_len - 1], "")
        test.log.info(f"11.2 Try with dialing string with length of <max number length> : {max_num_len}")
        test.dial_number_and_check_ld(max_index, dial_number[:max_num_len], test.dut.at1.last_response)
        test.log.info(f"11.3 Try with dialing string with length of <max number length+1> : {max_num_len + 1}")
        last_cpbr_response = test.dut.at1.last_response
        test.expect(test.dut.at1.send_and_verify(f"ATD{dial_number[:max_num_len + 1]};", "OK|ERROR"))
        if "OK" in test.dut.at1.last_response:
            test.log.info("OK in response, Product can dial number with longer length")
            test.hang_up_call()
            expect_resp = f"\+CPBR: 1,\"{dial_number[:max_num_len + 1]}\",\d+,\".*?\"\s+"
            expect_resp = test.parse_expect_cpbr(last_cpbr_response, expect_resp)
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_index}", expect_resp + "OK"))
            test.log.info(
                f"11.4 Try with dialing string with length of <max number length*2 - 1> : {max_num_len * 2 - 1}")
            test.dial_number_and_check_ld(max_index, dial_number[:max_num_len * 2 - 1], test.dut.at1.last_response)
            test.log.info(f"11.5 Try with dialing string with length of <max number length*2> : {max_num_len * 2}")
            test.dial_number_and_check_ld(max_index, dial_number[:max_num_len * 2], test.dut.at1.last_response)
            test.log.info(f"11.6 Try with dialing string with length of <max number length*2+1> : {max_num_len * 2 + 1}"
                          f", record will not be saved to LD")
            last_cpbr_response = test.dut.at1.last_response
            test.expect(test.dut.at1.send_and_verify(f"ATD{dial_number[:max_num_len * 2 + 1]};"))
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_index}", last_cpbr_response))
        test.hang_up_call()

        test.log.step("12. Clear phonebook: LD")
        test.expect(test.dut.at1.send_and_verify(clear_ld_atc))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",0,{max_index}"))

        test.log.step("13. check behaviour of attempt to write a phonebook entry wtih at+cpbw")
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1,\"12345\",129,\"A\"", "\+CME ERROR: operation not allowed"))
        random_name = generate_data.dstl_generate_data(max_name_len)
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=2,\"23456789012345678901\",129,\"{random_name}\"",
                                                 "\+CME ERROR: operation not allowed"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,2", "\+CME ERROR: not found"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\"{ld_storage}\",0,{max_index}"))

    def cleanup(test):
        # test.expect(test.dut.dstl_restart())
        # test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        pass

    def generate_number(test, prefix, number_length):
        """Append 0123456789 to original number until total length matches with expected"""
        append_length = number_length - len(prefix)
        number = prefix
        for i in range(append_length):
            number += str(i % 10)
        return number

    def make_mo_call(test, number, expect="OK"):
        test.expect(test.dut.at1.send_and_verify(f"ATD{number};", expect))
        test.sleep(0.2)
        pass

    def hang_up_call(test):
        test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
        pass

    def dial_number_and_check_ld(test, read_count, number, last_cpbr_response):
        test.make_mo_call(number)
        test.hang_up_call()
        expect_resp = f"\+CPBR: 1,\"{number}\",\d+,\".*\"\s+"
        # Append new expect message to original with original index increased
        expect_resp = test.parse_expect_cpbr(last_cpbr_response, expect_resp)
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{read_count}", expect_resp + "OK"))
        pass

    def parse_expect_cpbr(test, last_cpbr_response, new_cpbr_item):
        expect_resp = new_cpbr_item
        items = re.findall("(\+CPBR: (\d+),\".*?\",\d+,\".*?\")\s+", last_cpbr_response)
        if items:
            for item in items:
                index = int(item[1])
                temp_expect = item[0].replace(f"+CPBR: {index}", f"\+CPBR: {index + 1}")
                expect_resp += temp_expect + "\s+"
        return expect_resp


if __name__ == "__main__":
    unicorn.main()
