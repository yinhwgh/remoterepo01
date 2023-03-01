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

# from plugins.duration_monitor import duration_monitor

import re
import time
import random
import string
import threading

class Test(BaseTest):
    """ Test example for devboard DSTL methods   """

    def switch_off_fst_shdn_thr(test, start_ts, stop_ts):
        while (test.running == 1):
            if (test.thr_active == 1):
                test.log.info("fst thr start / stop ts: " + str(start_ts) + " " + str(stop_ts))
                timeout = random.randint(start_ts, stop_ts)
                test.log.info("Fst Shdn thr timeout: " + str(timeout))
                test.sleep(timeout)
                test.modules_on = 0
                test.toggle_fst_shdn_pin()
                test.sleep(0.1)
                test.switch_modules_on()
                test.check_modules_alive()
                test.modules_on = 1


    def toggle_fst_shdn_pin(test):
        test.dut.devboard.send_and_verify("mc:pipe=mc:gpio5=out|1ms|mc:gpio5=0|15msec|mc:vbatt=off,discharge", append = True)
        test.sleep(5)
        test.dut.devboard.send_and_verify("mc:gpio5=in")

    def switch_modules_on(test):
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")


    def check_modules_alive(test):
        test.check_duts = [False for i in range(test.num_of_modules)]

        test.sleep(test.restart_timeout)    # some modules takes more time to bootup, therefore wait fix, otherwise sysstart is not recognized
        test.dut.devboard.wait_for(".*SYSSTART.*", 10)

        #test.log.info("last resp: " + test.dut.devboard.last_response)   # only for debugging
        sysstart_count = re.findall(".*SYSSTART.*", test.dut.devboard.last_response)
        #test.log.info(str(sysstart_count))   # only for debugging

        for i in sysstart_count:
            index = int(i[4])
            test.check_duts[index - 1] = True    # index -1 because bulktester starts counting from 1..5, array index is from 0..4

        for i in range(0, test.num_of_modules):
            if (test.check_duts[i] == True):
                test.log.info("DUT " + str(i + 1) + " lives")
            else:
                test.log.warning("DUT " + str(i + 1) + " did not send SYSSTART")


    def setup(test):

        # Variables
        test.dut.at1.send_and_verify("ati")
        print('aaaa:', test.dut.at1.last_response)
        test.dut.at1.send_and_verify("at", append=True)
        print('bbbb:', test.dut.at1.last_response)
        test.sleep(100)



        test.running = 1
        test.modules_on = 1
        test.loops = 10
        test.loop_counter = 0
        test.sfsa_index = 0
        test.thr_active = 0
        # test.restart_timeout = 20

        # if only 4 or less modules are populated in the Bulktester, please specify number of modules here. Default is 5.
        test.num_of_modules = 5

        test.require_parameter("restart_timeout", default=30)

        test.log.info("Restart timeout = " + str(test.restart_timeout))
        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(3)
        start_ts = time.time()
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")
        #test.sleep(test.restart_timeout)
        test.dut.devboard.wait_for(".*SYSSTART.*", 60)
        test.sysstart_timeout = time.time() - start_ts
        test.sysstart_timeout = round(test.sysstart_timeout, 3)
        test.log.info("Measured SYSSTART timeout: " + str(test.sysstart_timeout))
        test.sleep(3)

        # detect module type automatically because dstl_detect() does not work with BulkTester
        test.dut.devboard.send_and_verify("at^cicret=swn", wait_for = ".*OK.*")
        test.sleep(2)
        prj = ""
        sw = ""
        for line in test.dut.devboard.last_response.splitlines():
            if (line.count('_') > 1 and "RELEASE" in line):
                prj = line[line.index(' '):line.index('_')]
                sw = line.split(' ')[1]
                test.log.info("Found project: " + prj + " with FW: " + sw)

        # Generate chars of random string
        test.num_bytes_sfsa = 120
        letters = string.ascii_lowercase
        test.random_str = ''.join(random.choice(letters) for i in range(test.num_bytes_sfsa))
        test.log.info("Test random string: " + test.random_str)

        # test.durat = duration_monitor.Durationmonitor('duration_monitor')
        # test.durat.register(test.loops, prj, sw)

        test.dut.devboard.send_and_verify("mc:vbatt=off")
        test.sleep(3)
        test.dut.devboard.send_and_verify("mc:vbatt=on")
        test.dut.devboard.send_and_verify("mc:igt=555")
        test.sleep(test.restart_timeout)

        test.fst_shdn_thr = threading.Thread(target=test.switch_off_fst_shdn_thr, args=(1,60,))
        test.fst_shdn_thr.start()

    def run(test):

        while (test.loop_counter < test.loops):

            if (test.modules_on == 1):

                test.log.info("Loop: " + str(test.loop_counter+1) + " / " + str(test.loops))

                # randomly run UC 1 or 2 but with more weigth on UC 1
                uc_rand = random.randint(0, 4)
                test.log.info("uc_rand: " + str(uc_rand))

                if (not uc_rand == 0):
                    # UC 1 write data with SFSA until power cut
                    test.log.info("Run UC 1")
                    #test.fst_shdn_thr = threading.Thread(target=test.switch_off_fst_shdn_thr, args=(1,60,))
                    #test.fst_shdn_thr.start()
                    test.thr_active = 1

                    # write to SFSA
                    test.send_at_cmd("at")
                    test.send_at_cmd("ati")
                    test.send_at_cmd("at+gsn")

                    #test.thr_active = 0

                    while (test.modules_on == 1):
                        test.send_at_cmd("at^sfsa=open,\"a:/test" + str(test.sfsa_index) + ".txt\",10")
                        test.sleep(0.1)
                        if (test.modules_on == 1):
                            letters = string.ascii_lowercase
                            test.random_str = ''.join(random.choice(letters) for i in range(test.num_bytes_sfsa))
                            test.log.info("Test random string: " + test.random_str)
                            test.dut.devboard.send_and_verify("at^sfsa=write,0," + str(test.num_bytes_sfsa), wait_for = ".*CONNECT.*", append = True)   #  wait_after_send = 0.5
                            test.sfsa_index += 1
                            if (test.sfsa_index == 31):
                                test.sfsa_index = 0
                        test.sleep(0.1)
                        if (test.modules_on == 1):
                            test.dut.devboard.send_binary(test.random_str + '\r')
                        test.sleep(0.1)
                        test.send_at_cmd("at^sfsa=close,0")
                    #test.log.info("Stop thread")
                    #test.fst_shdn_thr.join()
                    test.thr_active = 0

                else:
                    #UC 2 try switch module off before SYSSTART
                    test.log.info("Run UC 2")
                    test.toggle_fst_shdn_pin()
                    test.switch_modules_on()
                    timeout = random.uniform(0.000, test.sysstart_timeout)
                    test.log.info("uc2 sleep: " + str(timeout))
                    test.sleep(timeout)
                    test.toggle_fst_shdn_pin()
                    test.sleep(1)
                    test.switch_modules_on()
                    test.check_modules_alive()

                # test.durat.send_alive(test.loop_counter)

                # Every 5th loop let module come up normally
                if (test.loop_counter % 5 == 0 and test.loop_counter > 3):
                    test.log.info("let module recover every 5th loop...")
                    test.sleep(60)

                test.loop_counter += 1

            else:
                test.log.info("Main loop, module not available, sleep...")
                test.sleep(5)


    def cleanup(test):
        test.running = 0
        test.fst_shdn_thr.join()
        pass

    def send_at_cmd(test, cmd):
        if (test.modules_on == 1):
            test.dut.devboard.send_and_verify(cmd)   # wait_after_send = 0.5
        else:
            test.log.info("AT port not available, waiting...")
            test.sleep(3)


if "__main__" == __name__:
    unicorn.main()
