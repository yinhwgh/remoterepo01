#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091709.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.phonebook import phonebook_handle
import re

class Test(BaseTest):
    """
    TC0091709.001 - TpAtCpbwBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        test.log.step("1. Check commands without PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW?", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=", "\+CME ERROR"))

        test.log.step("2. Check valid commands after PIN input")
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.at1.send_and_verify,"AT+CPBS?", "OK", retry=3, sleep=2)
        sm_max = test.dut.dstl_get_pb_storage_max_location("SM")
        if not isinstance(sm_max, int):
            test.log.error("Fail to get max location for storage SM, useing 500 to continue following tests.")
            sm_max = 500
        # A DSTL may need be defined if response is different for other products
        expect_resp = f"\+CPBW: \(1-{sm_max}\),20,\(128,129,145,161,209,255\),14"
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=?", expect_resp))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1", "OK"))

        test.log.step("3. Check function of AT+CPBW")
        test.log.info("3.1 Write entries to SM storage")
        test.log.info("3.1.1 Clear SM phonebook")
        for i in range(2, sm_max+1):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i}", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\+CPBS: \"SM\",0,{sm_max}"))

        test.log.info("3.1.2 Write new entries to SM phonebook")
        pb_num = test.dut.sim.int_voice_nr
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{pb_num}\",129,\"testnumber1\"", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=2,\"{pb_num}\",129,\"testnumber2\"", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=3,\"{pb_num}\",129,\"testnumber3\"", "OK"))
        expect_read_resp = f"\+CPBR: 1,\"{pb_num}\",129,\"testnumber1\"\s+"
        expect_read_resp += f"\+CPBR: 2,\"{pb_num}\",129,\"testnumber2\"\s+"
        expect_read_resp += f"\+CPBR: 3,\"{pb_num}\",129,\"testnumber3\"\s+"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,3", expect_read_resp))
        for i in range(1,4):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i}"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\+CPBS: \"SM\",0,{sm_max}"))

        test.log.info("3.2 AT+CPBW command is not applicable to LD storage")
        error_resp = "\+CME ERROR: operation not allowed"
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"LD\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", "\+CPBS: \"LD\",\d+,\d+"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=1", error_resp))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{pb_num}\",129,\"testnumber1\"", error_resp))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"SM\"", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\+CPBS: \"SM\",0,{sm_max}"))

        test.log.step("4. Negative Tests")
        test.log.info("4.1 Write to max length + 1, min lenghth-1 location")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={sm_max+1},\"{pb_num}\",129,\"testnumber1\"", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=0,\"{pb_num}\",129,\"testnumber1\"", "\+CME ERROR: invalid index"))

        test.log.info("4.2 Write phone number with max length + 1")
        test.dut.at1.send_and_verify("AT+CPBW=?")
        query_format = "\+CPBW: \(.*?\),(\d+),\(.*\),(\d+)"
        match_format = re.search(query_format, test.dut.at1.last_response)
        if match_format:
            number_length = int(match_format.group(1))*2
            text_length = int(match_format.group(2))
        else:
            number_length = 20*2
            text_length = 14
        invalid_number = pb_num
        while len(invalid_number.replace('+','')) <= number_length:
            invalid_number += "8"
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{invalid_number}\",129,\"testnumber1\"", "\+CME ERROR: dial string too long"))

        test.log.info("4.3 Write text with max length + 1")
        text = "testnumber1"
        while len(text) <= text_length:
            text += "a"
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{pb_num}\",129,\"{text}\"", "\+CME ERROR: text string too long"))

        test.log.info("4.4 Write invalid type")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{pb_num}\",1290,\"testnumber1\"", "\+CME ERROR: invalid index"))

        test.log.info("4.5 Invalid commands")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=-1,\"{pb_num}\",129,\"testnumber1\"", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW", "\+CME ERROR: "))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW?", "\+CME ERROR: "))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS?", f"\+CPBS: \"SM\",0,{sm_max}"))
        
    def cleanup(test):
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))


if __name__ == "__main__":
        unicorn.main()
