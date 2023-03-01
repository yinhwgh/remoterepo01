#responsible: shuang.liang@globallogic.com
#location: Beijing
#TC0095580.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC0095580.001    AtCgansBasic

    basic test for AT+CGANS

1. Check the test and write command AT+CGANS without PIN.
2. Check the test and write command AT+CGANS with PIN.
3. Check invalid values for parameters for write command AT+CGANS
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_get_imei()
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("1. Check the test and write command AT+CGANS without PIN.")
        check_cgans(test, 'test', 'CME ERROR: SIM PIN required')
        check_cgans(test, 'write', 'CME ERROR: SIM PIN required', '1')
        check_cgans(test, 'write', 'CME ERROR: SIM PIN required')

        test.log.step("2. Check the test and write command AT+CGANS with PIN.")
        test.expect(dstl_register_to_network(test.dut))

        check_cgans(test, 'test', 'OK')
        check_cgans(test, 'write', 'OK', '1')
        check_cgans(test, 'write', 'OK')
        check_cgans(test, 'write', 'OK', '1,"PPP"')
        check_cgans(test, 'write', 'OK', '1,"PPP",1')

        test.log.step("Check invalid values for parameters for write command AT+CGANS")
        check_cgans(test, 'write', 'ERROR', '-1')
        check_cgans(test, 'write', 'ERROR', '2')
        check_cgans(test, 'write', 'ERROR', '1,0')
        check_cgans(test, 'write', 'ERROR', '1?')
        check_cgans(test, 'write', 'ERROR', 'one')
        check_cgans(test, 'write', 'ERROR', '255')

        check_cgans(test, 'write', 'OK', '0')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def check_cgans(test, mode, expected_response, value='0'):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGANS=?", ".*\\+CGANS: \\(0[,-]1\\),.* \\(\"PPP\"\\).*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGANS=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGANS={}".format(value), ".*{}.*".format(expected_response)))



if "__main__" == __name__:
    unicorn.main()
