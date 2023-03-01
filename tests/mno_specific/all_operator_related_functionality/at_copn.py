#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000420.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class TpCopn(BaseTest):
    """
        TC0000420.001 -  TpCopn
        This testcase will check the functionality of this AT+Command.

        ==> Some provider names and/or codes will be changed from time to time <==
        Debugged: Serval
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        # 1. SIM PIN is required for COPN commands
        test.log.info("1. SIM PIN is required for COPN commands")
        test.dut.at1.send_and_verify("at+cmee=2", "OK")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", expect="SIM PIN", retry=5, sleep=1)
        test.expect(test.dut.at1.send_and_verify("at+copn=?", "\+CME ERROR: SIM PIN required"))
        test.expect(test.dut.at1.send_and_verify("at+copn", "\+CME ERROR: SIM PIN required"))
        # 2. Proper responses are returned after entering pin
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("at+copn=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("at+copn", "OK", wait_for="\sOK\s", timeout=15))
        # Each operator information matches format +COPN: "<number>", "<name>"
        operators = test.dut.at1.last_response.split('\n')
        # Remove None elements
        operators = list(filter(None, operators))
        # Remove fist element "AT+COPN" and last element "OK"
        operators.remove(operators[0])
        operators.remove("OK")
        match_result = True
        for operator in operators:
            match_object = re.match('\+COPN:\s+"\d+","\S.*"', operator)
            if match_object is None or match_object.string != operator:
                test.log.error("Operator \"{}\" is not in correct format.".format(operator))
                match_result = False
        test.expect(match_result)
        # 3. Error message returns with invalid commands when CMEE is 2 and 1
        test.expect(test.dut.at1.send_and_verify("at+copn?", "\+CME ERROR:\s+\w.*"))
        test.expect(test.dut.at1.send_and_verify("at+copn=3", "\+CME ERROR:\s+\w.*"))
        test.expect(test.dut.at1.send_and_verify("at+copn=", "\+CME ERROR:\s+\w.*"))
        test.expect(test.dut.at1.send_and_verify("at+copn=Test", "\+CME ERROR:\s+\w.*"))
        test.dut.at1.send_and_verify("at+cmee=1", "OK")
        test.expect(test.dut.at1.send_and_verify("at+copn?", "\+CME ERROR:\s+\d{1,3}"))
        test.expect(test.dut.at1.send_and_verify("at+copn=3", "\+CME ERROR:\s+\d{1,3}"))
        test.expect(test.dut.at1.send_and_verify("at+copn=", "\+CME ERROR:\s+\d{1,3}"))
        test.expect(test.dut.at1.send_and_verify("at+copn=Test", "\+CME ERROR:\s+\d{1,3}"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
