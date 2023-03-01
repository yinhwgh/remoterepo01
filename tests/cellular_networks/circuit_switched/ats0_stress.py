# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0095731.001, TC0095731.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call import setup_voice_call
from dstl.call import extended_list_of_calls

import random


class Test(BaseTest):
    """
    TC0095731.001, TC0095731.002 - ATS0_Stress
    Intention: Stress test of ATS0
    Subscriber: 2, dut and remote module
    """
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_register_to_network())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        pass

    def run(test):
        loop_num = 100
        # restart_count = 0
        test.log.step("Set ATS0=5")
        test.expect(test.dut.at1.send_and_verify("ATS0=5", "OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", "\s+005\s+OK"))
        test.log.info(f"Loop for {loop_num} times")
        test.expect(test.dut.dstl_enable_slcc_urc())
        for loop in range(1, loop_num + 1):
            test.log.step(f"Loop {loop}/{loop_num} Call DUT from Remote and wait it auto answer")
            test.expect(test.dut.at1.send_and_verify("ATS0?", "\s+005\s+OK"))
            test.r1.at1.send_and_verify(f"ATD{test.dut.sim.nat_voice_nr};", timeout=10)
            test.log.info("Waiting for RING appears 5 times.")
            ring = test.expect(test.dut.at1.wait_for("(RING.*){5}", timeout=60))
            test.expect(test.dut.dstl_check_slcc_urc(is_mo=False))  # no append!, append=True))
            test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=False))
            test.expect(test.dut.dstl_release_call())
            test.expect(test.r1.at1.wait_for("NO CARRIER"))
            test.sleep(5)
        number = 5
        for loop in range(1, loop_num + 1):
            test.log.step(f"Loop {loop}/{loop_num}  Call DUT from Remote and rejected before anto answered;")
            test.expect(test.dut.at1.send_and_verify("ATS0?", f"\s+005\s+OK"))
            number = random.randint(1, 4)
            test.log.info(f'Got random number of RINGs: {number}')
            test.r1.at1.send_and_verify(f"ATD{test.dut.sim.nat_voice_nr};", timeout=10)
            test.log.info(f"Waiting for RING appears {number} times.")
            test.expect(test.dut.at1.wait_for("(RING.*)" + "{" + str(number) + "}", timeout=60))
            test.expect(test.dut.dstl_release_call())
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "OK"))
            test.expect(test.r1.at1.wait_for("NO CARRIER", timeout=60))
            test.sleep(5)
        pass

    def cleanup(test):
        test.expect(test.dut.dstl_disable_slcc_urc())
        test.expect(test.dut.at1.send_and_verify("ATS0=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", "\s+000\s+OK"))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        pass


if "__main__" == __name__:
    unicorn.main()
