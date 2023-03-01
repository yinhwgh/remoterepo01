#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0107347.001


import unicorn
import time

from core.basetest import BaseTest
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary import restart_module
import random


class Test(BaseTest):
    """
    Test which presents basic use of DSTL functions
    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.step('1.Prepare')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "GPIO/mode/FSR",std', 'OK'))
        test.dut.dstl_restart()

    def run(test):
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp','OK'))

        for i in range(1, 50000):
            test.log.info(f'Start test loop {i}')
            wait_time=random.randint(3, 20)
            test.log.info(f'Current loop wait time : {wait_time}')
            test.sleep(wait_time)
            test.log.step('2.fast shut down between 3-20s after ignition by Mctst4 GOIO4')
            test.dut.devboard.send('mc:gpio3cfg=0')
            test.dut.devboard.send('mc:gpio3cfg=1')

            test.log.step('3.Cut down power 15ms after step2')
            test.expect(
                test.dut.devboard.send_and_verify('mc:vbatt=off', 'OK'))
            test.expect(
                test.dut.devboard.send_and_verify('mc:vbatt=on', 'OK'))
            test.expect(
                test.dut.devboard.send_and_verify('mc:igt=1000', 'OK'))
            test.expect(test.dut.devboard.send_and_verify('MC:PWRIND','.*PWRIND: 0.*'))


    def cleanup(test):
        test.dut.devboard.send('mc:gpiocfg=3,inp')




if "__main__" == __name__:
    unicorn.main()
