# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0108422.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file, \
    dstl_clear_directory, dstl_read_file, dstl_remove_file, dstl_read_status

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

    def setup(test):
        test.log.info("*******************************************************************")
        test.log.info("SetUp_1: Initiate moudle and restore to default configurations ")
        test.log.info("*******************************************************************")
        dstl_detect(test.dut)

        # enable URCs on MCT to see which serial lines are changing
        test.dut.devboard.send_and_verify('mc:URC=SER')
        test.dut.devboard.send_and_verify("MC:urc=off common", ".*OK.*")
        test.dut.devboard.send_and_verify('mc:URC=PWRIND')

        test.log.info("*******************************************************************")
        test.log.info("SetUp_2: Clear FFS memory.")
        test.log.info("*******************************************************************")
        test.expect(dstl_clear_directory(test.dut, "a:/"))

    def run(test):
        # define the number of loops
        loops = 100
        for l in range(loops):
            test.log.step(f"This is in repeat{l+1} loop !")

            test.log.info("*******************************************************************")
            test.log.info("RunTest_1: Create a file on module.")
            test.log.info("*******************************************************************")
            dstl_open_file(test.dut, "a:/test1.txt", 10)

            test.log.info("*******************************************************************")
            test.log.info("RunTest_2: Write data(1500Byte*10) the file.")
            test.log.info("*******************************************************************")
            for i in range(10):
                test.log.info('Loop: ' + str(i + 1) + ' of ' + '10 write loops')
                test.expect(dstl_write_file(test.dut, 0, 1500, writ_string))
                test.sleep(5)

            test.log.info("*******************************************************************")
            test.log.info("RunTest_3: Close the file.")
            test.log.info("*******************************************************************")
            test.expect(dstl_close_file(test.dut, 0))

            test.log.info("*******************************************************************")
            test.log.info("RunTest_4: Check file size of new file")
            test.log.info("*******************************************************************")
            checkfile = dstl_read_status(test.dut, 'a:/test1.txt')
            if checkfile['fileSize'] != '15000':
                test.expect(False, critical=True, msg="loss data and stop ！")

            test.log.info("*******************************************************************")
            test.log.info("RunTest_5: Open the file again.")
            test.log.info("*******************************************************************")
            dstl_open_file(test.dut, "a:/test1.txt", 10)

            test.log.info("*******************************************************************")
            test.log.info("RunTest_6: Read data(1500Byte*10) from file.")
            test.log.info("*******************************************************************")
            for i in range(10):
                test.log.info('Loop: ' + str(i + 1) + ' of ' + '10 read loops')
                test.expect(dstl_read_file(test.dut, 0, 1500))
                test.sleep(5)

            test.log.info("*******************************************************************")
            test.log.info("RunTest_7: Close and delete the file. ")
            test.log.info("*******************************************************************")
            test.expect(dstl_close_file(test.dut, 0))
            dstl_remove_file(test.dut, "a:/test1.txt")

    def cleanup(test):
        test.log.info("*******************************************************************")
        test.log.info("CleanUp_1: Remove copyed file from module")
        test.log.info("*******************************************************************")
        dstl_remove_file(test.dut, "a:/test1.txt")


if __name__ == "__main__":
    unicorn.main()
