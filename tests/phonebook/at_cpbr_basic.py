#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091710.001

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
    TC0091710.001 - TpAtCpbrBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        test.log.step("1. Check commands without PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR?", "\+CME ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=", "\+CME ERROR"))

        test.log.step("2. Check valid commands after PIN input")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        test.attempt(test.dut.at1.send_and_verify, "AT+CPBR=?", "\+CPBR: \(\d+\-\d+\),\d+,\d+", retry=3, sleep=2)
        sm_max = test.dut.dstl_get_pb_storage_max_location("SM")
        test.log.info("Clear the first 10 entries")
        for i in range(1,11):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i}"))
        test.log.info("Write 3 entries into phone book")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=1,\"{test.dut.sim.int_voice_nr}\",145,\"Totti\""))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=2,\"{test.dut.sim.int_voice_nr}\",145,\"Canavaro\""))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBW=3,\"{test.dut.sim.int_voice_nr}\",145,\"Zambrotta\""))
        num_format = test.dut.sim.int_voice_nr.replace('+','\+')
        expect_resp_1 = f"\+CPBR: 1,\"{num_format}\",145,\"Totti\"\s+"
        expect_resp_2 = f"\+CPBR: 2,\"{num_format}\",145,\"Canavaro\"\s+"
        expect_resp_3 = f"\+CPBR: 3,\"{num_format}\",145,\"Zambrotta\"\s+"
        expect_resp = expect_resp_1 + expect_resp_2 + expect_resp_3 + "OK"
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,10", expect_resp))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", expect_resp_1))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=2", expect_resp_2))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=3", expect_resp_3))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=4", "\+CME ERROR: not found"))
        
        test.log.info("Delete added entries")
        for i in range(1,4):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i}"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1,10", "\+CME ERROR: not found"))
    
        test.log.step("3. Check invalid commands after PIN input")
        test.expect(test.dut.at1.send_and_verify("AT+CPBR", "\+CME ERROR: \w+"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=", "\+CME ERROR: \w+"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=-1", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=0", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR=1,{sm_max+1}", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={sm_max+1}", "\+CME ERROR: invalid index"))

    def cleanup(test):
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))


if __name__ == "__main__":
        unicorn.main()
