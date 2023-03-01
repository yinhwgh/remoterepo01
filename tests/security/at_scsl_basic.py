# responsible: xiaolin.liu@thalesgroup.com
# location: Dalian
# TC0094276.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security.lock_unlock_sim import dstl_lock_sim
import re


class Test(BaseTest):
    """
    TC0094276.001 - TpAtScslBasic
    Intention: This procedure provides the possibility of basic tests  for the test and write command of ^SCSL.
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2'))
        test.dut.dstl_enter_pin()
        test.expect(test.dut.dstl_lock_sim())
        pass

    def run(test):
        test.log.step("1. Chect the current status")
        test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2'))
        last_response = test.dut.at1.last_response
        data = test.get_operator()
        if '^SCSL: ""' in last_response:
            pw = 12345678
            test.log.step("2. If no SIM card is inserted, AT^SCSL is not SIM PIN protected")
            test.expect(test.dut.devboard.send_and_verify("MC:CCIN=1"))
            test.sleep(3)
            test.expect(test.dut.at1.send_and_verify('AT^SCSL=?'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",1,"{pw}","{data}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', f'\^SCSL: "{data}"'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",0,"{pw}"', '.*OK.*'))
            test.log.step("3. If SIM card is inserted AT^SCSL is SIM PIN protected")
            test.dut.dstl_restart()
            test.sleep(5)
            test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0"))
            test.sleep(3)
            test.log.step("3.1 Test without pin")
            test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL=?'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', '+CME ERROR: SIM PIN required'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",1,"{pw}","999.99:{data}"',
                                                     '+CME ERROR: SIM PIN required'))
            test.log.step("3.2 Test with pin")
            test.dut.dstl_enter_pin()
            test.expect(test.dut.at1.send_and_verify('AT^SCSL=?'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",1,"{pw}","999.99:{data}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', f'\^SCSL: "999.99:{data}"'))
            test.log.step("3.3 Test invalid parameter")
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="aa",2', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN;",2', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",3', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",A*', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",1,"#$%","*^%("', 'ERROR'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",1,"",""', 'ERROR'))
            test.log.step("4 Function check")
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', f'\^SCSL: "999.99:{data}"'))
            test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '\+CPIN: READY'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",0,"{pw}"', '.*OK.*'))

            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",1,"{pw}","999.99"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', '\^SCSL: "999.99"'))
            test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '\+CPIN: PH-NET PIN'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",0,"{pw}"', '.*OK.*'))

            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",1,"{pw}","{data}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', f'\^SCSL: "{data}"'))
            test.expect(test.dut.at1.send_and_verify('AT+CPIN?', '\+CPIN: READY'))
            test.expect(test.dut.at1.send_and_verify(f'AT^SCSL="PN",0,"{pw}"', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', '\^SCSL: ""\s+OK\s+'))
        else:
            test.log.error("This module has been PN locked!")
        pass

    def cleanup(test):
        # set all back, in case script has aborted somewhere in the mid
        test.expect(test.dut.devboard.send_and_verify("MC:CCIN=0"))
        ret = test.expect(test.dut.at1.send_and_verify('AT^SCSL="PN",2', '\^SCSL: ""\s+OK\s+'))
        if not ret:
            test.expect(False, msg="PLEASE CHECK IMMEDIATELY THE SCSL LOCK, USE PASSWORD '12345678' to UNLOCK! ")
        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))
        pass

    def get_operator(test):
        test.expect(test.dut.at1.send_and_verify("AT+CIMI"))
        # last_response = test.dut.at1.last_response
        find_mccmnc = re.findall("\d+", test.dut.at1.last_response)
        result = find_mccmnc[0][0:3] + '.' + find_mccmnc[0][3:5]
        return result


if '__main__' == __name__:
    unicorn.main()
