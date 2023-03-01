#responsible: sebastian.lupkowski@globallogic.com
#location: Wroclaw
#TC0091872.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import dstl_get_imei
from dstl.security.set_sim_waiting_for_pin1 import dstl_set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    TC0091872.002    TpAtCgattBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CGATT.

    1. Check without PIN authentication: test, read and write commands
    2. Check with PIN authentication: test, read and write commands
    3. Check with PIN authentication and invalid values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_sim_waiting_for_pin1(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("1. Check without PIN authentication: test, read and write commands")
        check_cgatt(test, 'test', 'CME ERROR: SIM PIN required')
        check_cgatt(test, 'write', 'CME ERROR: SIM PIN required', '1')
        check_cgatt(test, 'read', 'CME ERROR: SIM PIN required', '1')
        check_cgatt(test, 'write', 'CME ERROR: SIM PIN required')
        check_cgatt(test, 'read', 'CME ERROR: SIM PIN required')

        test.log.step("2. Check with PIN authentication: test, read and write commands")
        test.expect(dstl_register_to_network(test.dut))

        check_cgatt(test, 'test', 'OK')
        check_cgatt(test, 'write', 'OK', '1')
        check_cgatt(test, 'read', 'OK', '1')
        check_cgatt(test, 'write', 'OK')
        check_cgatt(test, 'read', 'OK')
        check_cgatt(test, 'write', 'OK', '')
        check_cgatt(test, 'read', 'OK', '1')

        test.log.step("3. Check with PIN authentication and invalid values")
        check_cgatt(test, 'write', 'CME ERROR', '-1')
        check_cgatt(test, 'write', 'CME ERROR', '2')
        check_cgatt(test, 'write', 'CME ERROR', '1,0')
        check_cgatt(test, 'write', 'CME ERROR', '1?')
        check_cgatt(test, 'write', 'CME ERROR', 'one')
        check_cgatt(test, 'write', 'CME ERROR', '255')

        check_cgatt(test, 'write', 'OK', '1')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def check_cgatt(test, mode, expected_response, value='0'):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*\\+CGATT: \\(0[,-]1\\).*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGATT={}".format(value), ".*{}.*".format(expected_response)))
    else:
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*\\+CGATT: {}.*OK.*".format(value)))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", ".*{}.*".format(expected_response)))


if "__main__" == __name__:
    unicorn.main()
