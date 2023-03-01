#responsible sebastian.lupkowski@globallogic.com
#Wroclaw
#TC 0093377.001
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC0093377.001    TpAtCgpiaf

    This procedure provides straight forward tests for the test and write command of +CGPIAF.

    1. Check command without PIN
    2. Check command with PIN
    3. Check with valid parameters
    4. Check invalid parameter values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        result = test.dut.at1.send_and_verify('AT+CPIN?', '.*SIM PIN.*')
        if not result:
            dstl_restart(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("1. Check command without PIN")
        check_cgpiaf(test, 'test', 'CME ERROR: SIM PIN required')
        check_cgpiaf(test, 'write', 'CME ERROR: SIM PIN required', '1')
        check_cgpiaf(test, 'read', 'CME ERROR: SIM PIN required', '1')
        check_cgpiaf(test, 'write', 'CME ERROR: SIM PIN required')
        check_cgpiaf(test, 'read', 'CME ERROR: SIM PIN required')

        test.log.step("2. Check command with PIN")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(15)  # waiting for module to get ready
        check_cgpiaf(test, 'test', 'OK')

        test.log.step("3. Check with valid parameters")
        check_cgpiaf(test, 'write', 'OK')
        check_cgpiaf(test, 'read', 'OK', '0,0,0,0')
        check_cgpiaf(test, 'write', 'OK', '1,1')
        check_cgpiaf(test, 'read', 'OK', '1,1,0,0')
        check_cgpiaf(test, 'write', 'OK', '1,0,1')
        check_cgpiaf(test, 'read', 'OK', '1,0,1,0')
        check_cgpiaf(test, 'write', 'OK', '1,0,1,1')
        check_cgpiaf(test, 'read', 'OK', '1,0,1,1')
        check_cgpiaf(test, 'write', 'OK', '1,0,0,1')
        check_cgpiaf(test, 'read', 'OK', '1,0,0,1')
        check_cgpiaf(test, 'write', 'OK', '1,0,1,0')
        check_cgpiaf(test, 'read', 'OK', '1,0,1,0')
        check_cgpiaf(test, 'write', 'OK', '1,1,1,1')
        check_cgpiaf(test, 'read', 'OK', '1,1,1,1')
        check_cgpiaf(test, 'write', 'OK', '1,1,0,1')
        check_cgpiaf(test, 'read', 'OK', '1,1,0,1')
        check_cgpiaf(test, 'write', 'OK', '')
        check_cgpiaf(test, 'read', 'OK', '1,1,0,1')

        test.log.step("4. Check invalid parameter values")
        check_cgpiaf(test, 'write', 'ERROR', '-1')
        check_cgpiaf(test, 'write', 'ERROR', '2')
        check_cgpiaf(test, 'write', 'ERROR', '1,2')
        check_cgpiaf(test, 'write', 'ERROR', '1,-1')
        check_cgpiaf(test, 'write', 'ERROR', '1,0,2')
        check_cgpiaf(test, 'write', 'ERROR', '1,0,-1')
        check_cgpiaf(test, 'write', 'ERROR', '1,0,0,2')
        check_cgpiaf(test, 'write', 'ERROR', '1,0,0,-1')

        check_cgpiaf(test, 'write', 'OK')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def check_cgpiaf(test, mode, expected_response, value='0'):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=?", ".*[+]CGPIAF: \\(0[,-]1\\),\\(0[,-]1\\),"
                                                                    "\\(0[,-]1\\),\\(0[,-]1\\).*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF={}".format(value), ".*{}.*".format(expected_response)))
    else:
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF?", ".*[+]CGPIAF: {}.*OK.*".format(value)))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF?", ".*{}.*".format(expected_response)))


if "__main__" == __name__:
    unicorn.main()
