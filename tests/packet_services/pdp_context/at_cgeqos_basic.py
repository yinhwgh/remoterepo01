#responsible: xizhu.zhao@thalesgroup.com
#location: Dalian
#TC0094324.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.security import set_sim_waiting_for_pin1
from dstl.network_service import register_to_network
from dstl.configuration import set_autoattach

import re

class AtCgeqosBasic(BaseTest):
    """
    TC0094324.001 - TpAtCgeqosBasic
    Intention:   This procedure provides the possibility of basic tests for the test, read and write command of +CGEQOS.

    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("init the test ")
        test.dut.dstl_enable_ps_autoattach()
        test.dut.dstl_set_sim_waiting_for_pin1()

    def run(test):

        test.log.step("**1.Check command without PIN ")
        test.dut.at1.send_and_verify('AT+cmee=2','OK')
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos?', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=1', '.*OK.*'))

        test.log.step("**2.Check command with PIN")
        test.dut.dstl_enter_pin()

        test.log.step("*2.1 Valid Value")
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=?', '.*\+CGEQOS: \(1-\d+\),\(0-9\),\(.*\),\(.*\),\(.*\),\(.*\).*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos?', '.*CGEQOS.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=1', 'OK'))

        test.log.info("*2.2  Invalid Value")
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=0', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=-1', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=18', '.*CME ERROR.*'))

        test.log.info("**2.3.Check command with more than one CID")
        test.dut.at1.send_and_verify('AT+CGDCONT=7,"IP","internet"', 'OK')
        test.dut.at1.send_and_verify('AT+CGDCONT=8,"IP","test"', 'OK')
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", 'OK'))
        cids = re.findall("\+CGDCONT: (\d+),", test.dut.at1.last_response)
        test.log.info(f"Found cids: {cids}")
        for i in range(1,17):
            if str(i) in cids:
                test.expect(test.dut.at1.send_and_verify(f'at+cgeqos={i}', 'OK'))
            else:
                test.expect(test.dut.at1.send_and_verify(f'at+cgeqos={i}', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=0', '.*CME ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgeqos=17', '.*CME ERROR.*'))


    def cleanup(test):
        test.log.info("**3.test completed ")
        test.dut.at1.send_and_verify('AT&F', 'OK')
        for i in range(7, 9):
            test.dut.at1.send_and_verify('at+cgdcont='+str(i),'OK')


if (__name__ == "__main__"):
    unicorn.main()
