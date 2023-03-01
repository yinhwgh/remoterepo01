#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC TC0093283.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.security import set_sim_waiting_for_pin1
from dstl.auxiliary.devboard import devboard

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()

    def run(test):
        test.log.info('1.check cfun=0')
        test.log.info('1.1 Restart Module')
        test.dut.dstl_restart()
        test.sleep(10)
        test.log.info('1.2 Check sim status')
        test.dut.at1.send_and_verify('at+cpin?', expect='SIM PIN')
        test.expect(test.dut.at1.send_and_verify('at+cfun?', expect='CFUN: 1'))
        test.log.info('1.3 Set Airplane Mode (at+cfun=0)')
        test.dut.at1.send_and_verify('at+cfun=0')
        test.sleep(3)
        test.log.info('1.4 Check sim status')
        test.expect(test.dut.at1.send_and_verify('at+cfun?', 'CFUN: 0'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='SIM not inserted'))
        test.log.info('1.5 Reset Module using the reset button')
        #test.dut.dstl_reset_with_emergoff_via_dev_board()
        test.reset_by_mctest()
        test.sleep(5)
        test.log.info('1.6 Check Sim status, current cfun, register to network')
        test.expect(test.dut.at1.send_and_verify('at', 'O'))
        test.expect(test.dut.at1.send_and_verify('at+cfun?', expect='CFUN: 1'))
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        #test.expect(test.dut.dstl_register_to_network())

        test.log.info('2.check cfun=4')
        test.log.info('2.1 Restart Module')
        test.dut.dstl_restart()
        test.sleep(10)
        test.log.info('2.2 Check sim status')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='SIM PIN'))
        test.log.info('2.3 Set Airplane Mode (at+cfun=4)')
        test.expect(test.dut.at1.send_and_verify('at+cfun=4'))
        test.sleep(3)
        test.log.info('2.4 Check sim status')
        test.expect(test.dut.at1.send_and_verify('at+cfun?','CFUN: 4'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='SIM PIN'))
        test.log.info('2.5 Reset Module using the reset button')
        #test.dut.dstl_reset_with_emergoff_via_dev_board()
        test.reset_by_mctest()
        test.sleep(5)
        test.log.info('2.6 Check Sim status, current cfun, register to network')
        test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN')
        test.expect(test.dut.at1.send_and_verify('at+cfun?', expect='CFUN: 1'))
        test.sleep(5)
        test.expect(test.dut.dstl_enter_pin())
        #test.expect(test.dut.dstl_register_to_network())

    def cleanup(test):
        test.dut.at1.send_and_verify('at+cfun=1')

    def reset_by_mctest(test):
        test.dut.devboard.send_and_verify('mc:emerg=1')
        test.sleep(1)
        test.dut.devboard.send_and_verify('mc:emerg=0')
        test.sleep(1)
        test.dut.devboard.send_and_verify('mc:igt=3000')
        test.dut.at1.wait_for('SYSSTART')


if "__main__" == __name__:
    unicorn.main()
