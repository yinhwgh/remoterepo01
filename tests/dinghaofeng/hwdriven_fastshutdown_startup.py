# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108213.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
import random
import re


class Test(BaseTest):
    """
       TC0108213.001 - HWDrivenFastShutdownStartup
    """

    def setup(test):
        bulk_tester_detect(test)
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=out', 'OK', wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=1', 'OK', wait_for=".*OK.*")

    def run(test):
        main_process(test)

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


def bulk_tester_detect(test):
    # detect module type automatically because dstl_detect() does not work with BulkTester
    test.dut.devboard.send_and_verify("at^cicret=swn", ".*OK.*", wait_for=".*OK.*")
    prj = ""
    sw = ""
    for line in test.dut.devboard.last_response.splitlines():
        if (line.count('_') > 1 and "RELEASE" in line):
            prj = line[line.index(' '):line.index('_')]
            sw = line.split(' ')[1]
            test.log.info("Found project: " + prj + " with FW: " + sw)


def main_process(test):
    for i in range(100000):
        test.log.step(f'loop times {i+1}')
        test.num_of_modules = 5
        test.check_duts = [False for i in range(test.num_of_modules)]
        test.sleep(random.randint(0, 10))
        test.dut.devboard.send_and_verify('mc:gpio5=0', 'OK', wait_for=".*OK.*")
        test.sleep(1)
        test.dut.devboard.send_and_verify("mc:gpio5=1")
        test.dut.devboard.send_and_verify("mc:igt=1000")
        test.sleep(60)
        test.expect(test.dut.devboard.wait_for('.*SYSSTART.*'))
        sysstart_count = re.findall(".*SYSSTART.*", test.dut.devboard.last_response)
        print('sysstart_count: ', sysstart_count)
        for i in sysstart_count:
            index = int(i[4])
            test.check_duts[index - 1] = True
        for i in range(test.num_of_modules):
            if test.check_duts[i] == True:
                test.log.info("DUT " + str(i + 1) + " lives")
            else:
                test.log.error("DUT " + str(i + 1) + " did not send SYSSTART")


if "__main__" == __name__:
    unicorn.main()
