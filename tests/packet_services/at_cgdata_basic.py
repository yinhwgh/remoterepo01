#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0091873.001

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.call.switch_to_command_mode import *

class Test(BaseTest):
    '''
    TC0091873.001 - TpAtCgdataBasic
    Subscriber :1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.sleep(5)

    def run(test):
        test.log.step('1. Restart module.')
        test.dut.dstl_restart()

        test.log.step('2. Check test command: should not work without pin authentication.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*"))
        check_cgdata(test, 'test', 'CME ERROR: SIM PIN required')

        test.log.step('3. Check write command: should not work without pin authentication.')
        check_cgdata(test, 'write', 'CME ERROR: SIM PIN required', '1')

        test.log.step('4. Register to network.')
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)

        test.log.step('5. Check test command: at+cgdata=? (should return list of supported <L2P>s).')
        check_cgdata(test, 'test', 'OK')

        test.log.step('6. Check exec command: at+cgdata (if supported - should return CONNECT).')
        test.log.step('7. Set valid parameters: (should return CONNECT).')
        test.log.info('Getting max number of PDP contexts')
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", ".*OK.*"))
        max_pdp = int(re.search(r'(CGDCONT: \(\d-)(\d{1,2})', test.dut.at1.last_response).group(2))
        test.log.info('Setting valid APN for next step')
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}"'
                                                 .format(1, test.dut.sim.apn_v4), '.*OK.*'))
        test.log.info('Setting valid APN for next step')
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}"'
                                                 .format(1, test.dut.sim.apn_v4), '.*OK.*'))
        check_cgdata(test, 'write', 'CONNECT', str(1))
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        time.sleep(2)
        test.expect(test.dut.at1.send_and_verify('ATO','.*CONNECT.*'))
        time.sleep(2)
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        time.sleep(3)
        test.expect(test.dut.at1.send_and_verify('ATH', '.*OK.*'))

        test.log.step('8. Set some invalid parameters: (should be rejected).')
        check_cgdata(test, 'test', 'ERROR','1', True)
        check_cgdata(test, 'write', 'ERROR','0', True)
        check_cgdata(test, 'write', 'ERROR',str(max_pdp+1), True)

    def cleanup(test):
        pass


def check_cgdata(test, mode, expected_response, cid = '1', invalid_write_command=False):
    if mode is 'test':
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGDATA=?", ".*\\+CGDATA: \\(\"PPP\"\\).*"))
        elif invalid_write_command:
            test.expect(test.dut.at1.send_and_verify('AT+CGDATA=?{}'.format(cid), ".*{}.*".format(expected_response)))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGDATA=?", ".*{}.*".format(expected_response)))
    elif mode is 'write':
        if expected_response is 'CONNECT':
            test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",{}'.format(cid), ".*CONNECT.*"))
        elif invalid_write_command:
            test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",{}'.format(cid), ".*{}.*".format(expected_response)))
        else:
            test.expect(test.dut.at1.send_and_verify('AT+CGDATA="PPP",{}'.format(cid), ".*{}.*".format(expected_response)))


if "__main__" == __name__:
    unicorn.main()
