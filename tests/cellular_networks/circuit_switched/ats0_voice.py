#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0092613.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.call import setup_voice_call

import random

class Test(BaseTest):
    '''
    TC0092613.001 - TpAtS0Voice
    Intention: Basic AtS0 test for Voice calls only.
    Subscriber: 2, dut and remote module
    '''
    def setup(test):
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.step("1. command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", "\d{3}\s+OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0=5", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0=0", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0=?", "ERROR"))

        test.log.step("2. Read command and write command with pin authentication")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("ATS0?", "\d{3}\s+OK"))
        valid_values = ("1", "255", "0")
        for value in valid_values:
            expect = "{prefix0}{value}\s+OK".format(prefix0="0"*(3-len(value)), value=value)
            test.expect(test.dut.at1.send_and_verify(f"ATS0={value}", "OK"))
            test.expect(test.dut.at1.send_and_verify("ATS0?", expect))
        
        test.log.step("3. Test : Invalid parameters")
        invalid_values = ("-1", "256", "?")
        for value in invalid_values:
            test.expect(test.dut.at1.send_and_verify(f"ATS0={value}", "ERROR"))
            # Invalid commands should not change ATS0 value
            test.expect(test.dut.at1.send_and_verify("ATS0?", "000\s+OK"))
        
        test.log.step("4. Test: Functionality test")
        # number should less than 7 accroding to comments in Pegasus that CALL will be timeout after 6 RINGs in Polish network
        ring_num=5
        test.expect(test.dut.at1.send_and_verify(f"ATS0={ring_num}", "OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", f"00{ring_num}\s+OK"))
        test.execute_mt_call_and_check_rings(ring_num)

        test.log.step("5. check setting after restart without and with PIN")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.dut.at1.send_and_verify("AT+CMEE=2")
        test.expect(test.dut.at1.send_and_verify("ATS0?", "000\s+OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0=3", "ERROR"))
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.at1.send_and_verify("ATS0=3", "OK"))
        test.expect(test.check_ats0_value("003"))
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.at1.send_and_verify("ATS0=7", "OK"))
        test.expect(test.check_ats0_value("007"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))
        test.expect(test.dut.at1.send_and_verify("ATS0=222", "OK"))
        test.expect(test.check_ats0_value("222"))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.check_ats0_value("007"))
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.at1.send_and_verify,"ATZ", retry=3, sleep=1)
        test.expect(test.check_ats0_value("007"))
        test.expect(test.dut.at1.send_and_verify("ATS0=77", "OK"))
        test.expect(test.check_ats0_value("077"))
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.at1.send_and_verify("ATZ"))
        test.expect(test.check_ats0_value("007"))

        test.log.step("6. Check Number of Rings after Restart")
        test.execute_mt_call_and_check_rings(ring_num=6)

        test.log.step("7. Set Back To Default Values")
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.check_ats0_value("000"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))
        test.attempt(test.dut.dstl_release_call, retry=3, sleep=2)
        test.attempt(test.r1.dstl_release_call, retry=3, sleep=2)
    
    def check_ats0_value(test, exp_value):
        match = test.dut.at1.send_and_verify("ATS0?",f"{exp_value}\s+OK")
        match &= test.dut.at1.send_and_verify("AT&V", f"S0:{exp_value}.*OK")
        return match

    def execute_mt_call_and_check_rings(test, ring_num):
        test.log.info(f"****** Incomming VOICE call start - check for {ring_num} RINGs ******")
        ring_num = str(ring_num)
        test.expect(test.dut.at1.send_and_verify("AT+CRC=0", "OK"))
        test.expect(test.r1.at1.send_and_verify(f"ATD{test.dut.sim.int_voice_nr};"))
        test.expect(test.dut.at1.wait_for("(RING\s+){" + ring_num + "}"))
        test.expect(test.dut.at1.send_and_verify("ATA"))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", ".*\+CLCC: 1,1,0,0,0.*OK.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", ".*\+CLCC: 1,0,0,0,0.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CHUP"))
        test.r1.at1.wait_for(".*NO CARRIER.*", timeout=5)
        


if "__main__" == __name__:
    unicorn.main()

