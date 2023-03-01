#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087958.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.miscellaneous.ffs_properties import dstl_get_ffs_max_dir_lenth


class FfsViaAtFileOpenCloseRemove(BaseTest):
    """
    TC0087958.001 - FfsViaAtFileOpenCloseRemove

    Debug base project: Serval
    """
    rootpath = 'a:/'
    dir_list = [rootpath + 'dir1/', rootpath + 'dir1/dir2/', rootpath + 'dir1/dir2/dir3/',
                rootpath + 'dir1/dir2/dir3/dir4/', rootpath + 'dir1/dir2/dir3/dir4/dir5/']
    step1path = rootpath + 'd'*116 + '/'
    file_none_exist = rootpath+'fne.txt'
    flags = [1, 2, 4, 16, 32, 64]
    file_100b = rootpath+'100bytes.txt'
    file_2 = rootpath + 'file2.txt'
    file_name3 = step1path+'000'
    file_name8 = step1path+'00000000'
    file_name10 = step1path+'0000000000'

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(5)
        # clear module FFS
        test.dut.dstl_clear_directory(test.rootpath)

    def run(test):
        max_path_len = test.dut.dstl_get_ffs_max_dir_lenth()
        test.log.info('1.Create a file location,  total path length = 120 characters.')
        test.expect(test.dut.dstl_create_directory(test.step1path))

        test.log.info('2.Try to open non existing file with all possible flag combinations but without 8')
        for i in test.flags:
            test.expect(test.dut.dstl_open_file(test.file_none_exist, i, expect_response='.*ERROR.*'))

        test.log.info('3.Create file with flag 8 only and try to write down 100 bytes of data to it.')
        fh = test.dut.dstl_open_file(test.file_100b, 8)
        test.expect(test.dut.dstl_close_file(fh))
        fh = test.dut.dstl_open_file(test.file_100b, 2)
        test.expect(test.dut.dstl_write_file(fh, 100, dstl_generate_data(100)))
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('4.Try to create file with the name as previously in step 3 and with flag 8')
        test.dut.dstl_open_file(test.file_100b, 8, expect_response='.*ERROR.*|.*OK.*')
        if 'OK' in test.dut.at1.last_response:
            test.dut.dstl_close_file(0)

        test.log.info('5.Open an existing file with all possible flag combinations and test: read, write, close.')
        fh = test.dut.dstl_open_file(test.file_2, 8)
        test.expect(test.dut.dstl_close_file(fh))
        fh = test.dut.dstl_open_file(test.file_2, 2)
        test.expect(test.dut.dstl_write_file(fh, 10, '0123456789'))
        test.dut.dstl_file_seek(fh, 0, 0)
        test.expect(test.dut.dstl_read_file(fh, 10))
        test.expect(test.dut.dstl_close_file(fh))

        if test.dut.platform == 'INTEL':
            test.step_6to7()
        else:
            test.log.info('Skip step 6 and 7, can\'t be auto')

        test.log.info('8.Try to create new file in location from step 1. File name has to be shorter than 8 characters.')
        fh = test.dut.dstl_open_file(test.file_name3, 8)
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('9.Try to create new file in location from step 1. File name has to contain 8 characters.')
        fh = test.dut.dstl_open_file(test.file_name8, 8)
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('10.Try to create new file in location from step 1. File name has to be longer than 8 characters.')
        test.expect(test.dut.dstl_open_file(test.file_name10, 8, expect_response='.*ERROR.*'))

        test.log.info('11. Try to remove opened file.')
        fh = test.dut.dstl_open_file(test.file_100b, 2)
        test.expect(test.dut.dstl_remove_file(test.file_100b, expect_response='.*ERROR.*'))
        test.log.info('12. Try to remove non existing file.')
        test.expect(test.dut.dstl_remove_file(test.file_none_exist, expect_response='.*ERROR.*'))

        test.log.info('13. Try to close all opened files.')
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('14. Try to close non opened file.')
        test.expect(test.dut.dstl_close_file(fh, expect_response='.*ERROR.*'))

        test.log.info('15. Try to remove all previously created files.')
        test.dut.dstl_clear_directory(test.rootpath)

        test.log.info('16. Try to create 65535 empty files.') # create 100 files
        for i in range(100):
            fh = test.dut.dstl_open_file(test.rootpath+'emptyf{}.txt'.format(i), 8)
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('17. Try to create 2 more files.')
        fh = test.dut.dstl_open_file(test.rootpath + 'emptyf1111.txt', 8)
        test.expect(test.dut.dstl_close_file(fh))
        fh = test.dut.dstl_open_file(test.rootpath + 'emptyf2222.txt', 8)
        test.expect(test.dut.dstl_close_file(fh))

        test.log.info('18. Remove all files from the FFS.')
        test.dut.dstl_clear_directory(test.rootpath)

        test.log.info('19. In the root directory a:/, try to create files with the name length from 1 to 128 characters.')
        for i in range(1, max_path_len - len(test.rootpath)+1):
            fname = test.rootpath + i*'a'
            test.log.info('current test length: {}'.format(len(fname)))
            fh = test.dut.dstl_open_file(fname, 8)
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('20. In the root directory a:/, try to create files with the name length >128 characters.')
        fname = test.rootpath + 126 * 'a'
        test.expect(test.dut.dstl_open_file(fname, 8, expect_response = 'ERROR'))

        test.log.info('21. Remove all files from the FFS.')
        test.dut.dstl_clear_directory(test.rootpath)

        #UCS2 part not support by Serval, will add later.

    def cleanup(test):
        pass
    def step_6to7(test):
        # skip, currently not test INTEL platform, may add later
        test.log.info('6. Copy files from PC to the FFS with attributes: read-only, hidden, system, archive.')
        test.log.info('7. Try to open (with different flags) modify and close each file previously copied from PC.')

if "__main__" == __name__:
    unicorn.main()