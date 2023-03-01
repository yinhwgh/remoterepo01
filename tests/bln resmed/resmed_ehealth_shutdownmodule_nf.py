#responsible: hongwei.yin@thalesgroup.com
#location: Dalian
#TC0107795.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary import restart_module


class Test(BaseTest):
    """
       TC0107795.001 - Resmed_eHealth_ShutDownModule_NormalFlow
    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.step("1. Enable GPIO FSR")
        test.dut.dstl_turn_off_dev_board_urcs()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "GPIO/mode/FSR",std', 'OK'))
        test.dut.dstl_set_urc(urc_str="PWRIND")
        # change takes effect after restart module
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):
        test.log.step("2. Triggers the module's fast shutdown line once a main's voltage drop is detected")
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_for='OK'))
        test.dut.devboard.send('mc:gpio3cfg=0')
        test.expect(test.dut.devboard.wait_for('>URC:  PWRIND: 1'))
        test.dut.devboard.send('MC:VBATT=OFF')
        test.log.step("3. Power off supply after 15ms fast shutdown"
                      "(.ie if the power can hold more then 15ms after shutdown the test will be fail)")
        test.sleep(1)
        test.dut.devboard.send('mc:gpio3cfg=1')
        test.dut.devboard.send('MC:VBATT=ON')
        test.expect(test.dut.devboard.send_and_verify("MC:IGT=1000", ".*SYSSTART.*", wait_for=".*SYSSTART.*"))
        test.dut.devboard.send_and_verify('mc:pwrind?')
        test.sleep(10)

    def cleanup(test):
        test.dut.devboard.send('mc:gpiocfg=3,inp')


if "__main__" == __name__:
    unicorn.main()
