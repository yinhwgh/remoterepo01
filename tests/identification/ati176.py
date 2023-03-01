# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0092333.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init

import re


class Test(BaseTest):
    '''
   	TC0092333.001 - ATI176
    Intetntion of this TC is to test if module returns correct answer when the ati176 command is issued.
    TC is designed to the format: <IMEI><CheckDigit>.<SVN> (with dot)
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        expect_format='\d{15}\s+OK'
        imei = '\d{15}'
        test.log.info('1. Send at+gsn command, module should return a response with following content: <sn> - IMEI')
        match_format = test.dut.at1.send_and_verify('AT+GSN', expect_format)
        if match_format:
            test.log.info("AT+GSN response matches with expect format.")
            imei = re.findall("(\d{15})\s+OK", test.dut.at1.last_response)[0]
        else:
            test.log.error(f"AT+GSN response does not match format {expect_format}.")
        

        test.log.info('2. Send at+cgsn command, module should return a response with following content: <sn> - IMEI')
        test.expect(test.dut.at1.send_and_verify('AT+CGSN', f'{imei}\s+OK'))
        

        test.log.info('3. Send ati176 command, module should return a response with following content:<IMEI><CheckDigit>.<SVN>')
        imei_svn = f'{imei}\.\d\d\s+OK'
        test.expect(test.dut.at1.send_and_verify('ATI176', f'{imei}\.\d\d\s+OK'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
