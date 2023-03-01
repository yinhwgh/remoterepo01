#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087956.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.configuration import character_set
from dstl.miscellaneous.ffs_properties import dstl_get_ffs_max_dir_lenth

class FfsViaAtDirCreateRenameRemove(BaseTest):
    """
    TC0087956.001 - FfsViaAtDirCreateRenameRemove

    Intention :This TC verify if it is possible to perform basic FFS functions via
    AT^SFSA command like: create, rename and remove directories using ASCII and USC2 character set.

    Debug base project: Serval
    """
    rootpath = 'a:/'
    #test path for GSM charset
    dir1 = rootpath + 'dir1'
    dir2 = rootpath + 'dir2'
    dir22 = rootpath + 'dir2/dir22'
    #test path for UCS2 charset
    dir1_u = rootpath + 'dir1u'
    dir2_u = rootpath + 'dir2u'
    dir22_u = rootpath + 'dir2u/dir22u'


    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_set_character_set('GSM')
        test.dut.dstl_restart()
        test.sleep(5)
        # clear module FFS
        test.dut.dstl_clear_directory(test.rootpath)

    def run(test):
        max_path_len = test.dut.dstl_get_ffs_max_dir_lenth()
        test.log.info('1.In the root directory a:/, try to create directories with the name length from 1 to 128')
        #for some products have limit, max 100 folder under root, seperate the test
        test.log.info('1.a test length 1 to 100')
        for i in range(1, 101):
            dname = test.rootpath + i * 'z'
            test.log.info('Current test length :{}'.format(len(dname)))
            test.expect(test.dut.dstl_create_directory(dname))

        test.log.info('4.a Try to list a content of the root directory after each new directory created(length 1-100)')
        file_list = test.dut.dstl_list_directory(test.rootpath)
        test.log.info(file_list)
        for i in range(1, 101):
            dname = i * 'z'+'/'
            if dname in file_list:
                test.log.info('directory {} is in list ,pass'.format(test.rootpath + i * 'z'))
                test.expect(True)
            else:
                test.log.error('directory is not in list, please check'.format(test.rootpath + i * 'z'))
                test.expect(False)

        test.log.info('1.b Clear root dir after create 100 folder')
        test.dut.dstl_clear_directory(test.rootpath)

        test.log.info('1.c test path length 101 to max')
        for i in range(101, max_path_len - len(test.rootpath) + 1):
            dname = test.rootpath + i * 'z'
            test.log.info('Current test length :{}'.format(len(dname)))
            test.expect(test.dut.dstl_create_directory(dname))

        test.log.info('4.b Try to list a content of the root directory after each new directory created(length 101-max)')
        file_list = test.dut.dstl_list_directory(test.rootpath)
        test.log.info(file_list)
        for i in range(101, max_path_len - len(test.rootpath)):
            dname = i * 'z' + '/'
            if dname in file_list:
                test.log.info('directory {} is in list ,pass'.format(test.rootpath + i * 'z'))
                test.expect(True)
            else:
                test.log.error('directory is not in list, please check'.format(test.rootpath + i * 'z'))
                test.expect(False)

        test.log.info('2.In the root directory a:/, try to create directories with the name length >128 characters.')
        dname = test.rootpath + 126 * 'z'
        test.expect(test.dut.dstl_create_directory(dname, expect_response='ERROR'))

        test.log.info('3. Try to create directory with the name already existing.')
        test.expect(test.dut.dstl_create_directory(test.dir1))
        test.expect(test.dut.dstl_create_directory(test.dir2))
        test.expect(test.dut.dstl_create_directory(test.dir1, expect_response='ERROR'))
        test.expect(test.dut.dstl_create_directory(test.dir2, expect_response='ERROR'))

        test.log.info('5. Try to create directories structure to have path length containing 128 characters.')
        longdir = test.rootpath + 'b/c/d/e/' + dstl_generate_data(max_path_len - len(test.rootpath)-8)
        test.expect(test.dut.dstl_create_directory_with_parser(longdir, test.rootpath))

        test.log.info('6. Try to create few additional directories in the path specified above.')
        test.expect(test.dut.dstl_create_directory(longdir+'/111/',expect_response='ERROR'))
        test.expect(test.dut.dstl_create_directory(longdir+'/xyz/', expect_response='ERROR'))
        test.expect(test.dut.dstl_create_directory(longdir+'/abc/', expect_response='ERROR'))

        test.log.info('7. Try to create a directory at non existing drivers.')
        test.expect(test.dut.dstl_create_directory('c:/dir1', expect_response='ERROR'))
        test.expect(test.dut.dstl_create_directory('d:/dir1', expect_response='ERROR'))

        if test.dut.project == 'SERVAL' or test.dut.project == 'VIPER':
            test.log.info('Skip step 8 to 11, not support')
        else:
            test.step8(max_path_len)

            test.log.info('9. Using USC2 characters try to create directory with the name already existing but created with ASCII characters.')
            test.expect(test.dut.dstl_ucs2_create_directory(test.dir1, expect_response='ERROR'))

            test.log.info('10.Using UCS2 characters try to rename directories created with ASCII characters')
            test.expect(test.dut.dstl_ucs2_rename_file(test.dir1, 'dirucs2'))
            test.expect(test.dut.dstl_ucs2_rename_file(test.rootpath+'dirucs2', 'dir1'))

            test.log.info('11.Using ASCII characters try to rename directories created with USC2 characters.')
            test.dut.dstl_set_character_set('GSM')
            test.expect(test.dut.dstl_rename_file(test.dir1_u, 'dirstep11'))


        test.log.info('12.Try to rename chosen directory/ies created in point 4 to extend total path length to above 128 characters')
        test.expect(test.dut.dstl_rename_file(test.rootpath+ 'z'*105, 'o' * 128, expect_response='ERROR'))

        test.log.info('13.Try to rename non existing directory.')
        test.expect(test.dut.dstl_rename_file(test.rootpath+'qazxsw123456','dir_09876', expect_response='ERROR'))

        test.log.info('14.Try to rename existing directory, new name should consist of 128 characters.')
        #serval will hung up here....
        test.expect(test.dut.dstl_rename_file(test.dir1, 'o'*(max_path_len - len(test.rootpath))))

        test.log.info('15.Try to rename existing directory, new name should consist more than 128 characters.')
        test.expect(test.dut.dstl_rename_file(test.dir2, 'o' * 128, expect_response='ERROR'))

        test.log.info('16.Try to remove non empty directory.')
        test.expect(test.dut.dstl_create_directory(test.dir22))
        if test.dut.project == 'SERVAL' or test.dut.project == 'VIPER':
            test.expect(test.dut.dstl_remove_directory(test.dir2, expect_response='OK'))
        else:
            test.expect(test.dut.dstl_remove_directory(test.dir2, expect_response='ERROR'))

        test.log.info('17.Try to remove all created directories: AT^SFSA="rmdir",path')
        test.dut.dstl_clear_directory(test.rootpath)

        test.log.info('18.Each time check if chosen directory is deleted: AT^SFSA="ls","a:"')
        test.dut.dstl_list_directory(test.rootpath)

        test.log.info('19.Try to remove already removed directory.')
        test.expect(test.dut.dstl_remove_directory(test.dir22, expect_response='ERROR'))

        test.log.info('20.Try to remove never existing directory.')
        test.expect(test.dut.dstl_remove_directory(test.rootpath+'not_exist_dir/', expect_response='ERROR'))

    def step8(test,max):
        test.log.info('8. Repeat above steps using USC2 characters instead of ASCII')
        test.dut.dstl_set_character_set('UCS2')

        test.log.info('8.1 (UCS2)In the root directory a:/, try to create directories with the name length from 1 to 128')
        max_len_ucs2 = (max - len(test.rootpath*4))//4
        for i in range(1,max_len_ucs2+1,4):
            dname = test.rootpath+'u'*i
            test.log.info('(UCS2)Current test length :{}'.format(len(dname)*4))
            test.expect(test.dut.dstl_ucs2_create_directory(dname))

        test.log.info('8.2 (UCS2)In the root directory a:/, try to create directories with the name length >128 characters')
        dname = test.rootpath + 32 * 'u'
        test.expect(test.dut.dstl_ucs2_create_directory(dname, expect_response='ERROR'))

        test.log.info('8.3 (UCS2)Try to create directory with the name already existing.')
        test.expect(test.dut.dstl_ucs2_create_directory(test.dir1_u))
        test.expect(test.dut.dstl_ucs2_create_directory(test.dir2_u))
        test.expect(test.dut.dstl_ucs2_create_directory(test.dir1_u, expect_response='ERROR'))
        test.expect(test.dut.dstl_ucs2_create_directory(test.dir2_u, expect_response='ERROR'))

        test.log.info('8.4 (UCS2)Try to list a content of the root directory after each new directory created')
        file_list = test.dut.dstl_ucs2_list_directory(test.rootpath)
        test.log.info(file_list)
        for i in range(1, max_len_ucs2+1):
            dname = test.dut.dstl_convert_to_ucs2(i * 'u'+'/')
            if dname in file_list:
                test.log.info('directory {} is in list ,pass'.format(test.rootpath + i * 'u'))
                test.expect(True)
            else:
                test.log.error('directory {} is not in list, please check'.format(test.rootpath + i * 'u'))
                test.expect(False)

        test.log.info('8.5 (UCS2)Try to create directories structure to have path length containing 128 characters.')
        max_path_ucsc2 = test.rootpath+dstl_generate_data(max_len_ucs2)
        test.expect(test.dut.dstl_ucs2_create_directory(max_path_ucsc2))

        test.log.info('8.6 (UCS2)Try to create few additional directories in the path specified above.')
        test.expect(test.dut.dstl_ucs2_create_directory(max_path_ucsc2 + '/xxx', expect_response='ERROR'))
        test.expect(test.dut.dstl_ucs2_create_directory(max_path_ucsc2 + '/qqq', expect_response='ERROR'))
        test.expect(test.dut.dstl_ucs2_create_directory(max_path_ucsc2 + '/aaa', expect_response='ERROR'))

        test.log.info('8.7 (UCS2)Try to create a directory at non existing drivers.')
        test.expect(test.dut.dstl_ucs2_create_directory('c:/dir1', expect_response='ERROR'))
        test.expect(test.dut.dstl_ucs2_create_directory('d:/dir1', expect_response='ERROR'))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()