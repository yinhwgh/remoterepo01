#responsible: hongwei.yin@thalesgroup.com
#location: Dalian
#TC0107599.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.network_service.register_to_network import dstl_enter_pin
import random
import time


class Test(BaseTest):
    """
       TC0107599.003 - Flash_Recovering_fastshutdown
    """

    def setup(test):
        dstl_detect(test.dut)
        test.sleep(2)

    def run(test):
        every_loop_time = 0
        time_start = time.time()

        while every_loop_time <= 86400:
            test.log.step("1. Check pin if ready")
            test.expect(dstl_enter_pin(test.dut))
            test.log.step("2. Set phonebook is SM")
            test.expect(test.dut.at1.send_and_verify("AT+CPBS=SM", ".*OK.*"))
            runnum = random.randint(1, 20)
            for i in range(runnum):
                test.log.info(f'Start {i+1} loop!')
                test.log.step("3. Edit phonebook(.eg write read and delete)")
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i+1},'13012345678',,'test{i+1}'", ".*OK.*"))
                test.sleep(3)
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBR={i + 1}", ".*OK.*"))
                test.sleep(3)
                test.expect(test.dut.at1.send_and_verify(f"AT+CPBW={i + 1}", ".*OK.*"))
                test.sleep(3)
            # During these operations shutdown module via at^smso at random intervals (between 0 and 180 seconds).
            test.log.step("4. Send AT^SMSO=? And check response")
            test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK"), critical=True)
            test.log.step("5. Send AT^SMSO command")
            test.expect(dstl_shutdown_smso(test.dut))
            test.log.step("6. Using McTest check if module is turned off ")
            test.expect(test.dut.devboard.send_and_verify('MC:PWRIND', '.*PWRIND: 1.*',wait_after_send=3))
            # Turn on module after randomly chosen intervals (between 0 and 60 seconds).
            test.sleep(random.randint(0, 60))
            test.log.step("7. Turn On module")
            test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(30)
            time_end = time.time()
            every_loop_time = time_end - time_start
        print('---------------', every_loop_time, '---------------')



    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
