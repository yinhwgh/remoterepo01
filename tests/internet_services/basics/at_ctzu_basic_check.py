#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class at_ctzu_basic_check(BaseTest):
    def setup(test):
        test.dut.dstl_detect()


    def run(test):
        test.log.info("1. test: check test, read and write command without PIN")
        test.expect(test.dut.at1.send_and_verify('at+ctzu=?', '.*CTZU: \\(0[,-]1\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*CTZU: [01].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*CTZU: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*CTZU: 0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr=0', '.*OK.*'))

        test.log.info("2. test: check test, read and write command with PIN")
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify('at+ctzu=?', '.*CTZU: \\(0[,-]1\\).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*CTZU: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=0', '.*OK.*'))

        test.log.info("3. test: check AT+CTZU  command with invalid parameters ")
        test.expect(test.dut.at1.send_and_verify('at+ctzu=-1', '.*ERROR\\s+'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=-2', '.*ERROR\\s+'))

        test.log.info('4. test: Functional Test')
        test.expect(test.dut.at1.send_and_verify('at+cops?', '.*\\+COPS: .*,.*,.*,[0379].*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgatt?', '.*OK.*'))
        if('+CGATT: 1' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*[+]CTZU: \"[\\d/]{8},\\d+:\\d+:\\d+\",[-+]\\d\\d?,\\d.*',wait_for='CTZU',timeout=90)

        test.log.info('*** Test CTZR=1 ***')
        test.log.info('*** Set airplane mode ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '.*OK.*\\^SYSSTART AIRPLANE MODE.*'))
        test.expect(test.dut.at1.send_and_verify('at+cereg=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr=?', '.*CTZR: \\(0.*3\\)\\s+OK\\s+'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 2' in test.dut.at1.last_response or '+CTZR: 3' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*OK.*'))
        if ('+CTZU: 0' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzu=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', '.*OK.*\\^SYSSTART.*'))

        test.log.info('*** Test CTZR=2 ***')
        test.log.info('*** Set airplane mode ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '.*OK.*\\^SYSSTART AIRPLANE MODE.*'))
        test.expect(test.dut.at1.send_and_verify('at+cereg=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr=?', '.*CTZR: \\(0.*3\\)\\s+OK\\s+'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 1' in test.dut.at1.last_response or '+CTZR: 3' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*OK.*'))
        if ('+CTZU: 0' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzu=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', '.*OK.*\\^SYSSTART.*'))

        test.log.info('*** Test CTZR=3 ***')
        test.log.info('*** Set airplane mode ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', '.*OK.*\\^SYSSTART AIRPLANE MODE.*'))
        test.expect(test.dut.at1.send_and_verify('at+cereg=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr=?', '.*CTZR: \\(0.*3\\)\\s+OK\\s+'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 1' in test.dut.at1.last_response or '+CTZR: 2' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=3', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu?', '.*OK.*'))
        if ('+CTZU: 0' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzu=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', '.*OK.*\\^SYSSTART.*'))

        test.log.info('5. test: Functional Test after changing time')
        test.expect(test.dut.at1.send_and_verify('at+cereg=2', '.*OK.*'))

        test.log.info('*** Test CTZR=1 ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 2' in test.dut.at1.last_response or '+CTZR: 3' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=1', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*[+]CEREG: [02]', wait_for='CEREG', timeout=90)

        test.expect(test.dut.at1.send_and_verify('"at+cclk=\"14/02/12,21:14:25+00\"', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*[+]CTZV:.*[-+]\\d+.*', wait_for='CTZV', timeout=90)
        # test.expect(test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*'))
        # test.log.info('*** Note: Waiting for registering to network and updating time.')
        # if re.search('.*[+]CTZV:.*[-+]\\d+.*', test.dut.at1.last_response, re.I | re.M) is None:
        #     test.expect(test.dut.at1.wait_for('.*[+]CTZV:.*[-+]\\d+.*'))
        # else:
        #     test.log.info('PASS: CTZV URC is matched.')

        test.log.info('*** Test CTZR=2 ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 1' in test.dut.at1.last_response or '+CTZR: 3' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=2', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*[+]CEREG: [02].*', wait_for='CEREG', timeout=90)

        test.expect(test.dut.at1.send_and_verify('"at+cclk=\"14/02/12,21:14:25+00\"', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*[+]CTZE: [-+]\\d+,\\d+,\"\\d+/\\d+/\\d+,\\d+:\\d+:\\d+\".*', wait_for='CTZE', timeout=90)

        test.log.info('*** Test CTZR=3 ***')
        test.expect(test.dut.at1.send_and_verify('at+ctzr?', '.*OK.*'))
        if ('+CTZR: 0' in test.dut.at1.last_response or '+CTZR: 1' in test.dut.at1.last_response or '+CTZR: 2' in test.dut.at1.last_response):
            test.expect(test.dut.at1.send_and_verify('at+ctzr=3', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*[+]CEREG: [02].*', wait_for='CEREG', timeout=90)

        test.expect(test.dut.at1.send_and_verify('"at+cclk=\"14/02/12,21:14:25+00\"', '.*OK.*'))
        test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*[+]CTZEU: [-+]\\d+,\\d+,\"\\d+/\\d+/\\d+,\\d+:\\d+:\\d+\".*',wait_for='CTZEU', timeout=90)

        test.expect(test.dut.at1.send_and_verify('at+ctzu=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ctzr=0', '.*OK.*'))
        test.log.info('*** END TEST ***')
    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
