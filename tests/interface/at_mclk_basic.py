# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0105192.001

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
    TC0105192.001 -  TpAtMclkBasic
    Intention:
    Check test,read and write command separately.
    Check settings shall be stored non-volatile.
    """

    def setup(test):
        test.dut.dstl_detect()
    
    def run(test):
        test.log.step("1. Check MCLK response of test command.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?", '\\^SCFG: "GPIO/Mode/MCLK",\\("std","off"\\)'))

        test.log.step("2. Check MCLK response of read command.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?", '\\^SCFG: "GPIO/Mode/MCLK","(off|std)"'))

        test.log.step("3. Enable MCLK , restart")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/MCLK\",\"std\"", '\\^SCFG: "GPIO/Mode/MCLK","std"\\s+OK'))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/MCLK\"", '\\^SCFG: "GPIO/Mode/MCLK","std"\\s+OK'))

        test.log.step("4. Disable MCLK , restart.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/MCLK\",\"off\"", '\\^SCFG: "GPIO/Mode/MCLK","off"\\s+OK'))
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/MCLK\"", '\\^SCFG: "GPIO/Mode/MCLK","off"\\s+OK'))

        test.log.step("5. check some invalid value(eg:-1, gpio, abcd,65535)")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        error_response = "\\+CME ERROR: invalid index"
        invalid_parameters = ['-1', 'gpio', 'rsv', 'abcd', '65535']
        for invalid_param in invalid_parameters:
            test.expect(test.dut.at1.send_and_verify(f"AT^SCFG=\"GPIO/Mode/MCLK\",\"{invalid_param}\"", error_response))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPIO/Mode/MCLK\",\"std\"", '\\^SCFG: "GPIO/Mode/MCLK","std"\\s+OK'))
    

if "__main__" == __name__:
    unicorn.main()

