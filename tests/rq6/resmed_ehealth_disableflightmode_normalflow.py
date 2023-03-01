# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107792.001 according to RQ6000061.001

import unicorn
from core.basetest import BaseTest
import resmed_ehealth_initmodule_normal_flow


class Test(BaseTest):
    """
       TC0107792.001 - Resmed_eHealth_DisableFlightMode_NormalFlow
    """

    def setup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', 'OK\r\n'))

    def run(test):
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK', wait_for='OK'))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK', wait_for='OK'))
        test.expect(test.dut.devboard.send_and_verify('MC:igt=10', 'OK', wait_for='OK'))
        test.sleep(1.5)
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
