#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0104948.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
    TC0104948.001 - AtCeerWrongAPN
    This procedure provides basic PS errors for the test
    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_gsm()
        test.sleep(3)


    def run(test):
        test.log.info('1.1 PS network cause: "Requested service option not subscribed"')
        test.expect(test.dut.at1.send_and_verify('at+CMEE=2', 'OK'))
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=8,"IPV4V6","WRONG"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,8', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: Requested service option not subscribed'))
        test.expect(test.dut.at1.send_and_verify('at+ceer=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: No cause information available'))

        test.log.info('1.2 PS internal cause: "PDP lowerlayer error"')
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=8', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact=1,8', 'ERROR|OK'))
        if 'invalid index' in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: No cause information available'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: PDP lowerlayer error'))
            test.expect(test.dut.at1.send_and_verify('at+ceer=0', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+ceer', 'CEER: No cause information available'))


    def cleanup(test):
        pass





if (__name__ == "__main__"):
    unicorn.main()
