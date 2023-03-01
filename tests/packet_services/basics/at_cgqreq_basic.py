#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091879.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
    TC0091879.001 - AtCgqreqBasic
    This procedure provides the possibility of basic tests for the test
    and write command of +CGQREQ.

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)

    def run(test):
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))

        if test.dut.platform == 'QCT':
            test.qct_check()
        else:
            test.no_qct_check()



    def cleanup(test):
        pass


    def qct_check(test):
        test.log.step('1.check test, read and write commands without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))

        test.log.step('2.check test, read and write commands with PIN')
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/AutoAttach","disabled"', '.*OK.*'))
        test.dut.dstl_restart()
        test.sleep(3)
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=?', '.*\+CGQREQ: "IP",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\).*OK.*'))

        test.log.step('3.check if there is possible to set command with all supported parameters')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,1,1,1,1,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=2,0,0,0,0,0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*CGQREQ: 1,1,1,1,1,1.*CGQREQ: 2,0,0,0,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*CGQREQ: \s+OK.*'))

        test.log.step('4. check command with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=-1,1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=17,1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,-1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,4,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,1,-1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,D,1,1,1,1', '.*ERROR.*'))

    def no_qct_check(test):
        test.log.step('1.check test, read and write commands without PIN')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*ERROR.*'))

        test.log.step('2.check test, read and write commands with PIN')
        test.dut.dstl_enter_pin()
        test.log.step('3. clear all cids first')
        for i in range(1,17):
            test.dut.at1.send_and_verify(f'at+cgdcont={i}', '.*OK.*')
        test.log.step('4. read the actual value -> test command')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=?', '.*\+CGQREQ: "IP",\(0-3\),\(0-4\),\(0-5\),\(0-9\),\(0-18,31\).*OK.*'))
        test.log.step('5. read the actual value -> read command')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*OK.*'))
        test.log.step('6. write command with ip and <cid> 1')
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,\"IP\",\"www.test.com\",\"192.192.192.192\",0,0', '.*OK.*'))
        test.log.step('7. set values for profile 1 <cid> 1')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,1,1,1,1,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '.*CGQREQ: 1,1,1,1,1,1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1', '.*OK.*'))
        test.log.step('8. check command with invalid values')
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=-1,1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=17,1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,-1,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,4,1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,1,-1,1,1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgqreq=1,D,1,1,1,1', '.*ERROR.*'))


if __name__ == "__main__":
    unicorn.main()
