# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0105159.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.status_control import extended_indicator_control
from dstl.status_control import check_dtmf_urc
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call

import random

class Test(BaseTest):
    """
    TC0105159.002 - sind_dtmf_atd_function
    Intention:
    Test case to check DTMF URC popup by atdxxxpxxx;
    
    Description:
    1.Restart two modules with sim card inserted
    2. Make two modules register on network
    3. Enabled sind DTMF URC on DUT side
    at^sind="dtmf",1
    4. Make an on-going call from remote to DUTby atdxxxp123;
    5. Verify on DUT side except RING URC popup, also DTMF URC show as below
    +CIEV: "dtmf",123,1
    note: if multi DTMF chars does not support, may be only one char is shown
    +CIEV: "dtmf",1,1
    6. Disable DTMF URC on DUT side
    7. Repeat step4 and verify on DUT side no DTMF URC popup 
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
    
    def run(test):
        test.log.step("1. Restart two modules with sim card inserted")
        test.expect(test.dut.dstl_restart())
        test.expect(test.r1.dstl_restart())

        test.log.step("2. Make two modules register on network")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())

        test.log.step("3. Enabled sind DTMF URC on DUT side")
        test.expect(test.dut.dstl_enable_one_indicator("dtmf", False))

        test.log.step("4. Make an on-going call from remote to DUT by atdxxxp123;")
        test.log.info("Set random tone duration.")
        duration = random.randint(0, 256)
        test.log.info(f'Generated random duration value is {duration}.')
        test.log.warning('Not to fix for Viper: IPIS100334609: Make a call to PLS83-J by '
                         '"atdxxxpxxx"(DTMF duration>100), URC not only display one time and '
                         'release the call automatically')
        test.expect(test.dut.at1.send_and_verify(f"AT+VTD={duration}"), "OK")
        test.expect(test.dut.at1.send_and_verify(f"AT+VTD?"), "OK")
        dtmfs_str = '0123456789*#ABCD'
        call_succeed = test.r1.dstl_voice_call_by_number(test.dut, f"{test.dut.sim.nat_voice_nr}p{dtmfs_str}", "OK")
        if not call_succeed:
            msg = "Remote module may not support all dtmfs in '0123456789*#ABCD', test with '0123456789*#'"
            test.expect(call_succeed, msg=msg)
            dtmfs_str = '0123456789*#'
            call_succeed = test.r1.dstl_voice_call_by_number(test.dut, f"{test.dut.sim.nat_voice_nr}p{dtmfs_str}", "OK")
        if call_succeed:
            test.log.step("5. Verify on DUT side except RING URC popup, also DTMF URC show as below")
            test.expect(test.dut.dstl_check_dtmf_atd_urc(dtmfs_str))
            test.expect(test.dut.dstl_release_call())

            test.log.step("6. Disable DTMF URC on DUT side")
            test.expect(test.dut.dstl_disable_one_indicator("dtmf", True))

            test.log.step("7. Repeat step4 and verify on DUT side no DTMF URC popup")
            test.expect(test.r1.dstl_voice_call_by_number(test.dut, f"{test.dut.sim.nat_voice_nr}P{dtmfs_str}", "OK"))
            test.log.info("Monitor for 1 minute.")
            test.sleep(60)
            response = test.dut.at1.read(append=True)
            test.expect("+CIEV: dtmf" not in response)
            test.expect(test.dut.dstl_release_call())
        else:
            test.expect(call_succeed, msg="Fail to call with dtmfs, skip next tests.")

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.dstl_disable_one_indicator("dtmf", True))
        test.expect(test.dut.at1.send_and_verify("AT&F"), "OK")
    

if "__main__" == __name__:
    unicorn.main()

