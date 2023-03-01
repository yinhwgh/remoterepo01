# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091813.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module

import re


class Test(BaseTest):
    """
    TC0091813.001 -  TpCheckPbOnBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        pass

    def run(test):
        # Variables should be designed into DSTL if value are different for products
        clear_ld_atc = "AT+CPBS"
        non_exit_number = "0152340"
        r1_voice_nr_regexpr = test.r1.sim.nat_voice_nr
        if r1_voice_nr_regexpr.startswith('0'):
            r1_voice_nr_regexpr = '.*' + r1_voice_nr_regexpr[1:]

        test.log.step("1. Check commands with PIN locked")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("at+cpbs=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("at+cpbs?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("at+cpbs=\"ON\"", "\+CME ERROR: SIM PIN required"))

        test.log.step("2. Check if SIM is ready (and not busy)")
        test.expect(test.dut.dstl_enter_pin())

        test.log.step("3. Check command when PIN is ready")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", retry=3, sleep=2)
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=?", "ON"))
        if "LD" in test.dut.at1.last_response:
            with_ld = True
        else:
            with_ld = False
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBS=ON"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "ON"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=?"))
        match_resp = re.findall("\+CPBR: \(\d+-\d+\),(\d+),\d+", test.dut.at1.last_response)
        if match_resp:
            max_num_length = int(match_resp[0][0])
        else:
            test.log.error("Cannot read max number length from response, using 20 to continue tests.")
            max_num_length = 20

        test.log.step("4. Read empty phonebook: ON ")
        test.log.step("****** Clear phonebook: ALL ******")
        test.expect(test.dut.dstl_clear_all_pb_storage())
        max_location = test.dut.dstl_get_pb_storage_max_location("ON")
        test.expect(test.dut.at1.verify("CPBS: \"ON\",0,\d", test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_location}", "\+CME ERROR: not found"))

        test.log.step("5. Read phonebook: ON with invalid index")
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=0", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=-1", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=\"ON\"", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={max_location + 1}", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=0,\"01999990\",,\"Dummy0\"", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=151,\"0199999151\",,\"Dummy151\"",
                                                 "\+CME ERROR: invalid index"))

        test.log.step("6. Fill phonebook: ON")
        expect_resp = ""
        for i in range(1, max_location + 1):
            test.log.info(f"Writing the {i}th entry")
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i},\"01234000{i}\",,\"Own Number {i}\""))
            expect_resp += f"\+CPBR: {i},\"01234000{i}\",\d+,\"Own Number {i}\"\s+"
        test.expect(test.dut.at1.send_and_verify(F"AT+CPBR=1,{max_location}", expect_resp + "OK"))
        for i in range(1, max_location + 1):
            test.log.info(f"Reading the {i}th entry")
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={i}",
                                                     f"\+CPBR: {i},\"01234000{i}\",\d+,\"Own Number {i}\"\s+OK"))

        test.log.step("****** Clear phonebook: ALL ******")
        test.expect(test.dut.dstl_clear_select_pb_storage("ON"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "\"ON\",0,\d"))

        test.log.step("7. Write too long entry (sometimes one is possible - SIM dependent)")
        max_length_number = test.generate_number(max_num_length)
        expect_cpbr_resp = ""
        for i in range(1, max_location + 1):
            test.dut.at1.send_and_verify(f"AT+CPBW={i},\"{max_length_number * 2}\",,\"2x max number{i}\"", "OK|ERROR")
            if "CME ERROR: memory full" in test.dut.at1.last_response:
                test.log.info("Memory is full cannot write more items to phonebook, stop writing.")
                break
            elif "ERROR" in test.dut.at1.last_response:
                test.log.info("It is not possible to store twice the nlength on this SIM, strop writing.")
                break
            else:
                expect_cpbr_resp += f"\+CPBR: {i},\"{max_length_number * 2}\",\d+,\"2x max number{i}\"\s+"
        expect_cpbr_resp = "\+CME ERROR: not found" if expect_cpbr_resp == "" else expect_cpbr_resp
        test.expect(test.dut.at1.send_and_verify(F"AT+CPBR=1,{max_location}", expect_cpbr_resp + "OK"))

        test.log.step("8. Write and read own numbers out of iMaCS")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.dut.sim.nat_voice_nr}\",,\"NAT_VOICE_NR\""))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=2,\"{test.dut.sim.int_voice_nr}\",,\"INT_VOICE_NR\""))
        cpbr1_resp = f"\+CPBR: 1,\"{test.dut.sim.nat_voice_nr}\",129,\"NAT_VOICE_NR\"\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", cpbr1_resp + "OK"))
        int_data_nr = test.dut.sim.int_data_nr.replace('+', '\+')
        cpbr2_resp = f"\+CPBR: 2,\"{int_data_nr}\",145,\"INT_VOICE_NR\"\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=2", cpbr2_resp + "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_location}", cpbr1_resp + cpbr2_resp))

        test.log.step("9. Set ON numbers to R1 and setup voice call to R1")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.r1.sim.nat_voice_nr}\",,\"NAT_VOICE_NR\""))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=2,\"{test.r1.sim.int_voice_nr}\",,\"INT_VOICE_NR\""))
        cpbr1_resp = f"\+CPBR: 1,\"{test.r1.sim.nat_voice_nr}\",129,\"NAT_VOICE_NR\"\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", cpbr1_resp + "OK"))
        int_voice_nr = test.r1.sim.int_voice_nr.replace('+', '\+')
        cpbr2_resp = f"\+CPBR: 2,\"{int_voice_nr}\",145,\"INT_VOICE_NR\"\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=2", cpbr2_resp + "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{max_location}", cpbr1_resp + cpbr2_resp))
        if not test.dut.dstl_is_voice_call_supported():
            test.log.info("Module does not support voice call, skip step.")
        else:
            test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
            test.sleep(2)
            test.log.info("*** Check if call is active ***")
            ret = test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0")
            while "+CLCC: 1,0,3" in test.dut.at1.last_response:
                test.log.info("CLCC status does not change yet, try again after 1 second.")
                test.sleep(1)
                ret = test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0")
            if not ret:
                test.log.error("Unexpected CLCC response, please check if configurations are correct.")
                check_status_cmds = ["at+cpbs?", f"at+cpbr=1,{max_location}"]
                for cmd in check_status_cmds:
                    test.dut.at1.send_and_verify(cmd)
            else:
                # Reponse may be different for products or SIM operator, then DSTL should be designed
                expect_clcc_resp = f".*\"{r1_voice_nr_regexpr}\",161"
                test.log.info(f"Checking if response {expect_clcc_resp} in CLCC response")
                match_clcc = re.search(expect_clcc_resp, test.dut.at1.last_response)
                test.expect(match_clcc != None)
                # Viper does not support CPAS, if other products need check AT+CPAS, DSTL should be designed
                test.dut.dstl_release_call()
            test.log.info("*** Switch to phonebook: LD and check it ***")
            if with_ld:
                test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"LD\""))
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "LD"))
                test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", cpbr1_resp + "OK"))
            else:
                test.log.info("SIM card does not support LD storage, skip step.")

        test.log.step("****** Clear phonebook: ON ******")
        test.expect(test.dut.dstl_clear_select_pb_storage("ON"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "\"ON\",0,\d"))
        pass

    def cleanup(test):
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        pass

    def generate_number(test, number_length):
        number = ""
        for i in range(number_length):
            number += str(i % 10)
        return number


if __name__ == "__main__":
    unicorn.main()
