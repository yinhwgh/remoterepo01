# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0105078.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import functionality_modes
from dstl.usim.sset_mode_control import dstl_wait_for_pin_ready


class Test(BaseTest):
    """
    TC0105078.001 - ATI176_PIN_airplane_Check
    Intention:
    This procedure provides tests for ATI176.
    Subscriber: 1
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()

    def run(test):
        expect_format = '\d{15}\.\d{2}\s+OK'
        test.log.info('1. Restart module and keep pin locked')
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))

        test.log.info('2. Query command ATI176')
        test.expect(test.dut.at1.send_and_verify('ati176', expect_format))

        test.log.info('3. Unlock pin')
        test.expect(test.dut.dstl_enter_pin())

        # hier war schon At^SSET  drin, und SSIM READY ist ja der URC für die SIM, wenn SIM BUSY beendet ist.
        test.dut.dstl_wait_for_pin_ready()
        # def dstl_wait_for_sim_ready(device, cmd='AT+CPIN?', exp_resp='.*(SIM PIN|READY).*'):
        # def dstl_wait_for_pin_ready(device, cmd='AT+CLCK="SC",2', exp_resp='.*(SIM PIN|READY).*'):

        test.log.info('4. Query command ATI176')
        test.expect(test.dut.at1.send_and_verify('ati176', expect_format))

        test.log.info('5. Make module enter airplane mode')
        test.expect(test.dut.dstl_set_airplane_mode())

        test.log.info('6. Query command ATI176')
        test.expect(test.dut.at1.send_and_verify('ati176', expect_format))

        test.log.info('7. Exist airplane mode')
        test.expect(test.dut.dstl_set_full_functionality_mode())

        test.log.info('8. Check some invalid value')
        test.expect(test.dut.at1.send_and_verify('ati176.6', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ati176bb', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ati176##', 'ERROR'))

    def cleanup(test):
        test.log.info('***Test End, clean up***')


if "__main__" == __name__:
    unicorn.main()
