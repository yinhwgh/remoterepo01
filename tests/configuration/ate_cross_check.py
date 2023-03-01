#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095730.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network

class CrossTestofATE(BaseTest):
    '''
    TC0095730.001 - CrossTestofATE
    Cross check of ATE and ATQ
    at1:asc0, at2:asc1
    '''
    def setup(test):
        test.expect(test.dut.at1.send_and_verify('ATQ0', 'OK'))
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()

    def run(test):
        test.log.info('1. Set ATE0 on ASC0.')
        test.expect(test.dut.at1.send_and_verify('ATE0', 'OK'))

        test.log.info('2. Input Cascading command; such as: at+cops?;+creg?')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at1))

        test.log.info('3. Set ATQ1.')
        test.expect(test.dut.at1.send_and_verify('ATQ1', '^$', wait_for='^$', handle_errors=True))

        test.log.info('4. Input Cascading command.')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at1))
        test.expect('OK' not in test.dut.at1.last_response)

        test.log.info('5. Set ATQ0.')
        test.expect(test.dut.at1.send_and_verify('ATQ0', 'OK'))

        test.log.info('6. Input Cascading command.')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at1))
        test.expect('OK' in test.dut.at1.last_response)

        test.log.info('7. Change to Asc1, check ATE value.')
        test.expect(test.dut.at2.send_and_verify('AT&V', 'E1'))

        test.log.info('8. Set ATE0 on ASC1.')
        test.expect(test.dut.at2.send_and_verify('ATE0', 'OK'))

        test.log.info('9. Input Cascading command.')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at2))

        test.log.info('10. Set ATQ1.')
        test.expect(test.dut.at2.send_and_verify('ATQ1', '^$', wait_for='^$', handle_errors=True))

        test.log.info('11. Input Cascading command.')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at2))
        test.expect('OK' not in test.dut.at2.last_response)

        test.log.info('12. Set ATQ0.')
        test.expect(test.dut.at2.send_and_verify('ATQ0', 'OK'))

        test.log.info('13. Input Cascading command.')
        test.expect(test.send_command_and_check_echo('at+cops?;+creg?', False, test.dut.at2))
        test.expect('OK' in test.dut.at2.last_response)


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('ATE1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('ATQ0', 'OK'))
        test.expect(test.dut.at2.send_and_verify('ATE1', 'OK'))
        test.expect(test.dut.at2.send_and_verify('ATQ0', 'OK'))

    def send_command_and_check_echo(test, command, echo, port):
        port.send(command,end='\r')
        port.wait_for('COPS: .*CREG: .*')
        if echo == True:
            if command in port.last_response:
                test.log.info('Echo message show, correct')
                return True
            else:
                test.log.error('Echo message should show but not')
                return False
        else:
            if command in port.last_response:
                test.log.error('Echo message should not show' )
                return False
            else:
                test.log.info('Echo message not show, correct ')
                return True

if "__main__" == __name__:
    unicorn.main()
