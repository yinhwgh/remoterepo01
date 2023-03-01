# responsible: hongwei.yin@thalesgroup.com
# location: Dalian


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
import time

shutdown_times = []
sysstart_times = []
at_times = []
simready_times = []
duration_time = 24 * 60 * 60


class Test(BaseTest):
    """
       check sysstart time if become longer after reboot many times.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify("mc:urc=off", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.sleep(2)

    def run(test):
        i = 1
        start_time = time.time()
        while time.time() - start_time < duration_time:
            test.log.info(f"This is {i} loop.")
            test.log.step("1. Send AT^SMSO command and check shutdown urc")
            test.expect(test.dut.dstl_shutdown_smso(), critical=True)
            urc_shutdown = time.time()

            test.log.step("2. Using McTest check if module is Off(MC:PWRIND) with in 1s after URC pop out")
            test.expect(test.dut.devboard.wait_for('.*PWRIND: 1.*', timeout=3))
            # test.expect(test.dut.devboard.send_and_verify('MC:PWRIND', '.*PWRIND: 1.*', wait_for='.*PWRIND: 1.*', timeout=1), critical=True)
            urc_pwrind = time.time()

            test.log.step("3. Using McTest measurement module shutdown time")
            every_shutdown_time = urc_pwrind-urc_shutdown
            print('every_shutdown_time: ', every_shutdown_time)
            shutdown_times.append(every_shutdown_time)
            test.expect(
                test.dut.devboard.send_and_verify('mc:vbatt=off', 'OK'))
            test.expect(
                test.dut.devboard.send_and_verify('mc:vbatt=on', 'OK'))
            test.sleep(2)

            test.log.step("4. Turn On module (MC:IGT=1000) and wait for ^SYSSTART")
            urc_igt = time.time()
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
            test.expect(test.dut.at1.wait_for('.*SYSSTART.*'), critical=True)
            urc_sysstart = time.time()
            every_sysstart_time = urc_sysstart - urc_igt
            print('every_sysstart_time: ', every_sysstart_time)
            sysstart_times.append(every_sysstart_time)
            if 'SSIM READY' in test.dut.at1.last_response:
                print('every_simready_time: ', every_sysstart_time)
                simready_times.append(every_sysstart_time)

                test.log.step("5. Send AT command to check if communication with module is possible")
                # test.expect(test.dut.at1.send_and_verify("AT", ".*OK", append=True))
                print('last_response: ', test.dut.at1.last_response)
                result = False
                while not result:
                    test.dut.at1.send("AT")
                    result = test.dut.at1.wait_for("OK", timeout=0.5, append=True)
                urc_at = time.time()
                every_at_time = urc_at - urc_igt
                print('every_at_time: ', every_at_time)
                at_times.append(every_at_time)

            else:
                test.log.step("5. Send AT command to check if communication with module is possible")
                # test.expect(test.dut.at1.send_and_verify("AT", ".*OK", append=True))
                print('last_response: ', test.dut.at1.last_response)
                result = False
                while not result:
                    test.dut.at1.send("AT")
                    result = test.dut.at1.wait_for("OK", timeout=0.5, append=True)
                urc_at = time.time()
                every_at_time = urc_at - urc_igt
                print('every_at_time: ', every_at_time)
                at_times.append(every_at_time)

                test.log.step("6. wait for the presentation of sim urc")
                test.expect(test.dut.at1.wait_for('SSIM READY', append=True), critical=True)
                urc_simready = time.time()
                every_simready_time = urc_simready - urc_igt
                print('every_simready_time: ', every_simready_time)
                simready_times.append(every_simready_time)

                print('last_response: ', test.dut.at1.last_response)
            i = i + 1
            if i%250==0:
                print(f'sysstart_times in loop {i}: ', sysstart_times)
            test.sleep(5)


        print('shutdown_times: ', shutdown_times)
        print('sysstart_times: ', sysstart_times)
        print('at_times: ', at_times)
        print('simready_times: ', simready_times)

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")



if "__main__" == __name__:
    unicorn.main()
