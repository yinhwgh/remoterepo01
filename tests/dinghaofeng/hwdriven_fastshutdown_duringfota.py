# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108216.001

import unicorn
from core.basetest import BaseTest
import random
import re
import threading

module_version = 'LYNX_100_038B'


class Test(BaseTest):
    """
       TC0108216.001 - HWDrivenFastShutdownDuringFOTA
    """

    def setup(test):
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=out', 'OK', wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=1', 'OK', wait_for=".*OK.*")
        test.modules_on = 1

    def run(test):
        main_process(test)

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


def send_at_cmd(test, cmd):
    if (test.modules_on == 1):
        test.dut.devboard.send_and_verify(cmd)
    else:
        test.log.info("AT port not available, waiting...")
        test.sleep(3)


def send_wait_for(test, expect, timeout):
    if (test.modules_on == 1):
        test.dut.devboard.wait_for(expect, timeout)
    else:
        test.log.info("AT port not available, waiting...")
        test.sleep(3)


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


def upgrade(test):
    test.log.info("Start upgrade")
    test.expect(send_at_cmd(test,
        'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.808_arn01.000.00_lynx_100_038_to_rev00.042_arn01.000.00_lynx_100_028b_resmed_prod02sign.usf"'))
    test.expect(send_at_cmd(test,
        'at^snfota="CRC","852b7532d11eecb3f3a2d7a1e731a6d50cf7b93c5cc76bd4fabb77241379c42c"'))
    test.expect(send_at_cmd(test, 'at^snfota="act",2'))
    send_wait_for(test, "\\^SNFOTA:act,0,0,100", timeout=180)  #replace of test_sleep, avoid interface conflict
    test.expect(send_at_cmd(test, 'AT^SFDL=2'))
    test.expect(send_wait_for(test, '^SYSSTART', timeout=900))
    test.sleep(5)


def downgrade(test):
    test.log.info("Start downgrade")
    test.expect(test.dut.devboard.send_and_verify(
        'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.808_arn01.000.00_lynx_100_038_to_rev00.042_arn01.000.00_lynx_100_028b_resmed_prod02sign.usf"'))
    test.expect(test.dut.devboard.send_and_verify(
        'at^snfota="CRC","852b7532d11eecb3f3a2d7a1e731a6d50cf7b93c5cc76bd4fabb77241379c42c"'))
    test.expect(test.dut.devboard.send_and_verify('at^snfota="act",2'))
    test.dut.devboard.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
    test.expect(test.dut.devboard.send_and_verify('AT^SFDL=2'))
    test.expect(test.dut.devboard.wait_for('^SYSSTART', timeout=900))
    test.sleep(5)


def main_process(test):
    for i in range(100000):
        test.log.step(f'loop times {i + 1}')
        test.num_of_modules = 5
        test.check_duts = [False for i in range(test.num_of_modules)]
        bulk_tester_detect(test)
        if (module_version in test.dut.devboard.last_response):
            print('now version is LYNX_100_038B')
            test.grade_thr = threading.Thread(target=upgrade, args=(test,))
        else:
            print('now version is XXX')
            test.grade_thr = threading.Thread(target=downgrade, args=(test,))
        test.grade_thr.setDaemon(True)
        test.grade_thr.start()
        test.sleep(random.randint(100, 900))
        test.module_on = 0
        test.dut.devboard.send_and_verify('mc:gpio5=0', 'OK', wait_for=".*OK.*")
        test.sleep(1)
        test.dut.devboard.send_and_verify("mc:gpio5=1")
        test.dut.devboard.send_and_verify("mc:igt=1000")
        test.sleep(60)
        test.expect(test.dut.devboard.wait_for('.*SYSSTART.*', timeout=900))
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
        test.module_on = 1


if "__main__" == __name__:
    unicorn.main()
