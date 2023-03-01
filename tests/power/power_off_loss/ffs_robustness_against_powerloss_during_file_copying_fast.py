#responsible: lijuan.li@thalesgroup.com
#location: Beijing
#TC0107604.002FfsRobustnessAgainst_shutdownDuringFileCopying



import unicorn
import random
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import *
from dstl.auxiliary.restart_module import *
from dstl.network_service.register_to_network import *
from dstl.auxiliary.init import *
from dstl.security.lock_unlock_sim import *
from dstl.miscellaneous.access_ffs_by_at_command import *

writ_string = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"

class FfsRobustnessAgainstPowerLossDuringFileCopying(BaseTest):

    def copy_file(test,source_path, destination_path):
        result = test.dut.at1.send('at^sfsa="copy","{}","{}"'.format(source_path, destination_path))
        start_time = time.time()
        test.dut.at1.wait_for("OK")
        end_time = time.time()
        return end_time - start_time

    wforsysstarttimer = 60
    time1 = 0

    def check_timing(test, teststep="", maxduration=10):
        if teststep == "":
            teststep = "general time measuring"

        time2 = time.perf_counter()
        # print("T1", time1, "T2", time2, "diff", (time2-time1) )
        duration = time2 - test.time1
        resultmsg = teststep, "was: {:.1f} sec.".format(duration)
        if duration > maxduration:
            resultmsg = resultmsg, "is bigger than " + str(maxduration) + " sec. - FAILED"
            test.log.critical(resultmsg)
            return -1
        else:
            resultmsg = resultmsg, "is lower than " + str(maxduration) + " sec. as expected."
            test.log.info(resultmsg)
        return 0

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations ")
        test.log.info("*******************************************************************")
        test.dut.detect()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK",timeout=30))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=30))
        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Disable SIM PIN lock before testing  ")
        test.log.info("*******************************************************************")
        test.dut.dstl_unlock_sim()

        # enable URCs on MCT to see which serial lines are changing
        test.dut.devboard.send_and_verify('mc:URC=SER')
        test.dut.devboard.send_and_verify('mc:URC=on')
        test.dut.devboard.send_and_verify('mc:URC=PWRIND')

    def run(test):
        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(0.3)
        test.dut.dstl_turn_on_igt_via_dev_board()
        test.sleep(test.wforsysstarttimer)
        test.dut.at1.send('ATi')
        test.dut.devboard.send_and_verify('mc:pwrind?')

        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Clear FFS memory.")
        test.log.info("*******************************************************************")
        test.expect(test.dut.dstl_clear_directory("a:/"))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Create a file on module, size of this file should fill about ~45% of free FFS.")
        test.log.info("*******************************************************************")
        test.dut.dstl_open_file("a:/test1.txt", 10)
        test.expect(test.dut.dstl_write_file(0, 1500, writ_string))
        test.expect(test.dut.dstl_close_file(0))
        o_totalsize = int(test.dut.dstl_read_global_status()['storageSize'])
        freesize = int(test.dut.dstl_read_global_status()['freeSize'])
        o_freesize = int(test.dut.dstl_read_global_status()['freeSize'])

        while freesize >= o_freesize * 0.55:
            test.dut.dstl_open_file("a:/test1.txt",6)
            for i in range (20):
                test.expect(test.dut.dstl_write_file(0, 1500, writ_string))
            test.expect(test.dut.dstl_close_file(0))
            freesize = int(test.dut.dstl_read_global_status()['freeSize'])

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Copy the created file and measure the copy time")
        test.log.info("*******************************************************************")
        copy_time = test.copy_file("a:/test1.txt","a:/test2.txt")
        test.log.info("Copy the created file takes {}s".format(copy_time))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Repeat random power loss during copying the created file for 500 times")
        test.log.info("*******************************************************************")
        for i in range (500):
            test.dut.dstl_remove_file("a:/test2.txt")
            test.dut.at1.send('at^sfsa="copy","a:/test1.txt","a:/test2.txt"')
            sleeptime= random.uniform(0, copy_time)
            test.sleep(sleeptime)
            test.dut.at2.send_and_verify('AT', "OK")
            test.dut.at2.send('at^smso=fast')
            test.time1 = time.perf_counter()
            test.expect(test.dut.at2.wait_for(".*PWRIND: 1.*", timeout=5))
            ret = test.check_timing("SMSO FAST SHUTDOWN", maxduration=1)
            test.log.info("******Random power loss in round {}******".format(i+1))
            test.dut.dstl_turn_on_vbatt_via_dev_board()
            test.dut.dstl_turn_on_igt_via_dev_board()
            test.dut.at1.wait_for("SYSSTART")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Copy the created file with another name to fill about ~90% of free FFS. ")
        test.log.info("*******************************************************************")
        test.dut.dstl_remove_file("a:/test2.txt")
        test.copy_file("a:/test1.txt", "a:/test2.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Delete the original created file, but leave the new copyed file. ")
        test.log.info("*******************************************************************")
        test.dut.dstl_remove_file("a:/test1.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Start copying the existing file as file with another name. ")
        test.log.info("*******************************************************************")
        test.copy_file("a:/test2.txt", "a:/test3.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Repeat random power loss during copying the existing file for 500 times")
        test.log.info("*******************************************************************")
        for i in range (500):
            test.dut.dstl_remove_file("a:/test3.txt")
            test.dut.at1.send('at^sfsa="copy","a:/test2.txt","a:/test3.txt"')
            sleeptime= random.uniform(0, copy_time)
            test.sleep(sleeptime)
            test.dut.at2.send('at^smso=fast')
            test.time1 = time.perf_counter()
            test.expect(test.dut.at2.wait_for(".*PWRIND: 1.*", timeout=5))
            ret = test.check_timing("SMSO FAST SHUTDOWN", maxduration=1)
            test.log.info("******Random power loss in round {}******".format(i+1))
            test.dut.dstl_turn_on_vbatt_via_dev_board()
            test.dut.dstl_turn_on_igt_via_dev_board()
            test.dut.at1.wait_for("SYSSTART")



    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Remove copyed file from module")
        test.log.info("*******************************************************************")
        test.dut.dstl_remove_file("a:/test2.txt")
        test.dut.dstl_remove_file("a:/test3.txt")



if (__name__ == "__main__"):
    unicorn.main()
