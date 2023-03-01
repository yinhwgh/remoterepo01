# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC: TC0107134.001
# jira:
# feature: LM0003276.00x
# Multiplexer: yes, this script supports tests under mux mode
# Note: please do not insert a DSTL_restart() or something else which will influence the multiplexer mode!

#!/usr/bin/env unicorn
"""

Create sub folder and a text file into the modules flash file system.
Do this recursively until flash file system is full and runs into out of memory.
Always the same file is used to be written. After each folder/file is created
the free size of the FFS and the size of the file is checked.
If out of memory appears, then recursively back all files and folders are deleted
and the free size of the FFS is checked again.

"""

import unicorn
import time
import os
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
import dstl.embedded_system.embedded_system_configuration
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file, dstl_list_directory
from dstl.miscellaneous.ffs_properties import dstl_get_ffs_disks
from os.path import realpath, dirname, join, isfile

ver = "1.0"

class Test(BaseTest):
    """

    """
    dst_test_path = ''
    BLOCK_SIZE = 1500   # most products have max. block size of 1500, see AT^SFSA=write

    def setup(test):
        """
        Steps to be executed before test is run.
        """

        test.log.com('***** Testcase: ' + test.test_file + ' Ver: ' + str(ver) + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        #test.dut.at2.open()  # channel for userware output
        #test.dut.log.open()  # channel for debug output

        # enable HW-flow on interface:
        test.expect(test.dut.at1.send_and_verify("AT&v"))
        test.expect(test.dut.at1.send_and_verify("AT\Q3"))
        test.expect(test.dut.at1.send_and_verify("AT&v"))

        # check general settings:
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("AT&w"))

        # set global values, product dependent:
        # if re.search(test.dut.project, 'SERVAL'):
        #    test.BLOCK_SIZE = 9000
        pass


    def run(test):
        """Run method.

        Actual test steps.
        See comments below for details.
        """

        SRV03_1755_RETEST = False
        dst_test_file_name_abs =""
        dst_test_path =""

        test.text_src_file_path = test.test_files_path + '\\text\\'
        test.text_src_file_name = 'suntzu.txt'
        test.text_src_file_name_abs = join(test.text_src_file_path, test.text_src_file_name)
        print("tfPath:", test.text_src_file_name_abs)

        if not isfile(test.text_src_file_name_abs):
            test.expect(False, critical=True,
                        msg="test text file not found (abort): {}".format(test.text_src_file_name_abs))

        # estimate file size of source file
        # open file and read in blocks (if product supports only 1500 bytes for one ^SFSA=write cmd):
        srcfileobj = _file_reader(test.text_src_file_name_abs, 'rt')
        src_file_size = len(srcfileobj)

        last_errors = None
        main_loop = 1

        while main_loop:
            main_loop -= 1
            # get free memory size of FFS
            dst_drive = test.dut.dstl_get_ffs_disks()[0]
            print("ffs_gstat", dst_drive)
            ffs_free_size = test.dut.dstl_read_global_status()['freeSize']
            print(' FFS free size is:', ffs_free_size)

            test.log.info("\n --- 1.) write file into sub folders until out of memory ---")
            # loop until error on creating folder or file:
            #   get last created sub folder
            #   create a sub folder named '1'.....
            #   create (open) a new file into that sub folder
            #   write the text data from test_files folder to the module into that new file
            #   close the file
            #   check file size of new file against source file
            #   get free memory size of FFS  and calc diff of previous free mem size - is it the file-size really ?

            # 2.) read file content, compare and delete this file
            # next loop:
            #   get last file name and sub folder name
            #   get free memory size of FFS
            #   open file for read
            #   read data from file
            #   compare file with source file
            #   delete file
            #   delete sub folder
            #   get free memory size of FFS  and calc diff of previous free mem size - is it the file-size really ?

            # 3.) check status of nearly empty FFS
            #

            #       # estimate file size of source file
            # get free memory size of FFS

            # delete all sub files and folders:

            # 0.) prepare and clear 'testfolder'
            dst_drive = dst_drive.replace('"', '')  # test.text_src_file_path
            test.dst_test_path = dst_drive.rstrip('/')
            test.dst_test_path = test.dst_test_path + "/testfolder"

            # create folder for our tests, or clear it: 'SFSA: 16 == path already exists'
            test.dut.dstl_create_directory(test.dst_test_path, expect_response='(?s).*(SFSA: 0.*OK|SFSA: 16).*')
            ret = test.dut.dstl_clear_directory(test.dst_test_path)
            if not ret:
                test.expect(False, critical=True, msg="Error on clearing test directory - abort!")

            # 1.) write file into sub folders until out of memory
            # loop until error on creating folder or file:
            if (test.dut.project == 'VIPER'):
                one_file_in_one_folder = False  # create NO sub folder
            else:
                one_file_in_one_folder = True  # create a sub folder and put only one file in it, next file in sub sub folder
            # if False: only test files are created - no folder is created!
            abort = False
            loop_num = 0
            while not abort:

                loop_num = loop_num + 1
                last_dst_test_path = test.dst_test_path
                if one_file_in_one_folder:
                    #   create a sub folder named '1'.....
                    test.dst_test_path = test.dst_test_path + "/" + str(loop_num)
                    ret = test.dut.dstl_create_directory(test.dst_test_path)
                    if not ret:
                        abort = True
                        break  # abort loop due to dir create error

                new_ffs_free_size = int(test.dut.dstl_read_global_status()['freeSize'])
                test.log.info(' ##> FFS free size is:' + str(new_ffs_free_size))
                if new_ffs_free_size < src_file_size:
                    src_file_size = new_ffs_free_size
                    test.log.info(
                        ' ##> ATTENTION: free mem in FFS is smaller than the give file, lets try to store max. free size of the file only')

                # set BLOCK_SIZE to maximum possible value, only possible with SERVAL:
                if (test.dut.project == 'SERVAL'):
                #if re.search(test.dut.project, 'SERVAL'):
                    if SRV03_1755_RETEST:
                        test.BLOCK_SIZE = 9000  # define your own block size from 1500 over 6000 to max.
                        if new_ffs_free_size < test.BLOCK_SIZE:
                            test.BLOCK_SIZE = new_ffs_free_size
                    else:
                        # this should also work, but fails with SERVAL_300_032 too!
                        if new_ffs_free_size > src_file_size:
                            test.BLOCK_SIZE = src_file_size
                        else:
                            test.BLOCK_SIZE = new_ffs_free_size  # ToDo: is this really possible ?

            #   create (open) a new file into that sub folder
                last_dst_test_file_name_abs = dst_test_file_name_abs
                dst_test_file_name_abs = test.dst_test_path + "/" + "{}.txt".format(loop_num)
                print(" dst file name:", dst_test_file_name_abs)

                fhandle = test.dut.dstl_open_file(dst_test_file_name_abs, 9)
                if fhandle is False:
                    abort = True
                    test.expect(False)
                    break  # abort loop  due to file create error

                print("fh:", fhandle)

                #   write the text data from test_files folder to the module into that new file
                if fhandle >= 0:
                    data_size_todo = len(srcfileobj)
                    data_pointer = 0
                    next_block_size = test.BLOCK_SIZE   # normally 1500

                    while data_size_todo > 0:
                        print("data_size_todo: ", data_size_todo)
                        if data_size_todo < test.BLOCK_SIZE:    # normally 1500
                            next_block_size = data_size_todo

                        ret = test.dut.dstl_write_file(fhandle, next_block_size,
                                                       srcfileobj[data_pointer:data_pointer + next_block_size])
                        if ret:
                            data_size_todo = data_size_todo - next_block_size
                            data_pointer = data_pointer + next_block_size
                            # time.sleep(5)
                        else:
                            abort = True
                            test.expect(False)
                            break  # abort loop due to file write abort

                # collect last error
                last_errors = test.dut.dstl_get_last_sfsa_error()

                #   close the file in any case
                #if not abort:
                ret = test.dut.dstl_close_file(fhandle)
                if not ret:
                    abort = True
                    test.log.error('error on closing last file')
                    test.expect(False)
                    break  # abort loop due to file close error

                #   check file size of new file against source file
                file_status = test.dut.dstl_read_status(dst_test_file_name_abs)
                new_file_size = int(file_status['fileSize'])

                ''' 
                # for_DEBUG_only
                if loop_num >= 3:
                    loop_num = loop_num - 1
                    break;
                '''

            if abort:
                last_sfsa_error = last_errors['sfsaError']
                last_cme_error = last_errors['cmeError']
                print('last SFSA error code: ', last_sfsa_error)
                print('last CME  error code: ', last_cme_error)
                sfsa_msg = test.dut.dstl_get_sfsa_error_text(last_sfsa_error)
                test.log.info('last SFSA error text: "{}"'.format(sfsa_msg))

                last_resp = test.dut.at1.last_response
                test.log.info ("old path: >" + str(last_dst_test_file_name_abs) + "<")

            #   check file size of new file against source file
            file_status = test.dut.dstl_read_status(dst_test_file_name_abs)
            if file_status:
                new_file_size = int(file_status['fileSize'])
            # new_file_size = int(test.dut.dstl_read_status(dst_test_file_name_abs)['fileSize'])

            #   get free memory size of FFS  and calc diff of previous free mem size - is it the file-size really ?
            new_ffs_free_size = test.dut.dstl_read_global_status()['freeSize']

            #   get last created sub folder

            test.log.info("\n --- 2.) read file content, compare and delete this file -----")
            # next loop:
            #   get last file name and sub folder name
            #   get free memory size of FFS
            #   open file for read
            #   read data from file
            #   compare file with source file
            #   delete file
            #   delete sub folder
            #   get free memory size of FFS  and calc diff of previous free mem size - is it the file-size really ?

            while loop_num > 0:

                if abort:
                    test.dst_test_path = last_dst_test_path
                    loop_num = loop_num -1
                    abort= False
                test.dst_test_path = test.dst_test_path.rstrip('/')
                test_file_name_abs = test.dst_test_path + "/{}.txt".format(loop_num)

                # get file size:
                old_file_size = test.expect(test.dut.dstl_read_status(test_file_name_abs)['fileSize'])
                test.log.info(" ##> file size is: {}, of file: {}".format(old_file_size, test_file_name_abs))
                if old_file_size.isdigit():
                    old_file_size = int(old_file_size)

                fhandle = test.dut.dstl_open_file(test_file_name_abs, 64)  # serval: 64==readonly
                if fhandle is False:
                    abort = True
                    test.log.error('error on opening a file to read')
                    test.expect(False)
                    break  # abort loop due to file open for read error

                print("fh:", fhandle)

                file_data = ''
                #   read the text data from test_files folder to the module into that new file
                if fhandle >= 0:
                    data_size_todo = old_file_size
                    next_block_size = test.BLOCK_SIZE       # normally 1500

                    while data_size_todo > 0:
                        test.log.info(" ##> data_size_todo: " + str(data_size_todo))
                        if data_size_todo < test.BLOCK_SIZE:    # normally 1500
                            next_block_size = data_size_todo

                        new_data: object = test.expect(test.dut.dstl_read_file(fhandle, next_block_size))
                        file_data = file_data + new_data
                        if new_data is False:
                            abort = True
                            break  # abort loop due to file read error
                        else:
                            data_size_todo = data_size_todo - next_block_size

                #   close the file
                ret = test.expect(test.dut.dstl_close_file(fhandle))

                ret = test.expect(test.dut.dstl_remove_file(test.dst_test_path + "/{}.txt".format(loop_num)))
                if one_file_in_one_folder:
                    ret = test.expect(test.dut.dstl_remove_directory(test.dst_test_path))
                new_ffs_free_size = test.expect(test.dut.dstl_read_global_status()['freeSize'])
                test.log.info(" ##> file and folder {} deleted, size left on FFS: {}".format(test.dst_test_path, new_ffs_free_size))
                loop_num = loop_num - 1


                #print("1:", test_file_name_abs)
                path_elements = test_file_name_abs.split('/')
                path_elements_num = len(path_elements)
                new_test_file_name = ''
                if one_file_in_one_folder:
                    for i in range(0, path_elements_num - 2, 1):
                        new_test_file_name = new_test_file_name + path_elements[i] + '/'
                else:
                    for i in range(0, path_elements_num - 1, 1):
                        new_test_file_name = new_test_file_name + path_elements[i] + '/'
                test.dst_test_path = new_test_file_name

                #print("2:", test.dst_test_path)
                #print("loop:", loop_num)


            test.log.info("\n --- 3.) check status of nearly empty FFS ----")
            #
            ffs_free_size = test.expect(test.dut.dstl_read_global_status()['freeSize'])
            test.log.info("free size of FFS: {}".format(ffs_free_size))


        test.log.info(" MAIN LOOP has ended.")
        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # 1st check how much free space is left:
        new_ffs_free_size = test.dut.dstl_read_global_status()['freeSize']

        # 2nd ok, lets clean up all:
        test.dut.dstl_clear_directory(test.dst_test_path)

        test.dut.at1.send_and_verify('AT', "^.*OK.*$", timeout=25)
        pass


def _file_reader(path, fo_params='rt'):
    file_object = open(path, fo_params)
    try:
        file_context = file_object.read()
    finally:
        file_object.close()
    return file_context


if "__main__" == __name__:
    unicorn.main()
