#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0091803.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.call import setup_voice_call
from random import randint

class Test(BaseTest):
    """
    TC0091803.001 -  TpAtClipBasic
    Intention:
        This procedure provides the possibility of basic tests for the test and write command of +CLIP.:
        - check command without and with PIN
        - check all parameters and also with invalid values
        - check functionality by performing MT-voice call
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        test.dut.dstl_restart()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()

    def run(test):
        test.log.info("*** 1. test without pin ***")
        test_resp_before_pin = "\+CME ERROR: SIM PIN required"
        read_resp_before_pin = "\+CME ERROR: SIM PIN required"
        write_resp_before_pin = "\+CME ERROR: SIM PIN required"
        read_resp_after_pin = "\+CLIP: 0,1\s+OK"
        test_resp_after_pin = "\+CLIP: \(0-1\)\s+OK"
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=?", test_resp_before_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", read_resp_before_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", read_resp_before_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=0", read_resp_before_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", read_resp_before_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", read_resp_before_pin))

        test.log.info("*** 2. test with pin ***")
        test.expect(test.dut.at1.send_and_verify("AT+CREG=1"))
        # including AT+CMEE=2
        test.expect(test.dut.dstl_enter_pin()) 
        test.expect(test.dut.at1.wait_for("\+CREG: 1"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CLIP=?", test_resp_after_pin, retry=5, sleep=2)
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", read_resp_after_pin))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=0"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 0,1\s+OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=1"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 1,1\s+OK"))

        test.log.step("*** 3. Functionality test: call from second party ***")
        slip_urc = f"\+CLIP: \"{test.r1.sim.nat_voice_nr}\",129,,,,0"
        test.check_clip_urc_on_voice_call(slip_urc)

        test.log.step("*** 4. Invalid commands ***")
        error_msg = ""
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=2", "\+CME ERROR: invalid index"))
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=-1", "\+CME ERROR: invalid index"))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CLIP=0"))
        test.dut.at1.send_and_verify("AT+CLIP?", "\+CLIP: 0,[012]")

    def check_clip_urc_on_voice_call(test, clip_urc):
        """
        For voice call, clip urc appears after every RING.
        For data call and fax call, clip URC only appears once
        """
        mt_number = test.dut.sim.nat_voice_nr
        test.r1.at1.send_and_verify(f"ATD{mt_number};")
        no_carrier = False
        while not no_carrier:
            if test.dut.at1.wait_for("RING", timeout=20):
                if test.dut.at1.wait_for(clip_urc, timeout=6):
                    test.log.info(f"Found URC {clip_urc} in response.")
                    test.dut.dstl_check_voice_call_status_by_clcc(is_mo=False, expect_status='4')
                    test.sleep(0.2)
                    no_carrier = "NO CARRIER" in test.dut.at1.last_response
                else:
                    if "NO CARRIER" in test.dut.at1.last_response or "NO ANSWER" in test.r1.at1.last_response:
                        test.log.info("Call is ended.")
                        no_carrier = True
                    else:
                        test.log.error(f"Cannot find URC {clip_urc} in response")
            elif "NO CARRIER" in test.dut.at1.last_response:
                no_carrier = True
            else:
                test.log.error("Module is not Rung.")
                break
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
    
if '__main__' == __name__:
    unicorn.main()


