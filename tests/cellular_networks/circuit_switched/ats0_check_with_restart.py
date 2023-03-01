#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095733.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call.setup_voice_call import dstl_is_data_call_supported

import random

class Test(BaseTest):
    '''
    TC0095733.001 - ATS0CheckWithRestart
    Intention: check ATS0 function after restart module(IPIS100098539)
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())

    def run(test):

        test.log.step("1.Set ATS0=2")
        test.expect(test.dut.at1.send_and_verify("ATS0=2", "OK"))

        test.log.step("2. at&v;")
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:002"))

        test.log.step("3. Restart module;")
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))

        test.log.step("4. at&v;")
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:000"))

        test.log.step("5. Call DUT , and check ATS0 function(Voice call & CSD Call);")
        test.func_check(False)

        test.log.step("6. Set ATS0=2;")
        test.expect(test.dut.at1.send_and_verify("ATS0=2", "OK"))

        test.log.step("7. at&v; at&w;")
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:002"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))

        test.log.step("8. Restart module;")
        test.dut.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.dstl_register_to_network())

        test.log.step("9. at&v;")
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:002"))

        test.log.step("10. Call DUT , and check ATS0 function(Voice call & CSD Call)")
        test.func_check(True)


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("ATS0=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:000"))

    def func_check(test,expect_auto_answer=True):
        dut_phone_num = test.dut.sim.nat_voice_nr
        if expect_auto_answer:
            test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
            test.expect(test.dut.at1.wait_for("(RING\s+){2}", timeout=60))
            test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,0,0,0.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
            test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
            test.expect(test.dut.at1.send_and_verify("ATH", "OK"))
            test.expect(test.r1.at1.wait_for("NO CARRIER"))
        else:
            test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
            test.expect(test.dut.at1.wait_for("(RING\s+){5}", timeout=60))
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,4,0,0.*"))
            test.expect(test.dut.at1.send_and_verify("ath", "OK"))
            test.expect(test.r1.at1.wait_for("NO CARRIER"))

        if test.dut.dstl_is_data_call_supported():
            test.log.info('Not implemented temporarily ...')


if "__main__" == __name__:
    unicorn.main()

