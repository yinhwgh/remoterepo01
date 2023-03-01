#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000421.001

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
from dstl.network_service import customization_cops_properties

import re

class Test(BaseTest):
    '''
    TC0000421.001 - TpCopsFunction
    This testcase will check the functionality of this AT+Command.
    Subscribers: 1 dut, 1 remote module which supports voice call
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=0", "OK"))
        test.network_types = test.dut.dstl_customized_network_types()
        if test.network_types['GSM'] == True:
            test.register_cmd = "CREG"
        else:
            test.register_cmd = "CEREG"

    def run(test):
        test.response_timeout = 150
        test.network_error = "\+CME ERROR: no network service"
        test.log.info("Preparations: SIM-Card inserted but not registered to network")
        test.expect(test.dut.dstl_enter_pin())
        test.attempt(test.dut.at1.send_and_verify,"AT+COPS=2","OK", timeout=test.response_timeout, sleep=5, retry=5)
        test.log.info("Step 1: Checking <Test Command> [AT+COPS=?] --> returns a list of all present providers")
        test_response = test.dut.dstl_customized_cops_test_response()
        test.expect(test.dut.at1.send_and_verify("AT+COPS=?", test_response, timeout=test.response_timeout))
        test.log.info("Step 2: Checking <Read Command> [AT+COPS?] --> returns current mode - 2")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2"))
        test.log.info("Step 2.1: Checking <Read Command> [AT+COPS?] --> returns current operator")
        test.attempt(test.dut.at1.send_and_verify,"AT+COPS=0","OK", timeout=test.response_timeout, sleep=5, retry=5)
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 0,\d,\".+?\",\d"))
        
        forbidden_operators = test.dut.dstl_get_forbidden_operators(timeout=test.response_timeout)
        if forbidden_operators:
            test.forbidden_operator = forbidden_operators[1].split(',')[0]
            test.forbidden_operator_rat = forbidden_operators[1].split(',')[1]
        else:
            test.forbidden_operator = ""
            test.forbidden_operator_rat = ""

        test.log.info("Step 3: Checking <Write Command> [AT+COPS=***] --> supported parameter: <mode>[, <format>[, <oper>]]")
        test.cops_mode_1_test(step_number="3.1")
        test.cops_mode_0_test(step_number="3.2")
        test.cops_mode_2_test(step_number="3.3")
        test.cops_mode_4_test(step_number="3.4")
        test.cops_mode_3_test(step_number="3.5")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "OK", wait_for="(OK|ERROR)"))
        if "COPS: 0" not in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", wait_for="(OK|ERROR)", timeout=test.response_timeout))
    
    def cops_mode_1_test(test, step_number="3.1"):
        test.log.info(f"Step {step_number}: COPS <mode>=1 (manual operator selection)")
        test.log.info(f"Step {step_number}.1:  Select non-existent operator ('88888'), while being registered to home operator ('CREG: 1')")
        test.check_registration_status("1")
        test.check_invalid_operator(operator="88888", cops_result=test.network_error, reg_state="2", cops_value="\+COPS: 1\s+")
        test.log.info(f"Step {step_number}.2:  Select forbidden operator (e.g.Vodafone D2 - '26202' in test case)")
        if test.forbidden_operator != "":
            test.check_invalid_operator(operator=test.forbidden_operator, cops_result=test.network_error, reg_state="(0|[234])", cops_value="\+COPS: 1\s+", rat=test.forbidden_operator_rat)
        else:
            test.log.error(f"Forbidden operators is blank, step skipped: {step_number}.2:  Select forbidden operator (e.g.Vodafone D2 - '26202' in test case).")
        
        
    def cops_mode_0_test(test, step_number="3.2"):
        test.log.info(f"Step {step_number}:  COPS <mode>=0 (auto operator selection)")
        test.log.info(f"Step {step_number}.1:  <format>='2' (numeric operator)")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=test.response_timeout))
        test.check_registration_status("(0|[234])")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2\s+"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,2", "OK", timeout=test.response_timeout))
        test.check_registration_status("1")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 0,2,\"\d{5}\",\d\s+"))
        test.log.info(f"Step {step_number}.2:  <format>='0' (alpha operator)")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=test.response_timeout))
        test.check_registration_status("0")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2\s+"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,0", "OK", timeout=test.response_timeout))
        test.check_registration_status("1")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 0,0,\"(\w|\s)+\",\d\s+"))
    
    def cops_mode_2_test(test, step_number="3.3"):
        test.log.info(f"Step {step_number}:  COPS <mode>=2 (deregister from network)")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=test.response_timeout))
        test.check_registration_status("0")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2\s+"))
        
        test.log.info(f"Step {step_number}.1:  If deregistration was successful, it should be impossible to call subscriber 2")
        test.expect(test.dut.at1.send_and_verify("ATD{};".format(test.r1.sim.nat_voice_nr), "NO CARRIER", wait_for="NO CARRIER"))
    
    def cops_mode_4_test(test, step_number="3.4"):
        operator_id = test.dut.dstl_get_operator_id()
        home_register_info = "\+COPS: 0,2,\"" + operator_id + "\",\d\s+"
        test.log.info(f"Step {step_number}: COPS <mode>=4 (manual/auto operator selection)")
        test.log.info(f"Step {step_number}.1:  Being not-registered to network ('CREG: 0')")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=test.response_timeout))
        test.check_registration_status("0")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "\+COPS: 2\s+"))
        
        test.log.info(f"Step {step_number}.1.1:  Select not-existent operator ('88888')")
        test.check_invalid_operator(operator="88888", cops_result="OK", reg_state="1", cops_value=home_register_info, mode="4")
        test.log.info(f"Step {step_number}.1.2:  Select forbidden operator (e.g. Vodafone D2 - '26202' in test case")
        if test.forbidden_operator != "":
            test.check_invalid_operator(operator=test.forbidden_operator, cops_result="OK", reg_state="1", cops_value=home_register_info, rat=test.forbidden_operator_rat, mode="4")
        else:
            test.log.error(f"Forbidden operators is blank, step skipped：{step_number}.1.2:  Select forbidden operator (e.g. Vodafone D2 - '26202' in test case.")

        test.log.info(f"Step {step_number}.2 Being registered to home operator ('CREG: 1')")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", timeout=test.response_timeout))
        test.check_registration_status("1")
        if test.dut.at1.send_and_verify("AT+COPS?", home_register_info):
            test.log.info(f"Step {step_number}.2.1 Select not-existent operator ('88888')")
            test.check_invalid_operator(operator="88888", cops_result="OK", reg_state="1", cops_value=home_register_info, mode="4")
            test.log.info(f"Step {step_number}.2.2 Select forbidden operator (e.g. Vodafone D2 - '26202' in test case)")
            if test.forbidden_operator != "":
                test.check_invalid_operator(operator=test.forbidden_operator, cops_result="OK", reg_state="1", cops_value=home_register_info, rat=test.forbidden_operator_rat, mode="4")
            else:
                test.log.error(f"Forbidden operators is blank, step skipped: {step_number}.2.2 Select forbidden operator (e.g. Vodafone D2 - '26202' in test case)")
            
            test.log.info(f"Step {step_number}.2.3 Select home operator (e.g. O2 - '26207' in test case)")
            test.expect(test.dut.at1.send_and_verify(f"AT+COPS=4,2,\"{operator_id}\"", "OK", timeout=30))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?", f"\+COPS: 1,2,\"{operator_id}\",\d"))

        else:
            test.log.error(f"Module is not registered, step skipped: {step_number}.2 Being registered to home operator ('CREG: 1')")
        
    def cops_mode_3_test(test, step_number="3.5"):
        test.log.info(f"Step {step_number}: COPS <mode>=3 (set <format> for read command)")
        test.log.info(f"Step {step_number}.1: COPS <mode>=3 (set <format> for read command) when module is registered automatically")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", timeout=test.response_timeout))
        test.check_registration_status("1")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "OK", timeout=test.response_timeout))
        test.attempt(test.dut.at1.send_and_verify,"AT+COPS=?", '\(2,"(.+?)","(.+?)","(\d+?)",(\d)\)', timeout=test.response_timeout, retry=3, sleep=5)
        cops_response = test.dut.at1.last_response
        current_operators = re.findall('\(2,"(.+?)","(.+?)","(\d+?)",(\d)\)', cops_response)
        if current_operators:
            current_operator_format_0,current_operator_format_1,current_operator_format_2,rat = current_operators[0]
            test.log.info(f"Step {step_number}.1.1:  <format>='0' (long alpha operator)")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=3,0","OK"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?",f"COPS: 0,0,\"{current_operator_format_0}\",{rat}"))
            test.log.info(f"Step {step_number}.1.2:  <format>='1' (short alpha operator)")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=3,1","OK"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?",f"COPS: 0,1,\"{current_operator_format_1}\",{rat}"))
            test.log.info(f"Step {step_number}.1.3:  <format>='2' (numeric operator)")
            test.expect(test.dut.at1.send_and_verify("AT+COPS=3,2","OK"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS?",f"COPS: 0,2,\"{current_operator_format_2}\",{rat}"))
        else:
            test.expect(False, msg=f"Module is not registered to network or incorred response for AT+COPS=?\nStep skipped: Step {step_number}: COPS <mode>=3 (set <format> for read command)")
       


    def check_invalid_operator(test, operator, cops_result, reg_state, cops_value, rat="", mode="1"):
        if rat != "":
            rat = "," + rat
        test.expect(test.dut.at1.send_and_verify(f"AT+COPS={mode},2,\"{operator}\"{rat}",cops_result, timeout=180))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", cops_value))
        test.check_registration_status(reg_state)
    

    def check_registration_status(test, status_number):
        is_registration_status_correct = test.dut.at1.send_and_verify(f"AT+{test.register_cmd}?", "\+" + f"{test.register_cmd}: \d,{status_number}")
        test.expect(is_registration_status_correct)
        # test call function only when module is successfully registered
        if status_number=="1" and is_registration_status_correct:
            test.dut.at1.send_and_verify("ATD{};".format(test.r1.sim.nat_voice_nr))
            test.expect(test.r1.at1.wait_for("RING", timeout=30))
            test.expect(test.dut.at1.send_and_verify("AT+CHUP", "OK"))
            
   

if __name__=='__main__':
    unicorn.main()
