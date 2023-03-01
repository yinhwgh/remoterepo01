#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0094508.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
    TC0094508.001 - TpAtCgeqosrdpBasic
    This procedure provides the possibility of basic tests for the test,
     exec and write command of +CGEQOSRDP

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.apn = test.dut.sim.apn_v4


    def run(test):

        test.log.info('1.test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=?', '.*\+CME ERROR: 11.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP', '.*\+CME ERROR: 11.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=', '.*\+CME ERROR: 11.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=1', '.*\+CME ERROR: 11.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=17', '.*\+CME ERROR: 11.*'))

        test.log.info('2.test with pin')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IPV4V6","{}"'.format(test.apn), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=5,"IPV4V6","{}"'.format(test.apn), 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=?', '.*CGEQOSRDP: 1.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=1', '.*CGEQOSRDP: 1,.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP', '.*CGEQOSRDP: 1.*OK.*|ERROR'))

        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=5', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=5', '.*ERROR.*'))


        test.log.info('3.check invalid parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP?', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=1,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOSRDP=17', '.*ERROR.*'))



    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
