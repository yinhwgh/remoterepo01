# responsible: wen.liu@thalesgroup.com
# location: Dalian
# TC0093947.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, dstl_set_airplane_mode


class Test(BaseTest):
    """
    TC0093947.001 - TpAtCvmodBasic
    Intention:  This procedure provides basic tests for the VoLTE related command AT+CVMOD.
    Subscriber: 1
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))

        test.test_resp = '\s+\+CVMOD: \(0-3\)\sOK\s'
        if test.dut.project is 'VIPER':
            test.test_resp = '\s+\+CVMOD: \(0,1,3\)\s+OK\s'
        pass

    def run(test):
        test.log.step("1. Test/Read/Write command without PIN")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', '\+CPIN: SIM PIN\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=0', '\+CME ERROR: SIM PIN required'))
        test.log.step("2. Test/Read/Write command with PIN")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('at+cvmod=?', test.test_resp))
        value = ['0', '1', '3']
        for set_value in value:
            test.expect(test.dut.at1.send_and_verify(f'at+cvmod={set_value}'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
        test.log.step("3. Check invalid parameters")
        test.expect(test.dut.at1.send_and_verify('at+cvmod=2', '\+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=4', '\+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=-1', '\+CME ERROR: invalid index'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=a', '\+CME ERROR: invalid index'))
        test.log.step("4. Check influence on current setting for AT&F")
        for set_value in value:
            test.expect(test.dut.at1.send_and_verify(f'at+cvmod={set_value}'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at&f', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
        test.log.step("5. Check influence on current setting for AT&W")
        for set_value in value:
            test.expect(test.dut.at1.send_and_verify(f'at+cvmod={set_value}'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
            test.expect(test.dut.at1.send_and_verify('at&w', 'OK'))
            test.expect(test.dut.dstl_restart())
            test.expect(test.dut.dstl_enter_pin())
            test.sleep(5)
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
        test.log.step("6. Check influence on current setting for AT&Z")
        for set_value in value:
            test.expect(test.dut.at1.send_and_verify(f'at+cvmod={set_value}'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
            test.expect(test.dut.at1.send_and_verify('atz', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cvmod?', f'\+CVMOD: {set_value}\s+OK'))
        test.log.step("7. Check influence on current setting for airplane mode")
        test.dut.dstl_set_airplane_mode()
        test.expect(test.dut.at1.send_and_verify('at+cvmod=?', '\+CME ERROR: operation not supported'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod?', '\+CME ERROR: operation not supported'))
        test.expect(test.dut.at1.send_and_verify('at+cvmod=0', '\+CME ERROR: operation not supported'))
        pass

    def cleanup(test):
        test.dut.dstl_set_full_functionality_mode()
        test.expect(test.dut.at1.send_and_verify('at+cvmod=3'))
        pass


if '__main__' == __name__:
    unicorn.main()
