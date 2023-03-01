# responsible: matthias.reissner@thalesgroup.com
# location: Berlin
# TC0000001.001
# This script is for the Bulktester designed and tests up to 5 modules in parallel.
# The intention is to test fast shutdown and check in every loop, if all modules are still responsible.
# Because all ASC0 interfaces are connected to one port, only the Bulktesterport needs to be specified in the local.cfg.
# No individual port config is needed for the 5 DUTs. Precondition: ASC0 must be available, this script will not work for USB only modules.
# There is one param which needs to be set in local.cfg:
# restart_timeout = 20
# Because this timeout is individual and should not be hard coded, it must be set in the local.cfg file


import unicorn
from core.basetest import BaseTest

from plugins.duration_monitor import duration_monitor

import re
import random
import string
import threading


class Test(BaseTest):
    """ Test example for devboard DSTL methods   """

    def switch_off_fst_shdn_thr(test):
        while (test.running == 1):
            timeout = random.randint(15, 60)
            test.log.info("Fst Shdn thr timeout: " + str(timeout))
            test.sleep(timeout)
            test.modules_on = 0
            test.dut.devboard.send_and_verify("mc:pipe=mc:gpio5=out|1ms|mc:gpio5=0|15msec|mc:vbatt=off,discharge",
                                              append=True)
            test.sleep(5)
            test.dut.devboard.send_and_verify("mc:gpio5=in")
            test.sleep(0.1)
            test.dut.devboard.send_and_verify("mc:vbatt=on")
            # test.dut.devboard.send_and_verify("mc:igt=555")
            test.check_duts = [False for i in range(test.num_of_modules)]

            test.dut.devboard.send_and_verify("mc:igt=555")
            test.sleep(
                test.restart_timeout)  # some modules takes more time to bootup, therefore wait fix, otherwise sysstart is not recognized
            test.dut.devboard.wait_for(".*SYSSTART.*", 10)

            # test.log.info("last resp: " + test.dut.devboard.last_response)   # only for debugging
            sysstart_count = re.findall(".*SYSSTART.*", test.dut.devboard.last_response)
            # test.log.info(str(sysstart_count))   # only for debugging

            for i in sysstart_count:
                index = int(i[4])
                test.check_duts[
                    index - 1] = True  # index -1 because bulktester starts counting from 1..5, array index is from 0..4

            for i in range(0, test.num_of_modules):
                if (test.check_duts[i] == True):
                    test.log.info("DUT " + str(i + 1) + " lives")
                else:
                    test.log.warning("DUT " + str(i + 1) + " did not send SYSSTART")

            # Every 5th loop let module come up normally
            if (test.loop_counter % 5 == 0 and test.loop_counter > 3):
                test.log.info("let module recover every 5th loop...")
                test.sleep(60)

            test.loop_counter += 1
            test.modules_on = 1

    def setup(test):

        test.running = 1
        test.modules_on = 1
        test.loops = 100000
        test.loop_counter = 0
        test.sfsa_index = 0

        test.log.info("Restart timeout = " + str(test.restart_timeout))
        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(3)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")
        test.sleep(test.restart_timeout)

        # detect module type automatically because dstl_detect() does not work with BulkTester
        test.dut.devboard.send_and_verify("at^cicret=swn")
        test.sleep(2)
        prj = ""
        sw = ""
        for line in test.dut.devboard.last_response.splitlines():
            if (line.count('_') > 1 and "RELEASE" in line):
                prj = line[line.index(' '):line.index('_')]
                sw = line.split(' ')[1]
                test.log.info("Found project: " + prj + " with FW: " + sw)

        # if only 4 or less modules are populated in the Bulktester, please specify number of modules here. Default is 5.
        test.num_of_modules = 5

        # Generate chars of random string
        test.num_bytes_sfsa = 120
        letters = string.ascii_lowercase
        test.random_str = ''.join(random.choice(letters) for i in range(test.num_bytes_sfsa))
        test.log.info("Test random string: " + test.random_str)

        test.durat = duration_monitor.Durationmonitor('duration_monitor')
        test.durat.register(test.loops, prj, sw)

        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(3)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")
        test.sleep(test.restart_timeout)

        test.fst_shdn_thr = threading.Thread(target=test.switch_off_fst_shdn_thr)
        test.fst_shdn_thr.start()

    def run(test):
        # test.sleep(1)

        while (test.loop_counter < test.loops):
            # write to SFSA
            test.send_at_cmd("at")
            test.send_at_cmd("ati")
            test.send_at_cmd("at+gsn")
            test.send_at_cmd("at^sfsa=open,\"a:/test" + str(test.sfsa_index) + ".txt\",10")
            test.sleep(0.1)
            if (test.modules_on == 1):
                letters = string.ascii_lowercase
                test.random_str = ''.join(random.choice(letters) for i in range(test.num_bytes_sfsa))
                test.log.info("Test random string: " + test.random_str)
                test.dut.devboard.send_and_verify("at^sfsa=write,0," + str(test.num_bytes_sfsa), wait_for=".*CONNECT.*",
                                                  append=True)
                test.sfsa_index += 1
                if (test.sfsa_index == 31):
                    test.sfsa_index = 0
            test.sleep(0.1)
            if (test.modules_on == 1):
                test.dut.devboard.send_binary(test.random_str + '\r')
            test.sleep(0.1)
            test.send_at_cmd("at^sfsa=close,0")

            # test.sleep(5)
            test.durat.send_alive(test.loop_counter)

    def cleanup(test):
        test.running = 0
        test.fst_shdn_thr.join()
        pass

    def send_at_cmd(test, cmd):
        if (test.modules_on == 1):
            test.dut.devboard.send_and_verify(cmd)
        else:
            test.log.info("AT port not available, waiting...")
            test.sleep(3)


if "__main__" == __name__:
    unicorn.main()
