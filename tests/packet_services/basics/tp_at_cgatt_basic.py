# responsible: malgorzata.kaluza@globallogic.com
# location: Wroclaw
# TC0091872.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.security.lock_unlock_sim import dstl_lock_sim,dstl_unlock_sim

class Test(BaseTest):
    """
    TC0091872.001    TpAtCgattBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CGATT.

    1. check command without and with PIN
    1.1 scenario without PIN: test, read and write commands should be PIN protected
    1.2 scenario with PIN
    - check test command response
    - check response for read command CGATT in related to SCFG=GPRS/Autoattach settings
    - set <state> to value 0 in write command
    - read the actual settings - state should be setting to: 0
    - set <state> to value 1 in write command
    - read the actual settings - state should be setting to: 1
    2. check all parameters and also with invalid values (error should be displayed)
    - check EXEC command
    - check test command invalid value
    - check read command invalid value
    - try to set not supported value for write command: -1 and 2
    - try to set empty write command (OK or ERROR - according to ATC)
    - try to set state parameter value not as a number
    - try to set write command with more than 1 parameter
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_lock_sim(test.dut)
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("1. check command without and with PIN")
        test.log.step("1.1 scenario without PIN: test, read and write commands should be PIN protected")
        check_cgatt(test, 'test', 'CME ERROR: SIM PIN required')
        check_cgatt(test, 'write', 'CME ERROR: SIM PIN required', '1')
        check_cgatt(test, 'read', 'CME ERROR: SIM PIN required')

        test.log.step("1.2 scenario with PIN")

        test.expect(dstl_register_to_network(test.dut))

        test.log.info("* check test command response")
        check_cgatt(test, 'test', 'OK')

        test.log.info("* check response for read command CGATT in related to SCFG=GPRS/Autoattach settings")
        check_auto_attach_status_and_ps_state(test)

        test.log.info("* set <state> to value 0 in write command")
        check_cgatt(test, 'write', 'OK', '0')

        test.log.info("* read the actual settings - state should be setting to: 0")
        check_cgatt(test, 'read', 'OK', '0')

        test.log.info("* set <state> to value 1 in write command")
        check_cgatt(test, 'write', 'OK', '1')

        test.log.info("* read the actual settings - state should be setting to: 1")
        check_cgatt(test, 'read', 'OK', '1')

        test.log.step("2. check all parameters and also with invalid values (error should be displayed)")

        test.log.info("* check EXEC command")
        check_cgatt(test, 'exec', 'ERROR')

        test.log.info("* check test command invalid value")
        check_cgatt(test, 'write', 'ERROR', '1?')

        test.log.info("* check read command invalid value")
        check_cgatt(test, 'read', 'ERROR', '', True)

        test.log.info("* try to set not supported value for write command: -1 and 2")
        check_cgatt(test, 'write', 'ERROR', '-1')
        check_cgatt(test, 'write', 'ERROR', '2')

        test.log.info("* try to set empty write command (OK or ERROR - according to ATC)")
        check_cgatt(test, 'write', 'OK', '')

        test.log.info("* try to set state parameter value not as a number")
        check_cgatt(test, 'write', 'ERROR', 'one')

        test.log.info("* try to set write command with more than 1 parameter")
        check_cgatt(test, 'write', 'ERROR', '1,0')

        test.log.info("* set cgatt proper value again")
        check_cgatt(test, 'write', 'OK', '1')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        dstl_unlock_sim(test.dut)

def check_auto_attach_status_and_ps_state(test):
    test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\"", ".*OK.*"))
    status = test.expect(re.search(".*SCFG: \"GPRS/AutoAttach\",(\".*\").*", test.dut.at1.last_response))
    attach_status = status.group(1)
    if 'enabled' in attach_status:
        check_cgatt(test, 'read', 'OK', '1')
    else:
        check_cgatt(test, 'read', 'OK', '0')


def check_cgatt(test, mode, expected_response, value='0', invalid_read_command=False):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*\\+CGATT: \\(0[,-]1\\).*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGATT={}".format(value), ".*{}.*".format(expected_response)))
    elif mode is 'exec':
        test.expect(test.dut.at1.send_and_verify("AT+CGATT", ".*{}.*".format(expected_response)))
    else:
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*\\+CGATT: {}.*OK.*".format(value)))
        else:
            if invalid_read_command:
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?11?", ".*{}.*".format(expected_response)))
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*{}.*".format(expected_response)))


if "__main__" == __name__:
    unicorn.main()
