#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105158.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.status_control import extended_indicator_control
from dstl.status_control import check_dtmf_urc
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call
from dstl.auxiliary import check_urc

import re
import random

class Test(BaseTest):
    """
    TC0105158.001 -  sind_dtmf_function
    Intention:
    Test case to check sind dtmf URC popup when DTMF characters are recognized during a on-going call.
    DTMF characters are listed below:
    0-9,*#,ABCD(not case sensitive)

    1. Restart both two modules with sim card inserted.
    2. For both DUT and remote one,Â  make both two register on network.
    3. Enable DTMF sind URCon DUT
        at^sind="dtmf",1
    4. Make a on-going call from DUT to remote, remote answer the call
    5. In remote side, generate TDMF tone by at+vts=0
    6. In DUT side verify DTMF URC popup as below
        +CIEV: "dtmf",0,1
    7. Repeat step 5 for all DTMF chars 0-9,*#,ABCD(abcd) and verify DTMF URC is triggered correctly for every chars.
    8. Disabled DTMF sind URCon DUT
        at^sind="dtmf",0
    9. Generate DTMF tone in remote side, verify in DUT side did not receive DTMF URC

    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        # set at+vtd to default value
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT+VTD?"))
    
    def run(test):
        dtmfs = list(range(0,10)) + ['*', '#', 'A', 'B', 'C', 'D']
        test.log.step("1. Restart two modules with sim card inserted")
        test.log.info("Skip restart since it is not necessary.")

        test.log.step("2. Make two modules register on network")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())

        test.log.step("3. Enabled sind DTMF URC on DUT side")
        test.expect(test.dut.dstl_enable_one_indicator("dtmf", False))

        test.log.step("4. Make a on-going call from DUT to remote, remote answer the call")
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, f"{test.r1.sim.nat_voice_nr}", "OK"),
                    critical=True, msg="Cannot continue tests due to voice call failure.")
       
        index = 0
        for dtmf in dtmfs:
            index += 1
            test.log.step(f"5.{index}. In remote side, generate DTMF tone by at+vts={dtmf}")
            test.sleep(2)
            test.expect(test.r1.at1.send_and_verify(f"AT+VTS=\"{dtmf}\",{index}"))

            test.log.step(f"6.{index}. In DUT side verify DTMF URC popup: +CIEV: \"dtmf\",{dtmf},1")
            if dtmf == '*':
                dtmf = f"\\{dtmf}"
            wait_for_urc = test.expect(test.dut.at1.wait_for(f"\\+CIEV: dtmf,\"{dtmf}\",1",
                                                             timeout=5, append=True))
        
        test.log.step('7. Disabled DTMF sind URC on DUT')
        test.expect(test.dut.dstl_disable_one_indicator("dtmf", False))

        test.log.step('8. Generate DTMF tone in remote side, verify in DUT side did not receive DTMF URC')
        index = 0
        response = ""
        for dtmf in dtmfs:
            index += 1
            test.expect(test.r1.at1.send_and_verify(f"AT+VTS=\"{dtmf}\",{index}"))
            test.sleep(1)
        test.expect(not test.dut.at1.wait_for("+CIEV: \"dtmf\"", timeout=5, append=True))

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.dstl_disable_one_indicator("dtmf", True))
        test.expect(test.dut.at1.send_and_verify("AT&F"), "OK")
    

if "__main__" == __name__:
    unicorn.main()

