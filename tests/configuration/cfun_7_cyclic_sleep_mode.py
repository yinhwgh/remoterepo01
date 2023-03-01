#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0010333.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.sms import sms_functions


class TpCfun7(BaseTest):
    """
    TC0010333.001 -  TpCfun7
    Subscribers: 2
    MCTest: True
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        # SMS part may be replace to dstl methods in future
        # Configure for dut
        test.expect(test.dut.at1.send_and_verify("AT+CMGF=1","OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca_int),"OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPMS=\"SM\",\"SM\",\"SM\"", "OK"))
        test.expect(test.dut.dstl_enable_sms_urc())
        # Configure for remote module
        test.expect(test.r1.at1.send_and_verify("AT+CMGF=1", "OK"))
        test.expect(test.r1.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca_int),"OK"))
        test.expect(test.r1.at1.send_and_verify("AT+CPMS=\"SM\",\"SM\",\"SM\"","OK"))

    def run(test):
        # Set hardware flow control
        test.expect(test.dut.at1.send_and_verify("AT\Q3", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT&V", "\Q3"))
        test.dut.at1.reconfigure({"rtscts": True})
        # Set module to CFUN: 7
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=7", "OK"))
        # CTS is in cycle active
        # According to Dingo's behaviour, can only detect CTS status changes, cycle time is unsure
        test.expect(test.check_cts_status_with_mctest(times=50, state="pulse"))
        # Wake up module temporarily by SMS
        test.expect(test.r1.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr), ".*>.*", wait_for=".*>.*"))
        test.expect(test.r1.at1.send_and_verify("Cfun7 Test, wakeup module by SMS", end="\u001A"))
        test.expect(test.dut.at1.wait_for("\+CMTI:"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN?", expect="\+CFUN: 7", handle_errors=True, retry=10, sleep=0.5)
        test.expect(test.check_cts_status_with_mctest(times=1, state="high"))
        test.sleep(5)
        test.expect(test.check_cts_status_with_mctest(times=1, state="low"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN?", expect="\+CFUN: 7", handle_errors=True, retry=10, sleep=0.5)
        # Wake up module through voice call
        test.r1.at1.send("ATD{};".format(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.wait_for("RING"))
        test.dut.at1.send("ATA")
        test.expect(test.r1.at1.wait_for("OK"))
        test.r1.at1.send("ATH")
        test.expect(test.dut.at1.wait_for("NO CARRIER"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN?", expect="\+CFUN: 7", handle_errors=True, retry=10, sleep=0.5)
        test.expect(test.check_cts_status_with_mctest(times=1, state="high"))
        test.sleep(5)
        test.expect(test.check_cts_status_with_mctest(times=1, state="low"))
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN?", expect="\+CFUN: 7", handle_errors=True, retry=10, sleep=0.5)
        # Set module back to normal mode
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN=1", expect="OK", handle_errors=True, retry=10, sleep=0.5)
        test.sleep(1)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\+CFUN: 1"))

    def cleanup(test):
        # Set module back to normal mode
        test.attempt(test.dut.at1.send_and_verify, "AT+CFUN=1", expect="OK", handle_errors=True, retry=10, sleep=0.5)
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\+CFUN: 1"))
        test.dut.at1.reconfigure({"rtscts": False})

    def check_cts_status_with_mctest(test, times=50, state="pulse"):
        if state not in ("pulse", "high", "low"):
            test.log.error("Cannot detect CTS status {}".format(state))
            return False
        cts_state_change = []
        for i in range(0, times):
            test.dut.devboard.send_and_verify("MC:ASC0?")
            response = test.dut.devboard.last_response
            cts_index = response.index("CTS0") + 6
            cts_value = response[cts_index:cts_index + 1]
            cts_state_change.append(cts_value)
        if state == "pulse":
            search_string = "0+1+0+1+0+1+"
        elif state == "high":
            search_string = "^1+$"
        else:
            search_string = "^0+$"
        search_result = re.search(search_string, ''.join(cts_state_change))
        if search_result:
            test.log.info("Find {} in {}".format(search_string, str(cts_state_change)))
        else:
            test.log.error("Unable to find {} in {}".format(search_string, str(cts_state_change)))
        return search_result


if __name__ == "__main__":
    unicorn.main()
