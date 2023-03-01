#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091706.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import set_sim_waiting_for_pin1
import re

class AtCnumFunc(BaseTest):
    """
    TC0091706.001 - TpAtCnumBasic    
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_set_sim_waiting_for_pin1())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        
    def run(test):
        test.log.step("1. Check commands without PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CNUM", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM?", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=1", "\+CME ERROR"))

        test.log.step("2. Check valid commands after PIN input")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.attempt(test.dut.at1.send_and_verify,"AT+CNUM", "OK", retry=3, sleep=2)
        cnum_resp = test.dut.at1.last_response.split('\r\n')[-1]
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=?", "OK"))
        on_used,on_total = test.get_on_capacities()
        test.expect(test.dut.at1.send_and_verify("AT+CNUM", cnum_resp))

        test.log.step("3. Check invalid commands after PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CNUM?", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=on", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=1", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CNUM=255", "\+CME ERROR"))

        test.log.step("4. Functionality Test")
        own_numbers = ["123456", "98765", "+4911223344", "545352", "132475", "+4388669988", "79188658"]
        own_number_types = ["129", "129", "145", "129", "129", "145", "129"]
        cpbr_entries = ""
        cnum_entries = ""
        test.log.info("Writing phonebook to ON storage")
        for i in range(int(on_total)):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i+1},\"{own_numbers[i]}\",{own_number_types[i]},\"Own Number {i+1}\""))
            check_number = own_numbers[i].replace("+", "\+")
            cpbr_entries += f"\+CPBR: {i+1},\"{check_number}\",{own_number_types[i]},\"Own Number {i+1}\"\s+"
            cnum_entries += f"\+CNUM: \"Own Number {i+1}\",\"{check_number}\",{own_number_types[i]}\s+"
        test.log.info("Index over max ON storage cannot be written to phone book")
        error_index = int(on_total) + 1
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={error_index},\"{own_numbers[error_index]}\",{own_number_types[error_index]},\"ERROR INDEX\"", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"CPBS: \"ON\",{on_total},{on_total}"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{on_total}", cpbr_entries))
        test.expect(test.dut.at1.send_and_verify(f"AT+CNUM", cnum_entries))
        test.log.info("Delete entries from phone book.")
        for i in range(int(on_total)):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i+1}", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CNUM", "^\s*AT\+CNUM\s*OK\s*$"))
        
    def cleanup(test):
        pass
    
    def get_on_capacities(test):
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"ON\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "OK"))
        match_format = re.search("\+CPBS: \"ON\",(\d+),(\d+)", test.dut.at1.last_response)
        if match_format:
            used = match_format.group(1)
            total = match_format.group(2)
        else:
            test.log.error("Unexpected response of AT+COPS?")
            used="unknown"
            total="unknown"
        test.log.info(f"Found total is {total},used is {used}.")
        return used, total

if __name__ == "__main__":
        unicorn.main()
