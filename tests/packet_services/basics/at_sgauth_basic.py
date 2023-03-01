# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091883.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init


class Test(BaseTest):
    '''
    TC0091883.001 - TpAtSgauthBasic
    Subscriber :1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(2)


    def run(test):
        maxlength = 127
        max_user = 'user' + 'u'*(maxlength-4)
        max_pw = 'passwd'+'p'*(maxlength-6)
        invalid_user = max_user+'1'
        invalid_pw = max_pw +'1'

        test.log.info('1. Check without pin')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))

        test.expect(test.dut.at1.send_and_verify('at^sgauth=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', 'OK'))

        test.log.info('2. Check with pin')
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at^sgauth=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*SGAUTH: 1,0.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=2,"IP","test"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=2,1,"testpwd2","testuser2"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*SGAUTH: 1,0\s+.SGAUTH: 2,1,"testuser2"\s+.*'))

        test.expect(test.dut.at1.send_and_verify('at^sgauth=2,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*SGAUTH: 1,0.*SGAUTH: 2,0.*'))

        test.log.info('3. Check for invalid parameters')
        test.expect(test.dut.at1.send_and_verify('at^sgauth=-1,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=17,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1,-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1,3,"pw"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(' at^sgauth=1,1,"pw",', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(' at^sgauth=1,1,,"user"', 'ERROR'))

        test.log.info('4. Check persistency of parameters')
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1,2,"abc","def"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=2,1,"testaaa3","testbbb3"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*\^SGAUTH: 1,2,"def".*\^SGAUTH: 2,1,"testbbb3".*'))
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*\^SGAUTH: 1,2,"def".*\^SGAUTH: 2,1,"testbbb3".*'))

        test.log.info('5. Check max length')
        test.expect(test.dut.at1.send_and_verify(f'at^sgauth=2,1,"{max_pw}","{max_user}"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', f'.*\^SGAUTH: 2,1,"{max_user}".*'))
        test.expect(test.dut.at1.send_and_verify(f'at^sgauth=2,1,"{max_pw}","{invalid_user}"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'at^sgauth=2,1,"{invalid_pw}","{max_user}"', 'ERROR'))



    def cleanup(test):
        test.log.info('Clear settings for at^sgauth')
        test.expect(test.dut.at1.send_and_verify('at^sgauth=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sgauth?', '.*SGAUTH: 1,0.*SGAUTH: 2,0.*'))



if "__main__" == __name__:
    unicorn.main()
