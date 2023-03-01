#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0094746.001

import unicorn
import random
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network


class Test(BaseTest):
    '''
    TC0094746.001 - StabilityTest_cfun_0_cfun_1
    Intention: To check DUT stability after using at+cfun=0 and at+cfun=1 commands

    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        time_interval1=random.randint(1,60)
        for i in range(10):
            test.log.info('-----------LOOP {}----------'.format(i+1))
            test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
            t1 = test.thread(test.port_check,test.dut.at1)
            t2 = test.thread(test.port_check,test.dut.at2)
            t1.join()
            t2.join()
            test.expect(test.dut.at1.send_and_verify('at+cfun=0', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cfun?', 'CFUN: 0.*OK'))
            test.sleep(time_interval1 * 60)

    def cleanup(test):
        pass

    def port_check(test,port):

        test.expect(port.send_and_verify('at+cgsn', 'OK'))
        test.expect(port.send_and_verify('ati', 'OK'))

        test.sleep(3)
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_check_network_status())
        test.expect(port.send_and_verify('at+cimi', '\d+.*OK'))
        test.expect(port.send_and_verify('at^spic', 'OK'))
        test.expect(port.send_and_verify('at+cnmi?', 'CNMI: \d,\d,\d,\d,\d.*OK'))
        test.expect(port.send_and_verify('at+cpms?', 'CPMS: .*OK'))
        test.expect(port.send_and_verify('at+cfun?', 'CFUN: 1.*OK'))


if "__main__" == __name__:
    unicorn.main()
