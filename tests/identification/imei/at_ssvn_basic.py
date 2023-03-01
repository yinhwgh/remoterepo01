#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0092545.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.security import set_sim_waiting_for_pin1
from dstl.network_service import register_to_network

class Test(BaseTest):
    '''
    Basic tests for the exec command of AT^SSVN for Customer IMEI  modules only.
    '''
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()

    def run(test):
        resp_ssvn_read_cmd = '\\d+.*OK.*'

        if test.dut.project == 'VIPER':
            resp_ssvn_read_cmd = '.*\\d\\s+OK.*|.*ERROR.*'


        test.log.info('1.check without pin')
        test.expect(test.dut.at1.send_and_verify('at^ssvn=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn?', resp_ssvn_read_cmd))
        test.expect(test.dut.at1.send_and_verify('at^ssvn=10', 'OK|ERROR'))

        test.log.info('2.check with pin')
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at^ssvn=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn?', resp_ssvn_read_cmd))
        test.expect(test.dut.at1.send_and_verify('at^ssvn=10', 'OK|ERROR'))

        test.log.info('3.check invalid parameters')
        test.expect(test.dut.at1.send_and_verify('at^ssvn=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn=a', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn=100', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn=\"1\"', 'ERROR'))

    def cleanup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()