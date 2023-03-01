# responsible: lijuan.li@thalesgroup.com
# adaption for Viper: christian.gosslar@thalesgroup.com
# location: Beijing
# TC0108128.001, TC0107604.003

import random
import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board # added by yinhw
from dstl.auxiliary.init import dstl_detect

from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file, \
    dstl_clear_directory, dstl_read_global_status, dstl_remove_file

writ_string = "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "12345678901234567890123456789012345678901234567890123456789012345678901234567890" \
              "123456789012345678901234567890123456789012345678901234567890"


class Test(BaseTest):

    def copy_file(test, source_path, destination_path):
        result = test.dut.at1.send('at^sfsa="copy","{}","{}"'.format(source_path, destination_path),
                                   timeout=300)
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
        return_result = 1
        if duration > maxduration:
            resultmsg = resultmsg, "is bigger than " + str(maxduration) + " sec. - FAILED"
            test.log.critical(resultmsg)
            return_result = 0
        else:
            resultmsg = resultmsg, "is lower than " + str(maxduration) + " sec. as expected."
            test.log.info(resultmsg)
        return return_result

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations ")
        test.log.info("*******************************************************************")
        dstl_detect(test.dut)

        # enable URCs on MCT to see which serial lines are changing
        test.dut.devboard.send_and_verify('mc:URC=SER')
        test.dut.devboard.send_and_verify("MC:urc=off common", ".*OK.*")
        test.dut.devboard.send_and_verify('mc:URC=PWRIND')

    def run(test):
        # define the number of loops
        loops = 1000
        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(0.3)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.sleep(test.wforsysstarttimer)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_1: Clear FFS memory.")
        test.log.info("*******************************************************************")
        test.expect(dstl_clear_directory(test.dut, "a:/"))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_2: Create a file on module, size of this file should fill about "
                      "~45% of free FFS.")
        test.log.info("*******************************************************************")
        dstl_open_file(test.dut, "a:/test1.txt", 10)
        test.expect(dstl_write_file(test.dut, 0, 1500, writ_string))
        test.expect(dstl_close_file(test.dut, 0))
        # o_totalsize = int(dstl_read_global_status(test.dut)['storageSize'])
        freesize = int(dstl_read_global_status(test.dut)['freeSize'])
        o_freesize = int(dstl_read_global_status(test.dut)['freeSize'])

        while freesize >= o_freesize * 0.55:
            dstl_open_file(test.dut, "a:/test1.txt", 6)
            # for i in range(20):
            #     test.expect(dstl_write_file(test.dut, 0, 1500, writ_string))
            test.expect(dstl_write_file(test.dut, 0, 1500, writ_string))
            test.expect(dstl_close_file(test.dut, 0))
            freesize = int(dstl_read_global_status(test.dut)['freeSize'])
            test.log.info("free size: {}".format(str(freesize)))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_3: Copy the created file and measure the copy time")
        test.log.info("*******************************************************************")
        copy_time = test.copy_file("a:/test1.txt", "a:/test2.txt")
        test.log.info("Copy the created file takes {}s".format(copy_time))

        test.log.info("*******************************************************************")
        test.log.info("RunTest_4: Repeat random power loss during copying the created file for ' + "
                      "str(loops) + ' times")
        test.log.info("*******************************************************************")
        for i in range(loops):
            test.log.info('Loop: ' + str(i) + ' of ' + str(loops) + ' loops')
            test.log.info("*******************************************************************")
            dstl_remove_file(test.dut, "a:/test2.txt")
            test.dut.at2.send('at^sfsa="copy","a:/test1.txt","a:/test2.txt"')
            sleeptime = random.uniform(0, copy_time)
            test.sleep(sleeptime)
            test.dut.at1.send_and_verify('AT', "OK")
            test.dut.at1.send('at^smso')
            test.time1 = time.perf_counter()
            test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
            test.expect(test.check_timing("SHUTDOWN", maxduration=5))
            test.log.info("******Random power loss in round {}******".format(i+1))
            dstl_turn_off_vbatt_via_dev_board(test.dut) # added by yinhw
            dstl_turn_on_vbatt_via_dev_board(test.dut)
            dstl_turn_on_igt_via_dev_board(test.dut)
            test.dut.at1.wait_for("SYSSTART")
            test.sleep(5)

        test.log.info("*******************************************************************")
        test.log.info("RunTest_5: Copy the created file with another name to fill about ~90% of "
                      "free FFS. ")
        test.log.info("*******************************************************************")
        dstl_remove_file(test.dut, "a:/test2.txt")
        test.copy_file("a:/test1.txt", "a:/test2.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_6: Delete the original created file, but leave the new copyed file.")
        test.log.info("*******************************************************************")
        dstl_remove_file(test.dut, "a:/test1.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_7: Start copying the existing file as file with another name. ")
        test.log.info("*******************************************************************")
        test.copy_file("a:/test2.txt", "a:/test3.txt")

        test.log.info("*******************************************************************")
        test.log.info("RunTest_8: Repeat random power loss during copying the existing file for ' "
                      "+ str(loops) + ' times")
        test.log.info("*******************************************************************")
        for i in range(loops):
            test.log.info('Loop: ' + str(i) + ' of ' + str(loops) + ' loops')
            test.log.info("*******************************************************************")
            dstl_remove_file(test.dut, "a:/test3.txt")
            test.dut.at2.send('at^sfsa="copy","a:/test2.txt","a:/test3.txt"')
            sleeptime = random.uniform(0, copy_time)
            test.sleep(sleeptime)
            test.dut.at1.send('at^smso')
            test.time1 = time.perf_counter()
            test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
            test.expect(test.check_timing("SHUTDOWN", maxduration=5))
            test.log.info("******Random power loss in round {}******".format(i+1))
            dstl_turn_off_vbatt_via_dev_board(test.dut)  # added by yinhw
            dstl_turn_on_vbatt_via_dev_board(test.dut)
            dstl_turn_on_igt_via_dev_board(test.dut)
            test.dut.at1.wait_for("SYSSTART")
            test.sleep(5)

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Remove copyed file from module")
        test.log.info("*******************************************************************")
        dstl_remove_file(test.dut, "a:/test1.txt")
        dstl_remove_file(test.dut, "a:/test2.txt")
        dstl_remove_file(test.dut, "a:/test3.txt")


if __name__ == "__main__":
    unicorn.main()