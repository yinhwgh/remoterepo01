# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108215.001

import unicorn
from core.basetest import BaseTest
import random
import re
from dstl.auxiliary.generate_data import dstl_generate_data
import threading

data_500 = dstl_generate_data(500)


class Test(BaseTest):
    """
       TC0108215.001 - HWDrivenFastShutdownDuringSocket
    """

    def setup(test):
        bulk_tester_detect(test)
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=out', 'OK', wait_for=".*OK.*")
        test.dut.devboard.send_and_verify('mc:gpio5=1', 'OK', wait_for=".*OK.*")
        test.modules_on = 1

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


def send_at_cmd(test, cmd):
    if (test.modules_on == 1):
        test.dut.devboard.send_and_verify(cmd)
    else:
        test.log.info("AT port not available, waiting...")
        test.sleep(3)


def socket_process(test):
    test.log.info("socket thread begins.")
    test.expect(test.dut.devboard.send_and_verify('AT+CGDCONT=1,IPV4V6,cmnet', ".*OK.*"))
    test.expect(test.dut.devboard.send_and_verify('AT^SISS=0,"srvType","socket"', ".*OK.*"))
    test.expect(test.dut.devboard.send_and_verify('AT^SISS=0,"conid","1"', ".*OK.*"))
    test.expect(test.dut.devboard.send_and_verify('AT^SISS=0,"address","socktcp://114.55.6.216:9012"', ".*OK.*"))
    test.expect(test.dut.devboard.send_and_verify('AT^SICA=1,1', ".*OK.*"))
    test.expect(test.dut.devboard.send_and_verify('AT^SISO=0', "SISW: 0,1", wait_for="SISW: 0,1"))
    for i in range(10):
        test.expect(test.dut.devboard.send_and_verify('AT^SISW=0,500', 'SISW:', wait_for='SISW:'))
        test.expect(test.dut.devboard.send_and_verify(data_500, 'OK', wait_for='SISW:'))
        test.sleep(5)
    test.expect(test.dut.devboard.send_and_verify('AT^SISC=0', ".*OK.*"))


def main_process(test):
    for i in range(1):
        test.log.step(f'loop times {i + 1}')
        test.num_of_modules = 5
        test.check_duts = [False for i in range(test.num_of_modules)]
        test.socket_thr = threading.Thread(target=socket_process, args=(test,))
        test.socket_thr.setDaemon(True)
        test.socket_thr.start()
        test.sleep(random.randint(0, 60))
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
