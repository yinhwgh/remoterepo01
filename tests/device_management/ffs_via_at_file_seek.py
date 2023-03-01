# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0087961.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.miscellaneous import ffs_properties
import random


class FfsViaAtFileSeek(BaseTest):
    '''
    TC0087961.001 - FfsViaAtFileSeek
    Intention: Check the function of at^sfsa ="seek",<fh>,<offset>,<seek_flag>
    Debug base project: Serval
    '''
    rootpath = 'a:/'
    dir_list = [rootpath + 'dir1/', rootpath + 'dir1/dir2/', rootpath + 'dir1/dir2/dir3/',
                rootpath + 'dir1/dir2/dir3/dir4/', rootpath + 'dir1/dir2/dir3/dir4/dir5/']
    testpath = rootpath + 'dir1/dir2/dir3/dir4/dir5/'
    empty_file_list = []
    nonempty_file_list = []
    flags = [2, 1, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 18, 19]  # 16

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(5)
        max_path_len = test.dut.dstl_get_ffs_max_dir_lenth()
        test.dut.dstl_clear_directory(test.rootpath)
        test.long_file = test.rootpath + 'z'*(max_path_len - len(test.rootpath))
        test.min_seek_offset = test.dut.dstl_get_ffs_min_seek_offset()
        test.max_seek_offset = test.dut.dstl_get_ffs_max_seek_offset()

    def run(test):
        if test.dut.platform == 'INTEL':
            test.step_1()
        else:
            test.log.info('Skip step 1, can\'t be auto')
        test.log.info('2. On the FFS, create empty files with all possible flag combinations.')
        # create file path list
        flag_count = len(test.flags)
        for i in range(flag_count // 2):
            test.empty_file_list.append(test.testpath + 'fe{}.txt'.format(i))

        for i in range(flag_count // 2, flag_count):
            test.nonempty_file_list.append(test.testpath + 'f{}.txt'.format(i))
        # create folder
        for dirpath in test.dir_list:
            test.expect(test.dut.dstl_create_directory(dirpath))
        for i in range(len(test.empty_file_list)):
            fh = test.dut.dstl_open_file(test.empty_file_list[i], random.randint(8, 10))
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('3. On the FFS, create non empty files with all possible flag combinations.')
        for i in range(len(test.nonempty_file_list)):
            fh = test.dut.dstl_open_file(test.nonempty_file_list[i], 10)
            fsize = random.randint(10, 100)
            test.expect(test.dut.dstl_write_file(fh, fsize, dstl_generate_data(fsize)))
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('4. Create new file, file name and path to it have to consist of 128 characters.')
        fh = test.dut.dstl_open_file(test.long_file, 8)
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('5. Open all files, with all possible flag combinations.')
        # open empty file
        for i in range(len(test.empty_file_list)):
            fh = test.dut.dstl_open_file(test.empty_file_list[i], test.flags[i])
        # open none empty file
        for i in range(len(test.nonempty_file_list)):
            fh = test.dut.dstl_open_file(test.nonempty_file_list[i], test.flags[i + len(test.empty_file_list)])

        test.log.info('6. Move the pointer, calculated from the beginning of the file - "0", to the position:')
        test.log.info('7. For each succeeded pointer move, try read and write data from the pointer position.')
        # execute following test with file a:/file.txt
        fh = test.dut.dstl_open_file('a:/file.txt', 10)
        write_size = random.randint(20, 100)
        random_pos = random.randint(1, write_size - 1)
        test.log.info('Test file size :{}'.format(write_size))
        write_data = dstl_generate_data(write_size)
        test.expect(test.dut.dstl_write_file(fh, write_size, write_data))
        # test seek flag 0,1,2
        for seek_flag in range(3):
            test.log.info('***** Start test seek flag: {} *****'.format(seek_flag))
            test.log.info('***** Current file size: {} *****'.format(write_size))
            test.log.info('a) beginning of the file')
            if seek_flag == 0:
                test.dut.dstl_file_seek(fh, 0, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'a'))
                test.dut.dstl_file_seek(fh, 0, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'a')
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, random_pos, 0)
                test.dut.dstl_file_seek(fh, random_pos * -1, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'd'))
                test.dut.dstl_file_seek(fh, -1, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'd')
            elif seek_flag == 2:
                test.dut.dstl_file_seek(fh, write_size * -1, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'g'))
                test.dut.dstl_file_seek(fh, write_size * -1, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'g')

            test.log.info('b) middle of the file')
            if seek_flag == 0:
                test.dut.dstl_file_seek(fh, write_size // 2, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'b'))
                test.dut.dstl_file_seek(fh, write_size // 2, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'b')
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, write_size // 2 - 1, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'e'))
                test.dut.dstl_file_seek(fh, -1, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'e')
            elif seek_flag == 2:
                test.dut.dstl_file_seek(fh, write_size // 2 * (-1), seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'h'))
                test.dut.dstl_file_seek(fh, -1, 1)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'h')

            test.log.info('c) end of the file')
            if seek_flag == 0:
                test.dut.dstl_file_seek(fh, write_size, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'c'))
                test.dut.dstl_file_seek(fh, write_size, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'c')
                test.dut.dstl_file_seek(fh, 0, 0)
                f_content = test.dut.dstl_read_file(fh, write_size + 1)
                test.expect(test.file_check(fh, f_content, 'a', 'c', write_size + 1))
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, write_size - 1 - write_size // 2, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'f'))
                test.dut.dstl_file_seek(fh, -1, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'f')
                test.dut.dstl_file_seek(fh, 0, 0)
                f_content = test.dut.dstl_read_file(fh, write_size + 1)
                test.expect(test.file_check(fh, f_content, 'd', 'f', write_size + 1))
            elif seek_flag == 2:
                test.dut.dstl_file_seek(fh, 0, seek_flag)
                test.expect(test.dut.dstl_write_file(fh, 1, 'i'))
                test.dut.dstl_file_seek(fh, -1, seek_flag)
                test.expect(test.dut.dstl_read_file(fh, 1) == 'i')
                test.dut.dstl_file_seek(fh, 0, 0)
                f_content = test.dut.dstl_read_file(fh, write_size + 1)
                test.expect(test.file_check(fh, f_content, 'g', 'i', write_size + 1))

            test.log.info('d) beginning of the file -1')
            if seek_flag == 0:
                test.log.info('skip when seek flag is 0(offset need >=0')
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, 0, 0)
                test.expect(test.dut.dstl_file_seek(fh, -1, seek_flag, '.*ERROR.*'))
            elif seek_flag == 2:
                test.expect(test.dut.dstl_file_seek(fh, -1, write_size * (-1) - 2, '.*ERROR.*'))

            test.log.info('e) end of the file + 1')
            if seek_flag == 0:
                test.expect(test.dut.dstl_file_seek(fh, write_size + 2, seek_flag, '.*ERROR.*'))
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, 0, 2)
                test.expect(test.dut.dstl_file_seek(fh, 1, seek_flag, '.*ERROR.*'))
            elif seek_flag == 2:
                test.log.info('skip when seek flag is 0(offset need <=0')

            test.log.info('f) max possible position')
            if seek_flag == 0:
                test.expect(test.dut.dstl_file_seek(fh, test.max_seek_offset, seek_flag, '.*ERROR.*'))
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, random_pos, 0)
                test.expect(test.dut.dstl_file_seek(fh, test.max_seek_offset, seek_flag, '.*ERROR.*'))
            elif seek_flag == 2:
                test.log.info('skip when seek flag is 2(offset need <=0')

            test.log.info('g) min possible position')
            if seek_flag == 0:
                test.log.info('skip when seek flag is 0(offset need >=0')
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, random_pos, 0)
                test.expect(test.dut.dstl_file_seek(fh, test.min_seek_offset, seek_flag, '.*ERROR.*'))
            elif seek_flag == 2:
                test.expect(test.dut.dstl_file_seek(fh, test.min_seek_offset, seek_flag, '.*ERROR.*'))

            test.log.info('h) max possible position + 1')
            if seek_flag == 0:
                test.expect(test.dut.dstl_file_seek(fh, test.max_seek_offset + 1, seek_flag, '.*ERROR.*'))
            elif seek_flag == 1:
                test.dut.dstl_file_seek(fh, random_pos, 0)
                test.expect(test.dut.dstl_file_seek(fh, test.max_seek_offset + 1, seek_flag, '.*ERROR.*'))
            elif seek_flag == 2:
                test.log.info('skip when seek flag is 2(offset need <=0')

            test.log.info('i) min possible position - 1')
            if seek_flag == 0:
                test.log.info('skip when seek flag is 0(offset need >=0')
            else:
                test.dut.dstl_file_seek(fh, random_pos, 0)
                test.expect(test.dut.dstl_file_seek(fh, test.min_seek_offset - 1, seek_flag, '.*ERROR.*'))

            write_size += 1

        test.log.info('8. Close all files.')
        test.expect(test.dut.dstl_close_file(fh))
        for i in range(len(test.flags)):
            test.expect(test.dut.dstl_close_file(i))

        test.log.info('9. Try to move position pointer while file handler is wrong.')
        test.expect(test.dut.dstl_file_seek(-1, 0, 0, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek(-1, 0, 1, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek(-1, 0, 2, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek(33, 0, 0, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek(33, 0, 1, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek(33, 0, 2, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek('a', 0, 0, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek('a', 0, 1, '.*ERROR.*'))
        test.expect(test.dut.dstl_file_seek('a', 0, 2, '.*ERROR.*'))

    def cleanup(test):
        pass

    def step_1(test):
        # skip, currently not test INTEL platform, may add later
        test.log.info('1. Create and copy files from PC to the FFS with mixed attributes.')

    def file_check(test, fh, s, begin, end, length):
        if str(s).startswith(begin) and s.endswith(end):
            test.log.info('File content matches')
            r1 = True
        else:
            test.log.error('File content doesn\'t match, please check')
            r1 = False
        size = test.dut.dstl_file_seek(fh, 0, 2)
        if int(size) == length:
            test.log.info('File length matches')
            r2 = True
        else:
            test.log.error('File length doesn\'t match, expect: {} infact: {}, please check.'.format(length, size))
            r2 = False
        return r1 and r2


if "__main__" == __name__:
    unicorn.main()
