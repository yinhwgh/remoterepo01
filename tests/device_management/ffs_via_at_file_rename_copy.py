# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087960.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.generate_data import dstl_generate_data
import random


class FfsViaAtFileRenameCopy(BaseTest):
    '''
    TC0087960.001 - FfsViaAtFileRenameCopy
    Intention :Perform basic FFS functions via AT^SFSA command like copy files and change name of files or directories
    Debug base project: Serval
    '''
    rootpath = 'a:/'
    dir_list = [rootpath + 'dir1/', rootpath + 'dir2/', rootpath + 'dir3/', rootpath + 'dir1/dir2']
    file_list = [rootpath + 'dir1/f1.txt', rootpath + 'dir2/f2.txt', rootpath + 'dir3/f3.txt', rootpath + 'dir1/dir2/f4.txt']
    copyed_file_list = [rootpath+'c1.txt', dir_list[0]+'c2.txt', dir_list[-1]+'c3.txt']
    dir_to_rename = [rootpath +'dir1', rootpath+'dira/dir2']
    rename_dir_list = ['dira', 'dirb']
    rename_dir_path =[rootpath +'dira', rootpath+'dira/dirb']
    pathA = rootpath+'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'#121+3
    pathB = rootpath+'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'#125+3
    fileA = rootpath+'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/CCC'#125+3
    fileB = rootpath+'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/B'#126+3

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_clear_directory(test.rootpath)

    def run(test):
        if test.dut.platform == 'INTEL':
            test.step_1()
        else:
            test.log.info('Skip step 1, can\'t be auto for current product.')

        test.log.info('2. On the FFS, create few new directories: AT^SFSA="mkdir",path')
        for dirpath in test.dir_list:
            test.expect(test.dut.dstl_create_directory(dirpath))

        test.log.info('3. In the created directories, create few new files with all possible flag combinations')
        for file in test.file_list:
            fh = test.dut.dstl_open_file(file, 10)
            fsize = random.randint(1, 100)
            test.expect(test.dut.dstl_write_file(fh, fsize, dstl_generate_data(fsize)))
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('4. Try to copy files between directories: AT^SFSA="copy",source_path,dest_path')
        for i in range(len(test.copyed_file_list)):
            test.expect(test.dut.dstl_copy_file(test.file_list[i+1],test.copyed_file_list[i]))

        test.log.info('5. Check if copied files are the same as original files: AT^SFSA="crc",path.')
        for i in range(len(test.copyed_file_list)):
            crc = test.dut.dstl_get_crc(test.file_list[i+1])
            copyed_crc = test.dut.dstl_get_crc(test.copyed_file_list[i])
            if (crc == copyed_crc):
                test.log.info('CRC same as original file, correct.')
                test.expect(True)
            else:
                test.log.error('CRC not same as original file, error!')
                test.expect(False)

        test.log.info('6. Rename few directories: AT^SFSA="rename",path,new_name.')
        for i in range(2):
            test.expect(test.dut.dstl_rename_file(test.dir_to_rename[i], test.rename_dir_list[i]))

        test.log.info('7. Check if it is possible to read the content of renamed directories.')
        for dir in test.rename_dir_path:
            test.expect(test.dut.dstl_list_directory(dir))

        test.log.info('8. Create a file in path A, the file name and path to it have to consist exactly 128 characters.')
        test.expect(test.dut.dstl_create_directory(test.pathA))
        fh=test.dut.dstl_open_file(test.fileA, 8)
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('9. Create directories structure with path length 128 characters - path B.')
        test.expect(test.dut.dstl_create_directory(test.pathB))

        test.log.info('10. Try to copy file from path A to B.')
        test.expect(test.dut.dstl_copy_file(test.fileA, test.fileB, expect_response='.*ERROR.*'))

        test.log.info('11. Try to rename file in path A - add 2 chars to the current name.')
        test.expect(test.dut.dstl_rename_file(test.fileA, test.fileA+'AA', expect_response='.*ERROR.*'))

        test.log.info('12. Try to rename one directory in path A - add 2 chars to the current name.')
        test.expect(test.dut.dstl_rename_file(test.pathA, test.pathA[3:] + 'AAAAA', expect_response='.*ERROR.*'))

        test.log.info('13. Try to rename file in path A - remove 2 chars from the current name.')
        test.expect(test.dut.dstl_rename_file(test.fileA, 'C'))

        test.log.info('14. Try to rename one directory in path B - remove 2 chars from the current name.')
        test.expect(test.dut.dstl_rename_file(test.pathB, test.pathB[3:-2]))

        test.log.info('15. Create new file in root directory, file name should contain only 2 characters.')
        fh = test.dut.dstl_open_file(test.rootpath+'xy', 10)
        fsize = random.randint(1, 100)
        test.expect(test.dut.dstl_write_file(fh, fsize, dstl_generate_data(fsize)))
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('16. Try to copy new file to path B.')
        test.expect(test.dut.dstl_copy_file(test.rootpath+'xy', test.pathB[:-2]+'/e'))

        test.log.info('17. Check if copied file are the same as original.')
        crc = test.dut.dstl_get_crc(test.rootpath+'xy')
        copyed_crc = test.dut.dstl_get_crc(test.pathB[:-2]+'/e')
        if (crc == copyed_crc):
            test.log.info('CRC same as original file, correct.')
            test.expect(True)
        else:
            test.log.error('CRC not same as original file, error!')
            test.expect(False)

    def cleanup(test):
        pass

    def step_1(test):
        # skip, currently not test INTEL platform, may add later
        test.log.info('1. Create and copy files from PC to the FFS with mixed attributes: read-only, hidden, system, archive.')

if "__main__" == __name__:
    unicorn.main()
