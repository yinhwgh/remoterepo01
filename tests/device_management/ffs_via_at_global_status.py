#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0087962.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import init
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import restart_module
from dstl.auxiliary import generate_random_byte_data
from dstl.miscellaneous import ffs_properties
import random

class Test(BaseTest):
    """
    TC0087962.001 - FfsViaAtGlobalStatus
    """
    def setup(test):
        test.dut.dstl_detect()
        test.log.info("Test Preparations: Clear FFS")
        test.expect(test.dut.dstl_restart())
        test.drives = test.dut.dstl_get_ffs_disks()  # parameter in <product>.cfg file
        for drive in test.drives:
            test.expect(test.dut.dstl_clear_directory(drive))
            test.expect(len(test.dut.dstl_list_directory(drive,1))==0, msg=f"Contents of drive "
            f"{drive} is not cleared")
        test.random_drive = random.choice(test.drives)
        test.log.info("Module support drive(s): {}".format(test.drives))
        test.log.info("Random test drive is generated to be {}".format(test.random_drive))
        test.files_number = 10
        test.log.info("{} files will be added for testing step 3,4,7,8".format(test.files_number))

    def run(test):
        test.log.info("Step 1. Read drive status: free space and storage_size has to be more or "
                      "less the same")
        test.test_clean_global_status()
        
        test.log.info("Step 2. Read global status of non existing drive B and C.")
        if "B:/" not in test.drives and "b:/" not in test.drives:
            test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"gstat\",\"B:/\"",
                                                     expect="\^SFSA: (invalid drive|100).*ERROR",
                                                     wait_for="ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"gstat\",\"C:/\"",
                                                 expect="\^SFSA: (invalid drive|100).*ERROR",
                                                 wait_for="ERROR"))
        
        test.log.info(f"Step 3. Create {test.files_number} files with 100 bytes of content")
        content_100_bytes = test.dut.dstl_generate_random_byte_data(100)
        for i in range(test.files_number):
            file_path = f"{test.random_drive}/f_{i}.txt"
            test.log.info(f"Create file {i+1}/{test.files_number}: {file_path} with 100 bytes")
            test.write_to_file(file_path, content_100_bytes, 100)

        test.log.info(f"Step 4. Read global status without drive parameter entered, check if "
                      f"storage_size - free_space = {test.files_number}*100 bytes")
        test.check_available_space(10)
        
        test.log.info("Step 5. Create one file with 1kB of content.")
        content_1_kb = test.dut.dstl_generate_random_byte_data(1024)
        file_path = f"{test.random_drive}/f_1_kb.txt"
        test.log.info(f"Create file : {file_path} with 1 KB")
        test.write_to_file(file_path, content_1_kb, 1024)

        test.log.info("Step 6. Read global status of drive A, check if storage_size - free_space = 2kB")
        test.check_available_space(1)

            
        test.log.info(f"Step 7.  Fill in the FFS with {test.files_number} files with random content "
                      f"size. Check global status after each file created")
        max_file_size_in_bytes = 1500
        for i in range(test.files_number):
            content_length = random.randint(1, max_file_size_in_bytes)
            content = test.dut.dstl_generate_random_byte_data(content_length)
            file_path = f"{test.random_drive}/f_random_{i}.txt"
            test.log.h3(f"Create file : {file_path} with {content_length} bytes")
            test.write_to_file(file_path, content, content_length)
            test.check_available_space(1, error_msg=f"Creating file {i}: ")
       

        test.log.info(f"Step 8.  Delete all files from FFS. After each file deleted check global "
                      f"status without drive parameter")
        for i in range(test.files_number):
            file_path = f"{test.random_drive}/f_random_{i}.txt"
            test.dut.dstl_remove_file(file_path)
            test.check_available_space(1,"increase", error_msg=f"Removing file {i}: ")

    def cleanup(test):
        test.log.info("Inner Step: Clear FFS")
        test.expect(test.dut.dstl_restart())
        for drive in test.drives:
            test.expect(test.dut.dstl_clear_directory(drive))
            test.expect(len(test.dut.dstl_list_directory(drive,1))==0, msg=f"Contents of drive"
            f" {drive} is not cleared")

    def write_to_file(test, file_path, file_content, content_size_in_bytes):
        fh = test.dut.dstl_open_file(file_path, flag=10)
        test.expect(test.dut.dstl_write_file(fh, content_size_in_bytes, file_content, "OK"))
        test.expect(test.dut.dstl_close_file(fh))
    
    def check_available_space(test, block_count, change="decrease", init_space=None, error_msg=""):
        """
        To check current available space changes with expected size
        params:
        init_space: space size before changing
        block_count: digit, indicating how many blocks of space are changed, one block is 2048 bytes
        change: "increase" or "decrease", indicating space is increasing or decreasing, default is
        "decrease"
        """
        init_space = test.available_space if not init_space else init_space
        test.log.info(f"Inner Step: Init space is {init_space}, block number is {block_count}")
        if change == "decrease":
            expected_available_size = init_space - block_count * 2048
        else:
            expected_available_size = init_space + block_count * 2048
        global_status = test.dut.dstl_read_global_status()
        if global_status:
            current_available_size = int(global_status["freeSize"])
            test.available_space = current_available_size
            error_msg += f"Current available space {current_available_size} is not equal with " \
                f"expected available space {expected_available_size}"
            size_matched = current_available_size == expected_available_size
            if size_matched:
                test.log.info(f"Available space matches with expected - {expected_available_size}.")
                test.expect(size_matched)
            elif block_count==1:
                test.log.info("Sometimes the file may occupy one more block.")
                expected_available_size = init_space - (block_count + 1)* 2048 \
                    if change == "decrease" else init_space + (block_count + 1)* 2048
                test.expect(current_available_size == expected_available_size, msg=error_msg)
        else:
            test.log.error("Failed to check global storage.")
        
    def test_clean_global_status(test):
        """ Test free memory size with AT^SFSA = gstat,"" when all files are deleted
            If module's free memory size is not in allowed range, try to restart module and read gstat again
        """
        global_status = test.dut.dstl_read_global_status()
        if global_status:
            total_size = int(global_status["storageSize"])
            available_size = int(global_status["freeSize"])
            test.available_space = available_size
            init_difference = total_size - available_size
            # The percentage 30%->50% was generated according to actual test results,
            # since no reference was found for the data
            allowed_difference = total_size * 0.5
            test.log.info(f"Checking storage size {total_size} subtracts free size {available_size} "
                          f"is {init_difference}, should within allowed differnce {allowed_difference}")
            if not init_difference <= allowed_difference:
                test.log.error(f"Storage size {total_size} subtracts free size {available_size} is "
                               f"{init_difference}, beyond allowed differnce {allowed_difference}\r\
                                 Try to restart module and check again")
                test.expect(test.dut.dstl_restart())
                global_status = test.dut.dstl_read_global_status()
                if global_status:
                    total_size = int(global_status["storageSize"])
                    available_size = int(global_status["freeSize"])
                    test.available_space = available_size
                    init_difference = total_size - available_size
                    test.log.info(f"Checking storage size {total_size} subtracts free size "
                                  f"{available_size} is {init_difference}, should within allowed "
                                  f"differnce {allowed_difference}")
                    error_msg = f"After restarting, storage size {total_size} subtracts free size " \
                        f"{available_size} is {init_difference}, beyond allowed differnce " \
                        f"{allowed_difference}"
                    test.expect(init_difference <= allowed_difference, msg=error_msg)
                else:
                    test.log.error("Failed to check global storage.")
        else:
            test.log.error("Failed to check global storage.")


if "__main__" == __name__:
    unicorn.main()