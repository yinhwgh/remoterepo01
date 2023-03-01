#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091875.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.packet_domain import config_pdp_context
from dstl.configuration import set_autoattach
from dstl.security import set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    TC0091875.001 - TpAtCgdscontBasic
    This procedure provides the possibility of basic tests for the test,
     exec and write command of +CGDSCONT

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_disable_ps_autoattach()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.sleep(3)
        test.apn = test.dut.sim.apn_v4

    def run(test):

        test.log.step('1.test without pin')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=16', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=?', 'OK'))

        test.log.step('2.test with pin and function tests')
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()
        max_cid = test.dut.dstl_get_supported_max_cid()
        test_resp = f'.*CGDSCONT: \\(1-{max_cid}\\),\\(.*\\),\\(0-2\\),\\(0-4\\)\s+OK.*'

        test.clear_config()
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=?', test_resp))
        test.expect(
            test.dut.at1.send_and_verify('at+cgdcont=1,\"IP\",\"test\",\"192.192.192.192\",0,0', '.*OK.*'))


        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=7,1,0,0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', '\+CGDSCONT: 7,1,0,0\s+OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=7', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', 'CGDSCONT: \s+OK'))

        test.log.step('3.check invalid parameter')
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=8,1,0,5', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=8,1,3,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=9,1,-1,2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=9,1,0,-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=7,-1,0,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGDSCONT=7,{max_cid+1},0,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=-1,1,0,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=1,2,1,0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=1,2,0,2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=0', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT=1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'AT+CGDSCONT={max_cid+1},1', 'ERROR'))


    def cleanup(test):
        test.dut.at1.send_and_verify(f'at+cgdcont=1,\"IP\",\"{test.apn}\"', '.*OK.*')
        test.expect(test.dut.dstl_enable_ps_autoattach())
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def clear_config(test):
        test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', 'OK'))
        res = test.dut.at1.last_response
        configed = re.findall('\+CGDSCONT: (\d+),',res)
        if configed:
            for id in configed:
                test.expect(test.dut.at1.send_and_verify(f'AT+CGDSCONT={id}', 'OK'))






if (__name__ == "__main__"):
    unicorn.main()
