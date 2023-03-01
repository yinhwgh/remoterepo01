#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC TC0092972.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration.default_parameters import dstl_get_default_ate_value

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        ate_default = test.dut.dstl_get_default_ate_value()
        test.log.info('1. Send ATE command with no parameter.')
        test.expect(test.dut.at1.send_and_verify('ATE', 'OK'))

        test.expect(test.dut.at1.send_and_verify('AT&V', ate_default))
        test.log.info('2. Send ATE command with ATE1.')
        test.expect(test.dut.at1.send_and_verify('ATE1', 'OK'))
        test.expect( test.dut.at1.send_and_verify('AT&V', 'E1'))
        test.log.info('3. Disable echo witch ATE0.')
        test.expect(test.dut.at1.send_and_verify('ATE0', 'OK'))

        test.log.info('4. Check ATE setting with AT&V.')
        test.expect(test.dut.at1.send_and_verify('AT&V', 'E0'))
        test.log.info('5. Store ATE settings with AT&W.')
        test.expect(test.dut.at1.send_and_verify('AT&W', 'OK'))
        test.log.info('6. Restart module.')
        test.dut.dstl_restart()
        test.sleep(5)
        test.log.info('7. Check ATE setting with AT&V.')
        test.expect(test.dut.at1.send_and_verify('AT&V', 'E0'))
        test.log.info('8. Restore factory value with AT&F.')
        test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
        test.log.info('9. Check ATE setting with AT&V.')
        test.expect(test.dut.at1.send_and_verify('AT&V', 'E1'))
        test.log.info('10. Store ATE settings with AT&W. ')
        test.expect(test.dut.at1.send_and_verify('ATE1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT&W', 'OK'))
        test.expect(test.dut.at1.send_and_verify('ATE0', 'OK'))
        test.dut.dstl_enter_pin()
        # BOB-4735: workaround to catch SIM busy shortly after PIN1 entering
        test.attempt(test.dut.at1.send_and_verify, "ATZ", 'OK', retry=5, sleep=0.3, append=True)
        # workaround for Unicorn IPIS100311352
        if 'SIM failure' in test.dut.at1.last_response:
            test.log.critical("SIM busy expected here, see IPIS100311283")
            test.expect(False)

        test.expect(test.dut.at1.send_and_verify('AT&V', 'E1'))
        test.log.info('11. Send ATE0')
        test.expect(test.dut.at1.send_and_verify('ATE0', 'OK'))
        test.log.info('12. Send AT')
        send_command_and_check_echo(test,'AT', False)
        test.log.info('13. Send ATE1')
        test.expect( test.dut.at1.send_and_verify('ATE1', 'OK'))
        test.log.info('14. 12. Send AT')
        send_command_and_check_echo(test,'AT', True)

    def cleanup(test):
        pass

def send_command_and_check_echo(test,command,echo):
    test.dut.at1.send_and_verify(command)
    if echo == True:
        if command in test.dut.at1.last_response:
            test.expect(True)
        else:
            test.log.error('Echo message should show but not')
            test.expect(False)
    else:
        if command in test.dut.at1.last_response:
            test.log.error('Echo message should not show' )
            test.expect(False)
        else:
            test.expect(True)

if "__main__" == __name__:
    unicorn.main()
