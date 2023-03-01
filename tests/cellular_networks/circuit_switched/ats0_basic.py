#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091713.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call.setup_voice_call import dstl_is_data_call_supported

import random

class Test(BaseTest):
    '''
    TC0091713.001 - TpAtS0Basic
    Intention: This procedure provides basic tests for the command of AtS0
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())


    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        test.log.step("1.Read command and write command  without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("ATS0=2", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", "OK"))

        test.log.step("2. Read command and write command with PIN authentication")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("ATS0=2", "OK"))
        test.expect(test.dut.at1.send_and_verify("ATS0?", "002"))

        test.log.step("3. Check write command with invalid parameters")

        test.expect(test.dut.at1.send_and_verify("ATS0=-1", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0=256", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("ATS0=", "ERROR"))

        if test.dut.dstl_is_data_call_supported():
            test.log.info('Not implemented temporarily ...')
            test.log.step("4.Make an incomming data call with ats0 set to '5', release data call")
            test.log.step("5.Set DTR to off (at&d2) and make an incomming data call with sts0 set to '2', disconnect")

        test.log.step("6. Test voice call")
        test.expect(test.dut.at1.send_and_verify("ATS0=5", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))

        test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
        test.expect(test.dut.at1.wait_for("(RING\s+){5}", timeout=60))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,0,0,0.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
        test.expect(test.r1.at1.wait_for("NO CARRIER"))



    def cleanup(test):
        test.log.step("7.Restore default value with ats0=0")
        test.expect(test.dut.at1.send_and_verify("ATS0=0", "OK"))
        test.expect(test.dut.at1.send_and_verify("at&v", "S0:000"))



if "__main__" == __name__:
    unicorn.main()

