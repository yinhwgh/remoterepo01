#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000422.001

import unicorn

from core.basetest import BaseTest

from dstl.status_control import extended_indicator_control
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import check_urc
from dstl.security import lock_unlock_sim
from dstl.network_service import customization_network_types
from dstl.network_service import customization_operator_id
from dstl.network_service import operator_selector

import re

class Test(BaseTest):
    '''
    TC0000422.001 -  TpCpol01
    AT+CPOL (Preferred Operator List)
    This testcase will check the functionality of this AT+Command.
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify(f"AT+CMEE=2", "OK"))

    def run(test):
        test.log.info("Step 1. Checking <Test Command> [AT+CPOL=?] --> returns list of supported <index>s and <format>s in the SIM preferred operator list")
        cpol_test_response = "\+CPOL: \(1\-\d{1,3}\),\(0\-2\)"
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))
        test.expect(test.dut.at1.send_and_verify("AT+CPLS?", "\+CPLS: 0"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=?", cpol_test_response))

        test.log.info("Step 2. Checking <Read Command> [AT+CPOL?] --> returns preferred <index>, <format>, <operator> ")
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", "(\+CPOL: \d{1,2},0,\"(\w|\s)+?\",[01],[01],[01],[01]\s+)*OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL=,2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", "(\+CPOL: \d{1,2},2,\"\d+?\",[01],[01],[01],[01]\s+)*OK"))

        test.log.info("Step 3. Checking <Write Command> [AT+CPOL=***] --> <index>[, <format>, <operator>]")
        test.log.info("Step 3.1 Replace 1st and 2nd position of list")
        cpol_list = re.findall("(\+CPOL: [12],2,(\"\d+?\",[01],[01],[01],[01]))",test.dut.at1.last_response)
        if cpol_list is not None and len(cpol_list)==2:
            cpol_position_1 = cpol_list[0][1]
            cpol_position_2 = cpol_list[1][1]
            cpol_read_response_recover = f"\+CPOL: 1,2,{cpol_position_1}\s+\+CPOL: 2,2,{cpol_position_2}\s+"
            cpol_read_response_reverse = f"\+CPOL: 1,2,{cpol_position_2}\s+\+CPOL: 2,2,{cpol_position_1}\s+"
        else:
            test.log.info("Not enough operators are read, use default operators to continue tests.")
            cpol_position_1 = '"26202",1,0,1,0'
            cpol_position_2 = '"26203",0,0,0,1'
            cpol_read_response_recover = f"\+CPOL: 1,2,{cpol_position_1}\s+\+CPOL: 2,2,{cpol_position_2}\s+"
            cpol_read_response_reverse = f"\+CPOL: 1,2,{cpol_position_2}\s+\+CPOL: 2,2,{cpol_position_1}\s+"
            test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,{cpol_position_1}", "OK"))
            test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=2,2,{cpol_position_2}", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT+CPOL?", cpol_read_response_recover))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,{cpol_position_2}", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=2,2,{cpol_position_1}", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", cpol_read_response_reverse))
        test.log.info("Step 3.2 Change 1st and 2nd position back to default operator")
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,{cpol_position_1}", "OK"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=2,2,{cpol_position_2}", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPOL?", cpol_read_response_recover))

        test.log.info("Step 4. Checking for intentional Errors")
        cpol_error = "\+CME ERROR: invalid index"
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=-1", cpol_error))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,3", cpol_error))
        # IPIS100324123 no exetended error for invalid operator - not to fix
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,\"abc\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify(f"AT+CPOL=1,2,\"46000\",a", cpol_error))

        test.log.info("Step 5. Check CPOL READ TEST for all CPLS value")
        for i in range(3):
            test.expect(test.dut.at1.send_and_verify(f"AT+CPLS={i}", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT+CPLS?", f"\+CPLS: {i}"))
            test.expect(test.dut.at1.send_and_verify("AT+CPOL=?", cpol_test_response))
            test.expect(test.dut.at1.send_and_verify("AT+CPOL?", "(\+CPOL: \d{1,2},0,\"(\w|\s)+?\",[01],[01],[01],[01]\s+)*OK"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify(f"AT+CPLS=0", "OK"))


if __name__=='__main__':
    unicorn.main()