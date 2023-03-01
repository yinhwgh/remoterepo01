#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091881.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain.config_pdp_context import dstl_get_supported_max_cid


class Test(BaseTest):
    """
    TC0091881.001 - AtCgeqreqBasic
    This procedure provides the possibility of basic tests for the test,
    exec and write command of +CGEQREQ
    (current only test VIPER)

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.apn = test.dut.sim.apn_v4


    def run(test):

        if test.dut.platform.upper() == 'QCT':
            no_pin_protect = True
            is_qct = True
        else:
            no_pin_protect = False
            is_qct = False
        max_cid = test.dut.dstl_get_supported_max_cid()
        para_list = '.*\\(0-4\\),\\(0-11520\\),\\(0-42200\\),\\(0-11520\\),\\(0-42200\\),\\(0-2\\),\\(0,10-1520,1502\\),\\(\"0E0\",\"1E1\",\"1E2\",\"7E3\",\"1E3\",\"1E4\",\"1E5\",\"1E6\"\\),\\(\"0E0\",\"5E2\",\"1E2\",\"5E3\",\"4E3\",\"1E3\",\"1E4\",\"1E5\",\"1E6\",\"6E8\"\\),\\(0-3\\),\\(0,100-150,200-950,1000-4000\\),\\(0-3\\).*'
        resp_test_cmd = '.*CGEQREQ: \"IP\"'+para_list+'.*CGEQREQ: \"PPP\"'+para_list+'.*CGEQREQ: \"IPV6\"'+para_list+'.*CGEQREQ: \"IPV4V6\"'+para_list+'.*OK.*'

        test.log.step('1.test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        if no_pin_protect:
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq=?', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*OK.*'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq=?', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1', '.*ERROR.*'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*ERROR.*'))

        test.log.step('2.test with pin')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        test.log.info('*** 2.1 checking read,write,test command ***')
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=?', resp_test_cmd))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '\+CGEQREQ:\s+OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,0,0,0,0,2,0,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,0,0,0,2,0,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,0,0,2,0,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,0,2,0,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,2,0,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,0,"0E0","0E0",3,0,0.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"0E0","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"1E2","0E0",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"1E2","5E3",3,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"1E2","5E3",1,0,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,950', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"1E2","5E3",1,950,0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,3000,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '.*\+CGEQREQ: 1,4,128,128,128,128,1,10,"1E2","5E3",1,3000,1.*OK.*'))

        test.log.step('*** 2.2 checking nested brackets ***')

        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,,,,,,,,,,,,1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?',
                                                 '.*\+CGEQREQ: 1,4,0,0,0,0,2,0,"0E0","0E0",3,0,1.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,0,', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq?','.*\+CGEQREQ: 1,0,0,0,0,0,2,0,"0E0","0E0",3,0,0.*OK.*'))


        test.log.step('3.check invalid parameter')
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=17', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,1000,-1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,1000,4', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,3851,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",1,4001,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,511,128,128,128,3,1520,"1E2","5E3",3,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,129,128,128,128,3,1520,"1E2","5E3",3,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",-1,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","5E3",4,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"8E2","5E3",-1,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,4,128,128,128,128,1,10,"1E2","8E3",3,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=1,-1,128,128,128,128,3,1520,"1E2","5E3",3,100,1', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqreq=-1,1,128,128,128,128,3,1520,"1E2","5E3",3,100,1', '.*ERROR.*'))

        test.log.step('4. clear up all profiles')
        for i in range(1, max_cid+1):
            test.expect(test.dut.at1.send_and_verify(f'at+cgeqreq={i}', '.*OK.*'))



    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
