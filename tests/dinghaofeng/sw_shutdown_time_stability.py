# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108212.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
import time

shutdown_times = []
fsd_times = []


class Test(BaseTest):
    """
       TC0108212.001 - SWShutDownTimeStability
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify("mc:urc=off", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.sleep(2)

    def run(test):
        for i in range(10):
            test.log.step("1. Send AT^SMSO command and check shutdown urc")
            test.expect(test.dut.dstl_shutdown_smso())
            urc_shutdown = time.time()

            test.log.step("2. Using McTest check if module is Off(MC:PWRIND) with in 1s after URC pop out")
            test.expect(test.dut.devboard.wait_for('.*PWRIND: 1.*'))
            # test.expect(test.dut.devboard.send_and_verify('MC:PWRIND', '.*PWRIND: 1.*', wait_for='.*PWRIND: 1.*', timeout=1), critical=True)
            urc_pwrind = time.time()

            test.log.step("3. Using McTest measurement module shutdown time")
            every_loop_time = urc_pwrind-urc_shutdown
            print('every_loop_time: ', every_loop_time)
            shutdown_times.append(every_loop_time)
            test.sleep(2)

            test.log.step("4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(2)

            test.log.step("5. Send AT command to check if communication with module is possible")
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK"))
        print(shutdown_times)
        between_shutdown_times = max(shutdown_times) - min(shutdown_times)
        print("The difference between the maximum and the minimum :", between_shutdown_times)
        test.expect(between_shutdown_times <= 1, msg="The difference shutdown_times between the maximum and the minimum > 1s")

        for i in range(10):
            test.log.step("6. Send command AT^SMSO=fast")
            test.expect(test.dut.at1.send("AT^SMSO=fast"))
            urc_shutdown = time.time()

            test.log.step("7. Using McTest check if module is Off(MC:PWRIND)")
            test.expect(test.dut.devboard.wait_for('.*PWRIND: 1.*'))
            urc_pwrind = time.time()

            test.log.step("8. Using McTest measurement module shutdown time")
            every_loop_time = urc_pwrind - urc_shutdown
            print('every_loop_time: ', every_loop_time)
            fsd_times.append(every_loop_time)
            test.sleep(2)

            test.log.step("9. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.dut.at1.wait_for('.*SYSSTART.*')
            test.sleep(2)

            test.log.step("10. Send AT command to check if communication with module is possible")
            test.expect(test.dut.at1.send_and_verify("AT", ".*OK"))
        print(fsd_times)
        between_fsd_times = max(fsd_times) - min(fsd_times)
        print("The difference between the maximum and the minimum :", between_fsd_times)
        test.expect(between_fsd_times <= 1, msg="The difference fsd_times between the maximum and the minimum > 1s")

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


if "__main__" == __name__:
    unicorn.main()
