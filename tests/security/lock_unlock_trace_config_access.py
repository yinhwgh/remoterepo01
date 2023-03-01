#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0103400.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import spc_security
import os
import time

class Test(BaseTest):
    """
    Scripts may rely much on Unicorn's performance.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        test.spc_pwd = test.dut.dstl_get_spc_password()
        test.incorrect_pwd = test.spc_pwd[:-1] + str(9-int(test.spc_pwd[:-1]))
        test.log.info(f"Get SPC password : {test.spc_pwd}")
        test.log.info("******* Check if password is correct *******")
        unlocked = test.is_pwd_correct()
        if not unlocked:
            raise Exception("Cannot unlock trace with provided password")
        test.log.step("2. When incorrect <passwd> has been used,  5 sec delay for the first 3 attempts, 30s for the after")
        for i in range(1, 5):
            test.log.step(f"2.{i}.1.  Lock Debug access without password")
            test.lock_trace_config()
            delay = 30 if i > 3 else 5
            test.log.step(f"2.{i}.2   {delay} seconds delay after {i} failed attempts.")
            test.test_delay_with_attempts(i)

    def cleanup(test):
        test.unlock_trace_config()
    
    def lock_trace_config(test):
        test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"")
        if "UNLOCK" in test.dut.at1.last_response:
            test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\",LOCK")
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\^SSECUG: \"Factory/Debug\", LOCK"))
        elif "LOCK" in test.dut.at1.last_response:
            test.log.info("Trace configuration is already locked.")
        else:
            test.log.error("Unexpected response of AT^SSECUG=\"Factory/Debug\".")
    
    def unlock_trace_config(test):
        unlocked = test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "\"Factory/Debug\", UNLOCK")
        i = 1
        while not unlocked and i < 50:
            test.sleep(1)
            unlocked = test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "\"Factory/Debug\", UNLOCK")
            i += 1
        unlocked  &= test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", UNLOCK")
        if i>1:
            test.log.info(f"Used {i-1} seconds to unlock trace.")
        return unlocked
        
    def is_pwd_correct(test):
        test.lock_trace_config()
        unlocked = test.unlock_trace_config()
        return unlocked

    def test_delay_with_attempts(test, attempts):
        for i in range(1, attempts + 1):
            test.sleep(5)
            test.log.info("****** Unlock trace with incorrect pwd *****")
            test.expect(test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.incorrect_pwd}\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", LOCK"))
        test.log.info("****** Unlock trace with correct pwd within 5s, unlock failed *****")
        test.expect(test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", LOCK"))
        if i <= 3:
            test.log.info(f"****** For {i} failed attempts, unlock trace with correct pwd after 5s, unlock succeed *****") 
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", UNLOCK"))
        else:
            test.log.info(f"****** For {i} failed attempts, unlock trace with correct pwd after 5s, before 30s, unlock failed *****") 
            test.sleep(20)
            test.expect(test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", LOCK"))
            test.log.info(f"****** For {i} failed attempts, unlock trace with correct pwd after 30s, unlock succeed *****") 
            test.sleep(5)
            test.expect(test.unlock_trace_config())
            unlocked = test.dut.at1.send_and_verify(f"AT^SSECUG=\"Factory/Debug\",UNLOCK,\"{test.spc_pwd}\"", "OK")
            if unlocked:
                test.expect(unlocked)
                test.expect(test.dut.at1.send_and_verify("AT^SSECUG=\"Factory/Debug\"", "\"Factory/Debug\", UNLOCK"))
            else:
                test.log.error("Fail to unlock trace debug, will try more times.")
                test.expect(test.unlock_trace_config())





if __name__ == "__main__":
    unicorn.main()