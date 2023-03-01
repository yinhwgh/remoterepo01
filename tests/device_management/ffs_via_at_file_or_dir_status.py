#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0087959.001

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.auxiliary import init
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import restart_module
from dstl.miscellaneous.ffs_properties import dstl_get_ffs_max_dir_lenth


class FfsViaAtFileOrDirStatus(BaseTest):
    """
    TC0087959.001 - FfsViaAtFileOrDirStatus
    """
    rootpath = 'a:/'
    dir_list = [rootpath + 'dir1/', rootpath + 'dir1/dir2/', rootpath + 'dir1/dir2/dir3/',
                rootpath + 'dir1/dir2/dir3/dir4/', rootpath + 'dir1/dir2/dir3/dir4/dir5/']
    file_list = [rootpath + 'f1', rootpath + 'f2', rootpath + 'f3']

    create_flag_list = [8, 9, 10]
    openflag_list = [2, 3, 10]

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(5)
        #128 chars
        max_path_length = test.dut.dstl_get_ffs_max_dir_lenth()
        test.long_file = test.rootpath+'dir1/dir2/dir3/dir4/dir5/'+'x'*(max_path_length-25-len(test.rootpath))

        # clear module FFS
        test.dut.dstl_clear_directory(test.rootpath)

    def run(test):
        # initial status
        dir_status = []
        file_status = []
        # status after change
        dir_status_1 = []
        file_status_1 = []
        test.log.info('1. Set module time to your current local time.')
        test.expect(test.dut.dstl_set_real_time_clock(time='20/01/01,00:00:00'))

        test.log.info('2. Create and copy files from PC to the FFS with '
                      'mixed attributes: read-only, hidden, system, archive.')

        test.log.info('3.Create few new directories on the module FFS')
        for dirpath in test.dir_list:
            test.expect(test.dut.dstl_create_directory(dirpath))

        test.log.info('4.Create few new files with all possible flag combinations on the module FFS')
        for i in range(len(test.create_flag_list)):
            fh = test.dut.dstl_open_file(test.file_list[i], test.create_flag_list[i])
            test.dut.dstl_close_file(fh)

        test.log.info('5. Read status of all files and directories on the FFS')
        # read and save file status
        for i in range(len(test.dir_list)):
            dir_status.append(test.dut.dstl_read_status(test.dir_list[i]))
        for i in range(len(test.file_list)):
            file_status.append(test.dut.dstl_read_status(test.file_list[i]))

        test.log.info('6. Move the module time one hour forward.')
        test.expect(test.dut.dstl_set_real_time_clock(time='20/01/01,01:00:00'))

        test.log.info('7. Read status of all files and directories on the FFS and compare received details with the previous values.')
        # read and save file status after change time
        for i in range(len(test.dir_list)):
            dir_status_1.append(test.dut.dstl_read_status(test.dir_list[i]))

        for i in range(len(test.file_list)):
            file_status_1.append(test.dut.dstl_read_status(test.file_list[i]))
        # compare attributes with previous values, all attributes should be same
        for i in range(len(dir_status_1)):
            for attri_key in dir_status_1[i].keys():
                test.expect(test.compare_status(attri_key,dir_status_1[i],dir_status[i]))
        for i in range(len(file_status_1)):
            for attri_key in file_status_1[i].keys():
                test.expect(test.compare_status(attri_key,file_status_1[i],file_status[i]))

        test.log.info('8. Open all the files with different flag combinations and close files.')
        for i in range(len(test.file_list)):
            fh = test.dut.dstl_open_file(test.file_list[i], 2)
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('9. Check status each file and compare with previous values.')
        file_status = file_status_1.copy()
        file_status_1.clear()
        for i in range(len(test.file_list)):
            file_status_1.append(test.dut.dstl_read_status(test.file_list[i]))

        # compare attributes with previous values, access time should change
        for i in range(len(file_status_1)):
            for attri_key in file_status_1[i].keys():
                if attri_key == 'lastAccessDate':
                    test.expect(test.compare_status(attri_key, file_status_1[i], file_status[i], expect_same=False))
                else:
                    test.expect(test.compare_status(attri_key, file_status_1[i], file_status[i]))

        test.log.info('10. Open few files with different flag combinations, modify files content. Close all the files.')
        for i in range(len(test.file_list)):
            fh = test.dut.dstl_open_file(test.file_list[i], test.openflag_list[i])
            test.expect(test.dut.dstl_write_file(fh, 10, '0123456789'))
            test.expect(test.dut.dstl_close_file(fh))

        test.log.info('11. Check status each file and compare with previous values.')
        file_status = file_status_1.copy()
        file_status_1.clear()
        for i in range(len(test.file_list)):
            file_status_1.append(test.dut.dstl_read_status(test.file_list[i]))

        # compare attributes with previous values,all should change
        for i in range(len(file_status_1)):
            for attri_key in file_status_1[i].keys():
                if attri_key == 'Attribute':
                    pass
                else:
                    test.expect(test.compare_status(attri_key, file_status_1[i], file_status[i], expect_same=False))

        test.log.info('12. Create file, file name and path to it have to consist of 128 characters.')
        fh_long = test.dut.dstl_open_file(test.long_file, 8)
        if (type(fh_long) == int):
            test.log.info('13. Read status of the file already created and close the file.')
            test.expect(test.dut.dstl_close_file(fh_long))
            stat = test.dut.dstl_read_status(test.long_file)

            test.log.info('14. Move the module time 23 hours forward and check file status.')
            test.expect(test.dut.dstl_set_real_time_clock(time='20/01/02,00:00:00'))
            stat_1 = test.dut.dstl_read_status(test.long_file)
            # compare , all should be same
            for attri_key in stat_1.keys():
                test.expect(test.compare_status(attri_key, stat_1, stat))

            test.log.info('15. Open and close file. Check file status.')
            fh = test.dut.dstl_open_file(test.long_file, 2)
            test.expect(test.dut.dstl_close_file(fh))
            stat = stat_1.copy()
            stat_1 = test.dut.dstl_read_status(test.long_file)
            # compare attributes with previous values, access time should change
            for attri_key in stat_1.keys():
                if attri_key == 'lastAccessDate':
                    test.expect(test.compare_status(attri_key, stat_1, stat, expect_same=False))
                else:
                    test.expect(test.compare_status(attri_key, stat_1, stat))

            test.log.info('16. Move the module time 30 min forward and check file status.')
            test.expect(test.dut.dstl_set_real_time_clock(time='20/01/02,00:30:00'))
            stat = stat_1.copy()
            stat_1 = test.dut.dstl_read_status(test.long_file)
            # compare , all should be same
            for attri_key in stat_1.keys():
                test.expect(test.compare_status(attri_key, stat_1, stat))

            test.log.info('17. Open, modify and close file.')
            fh = test.dut.dstl_open_file(test.long_file, 2)
            test.expect(test.dut.dstl_write_file(fh, 10, '0123456789'))
            test.expect(test.dut.dstl_close_file(fh))

            test.log.info('18. Read file status.')
            stat_2 = test.dut.dstl_read_status(test.long_file)
            for attri_key in stat_2.keys():
                if attri_key == 'Attribute':
                    pass
                else:
                    test.expect(test.compare_status(attri_key, stat_1, stat_2, expect_same=False))

        else:
            test.log.error('create long path file fail, please check')
            test.expect(False)

        test.log.info('19. Try to read status of non existing directory.')
        test.expect(test.dut.dstl_read_status(test.rootpath + 'fakedirfakedirfakedir/') == False)

        test.log.info('20. Try to read status of non existing file.')
        test.expect(test.dut.dstl_read_status(test.rootpath + 'fakefilefakefilefakefile.txt') == False)

    def cleanup(test):
        pass

    def compare_status(test, key_value, attribute_dic1, attribute_dic2, expect_same = True):
    # function used to compare attribute values
        if expect_same == True:
            if attribute_dic1[key_value] == attribute_dic2[key_value]:
                test.log.info('Attributes "{}" are equal'.format(key_value))
                return True
            else:
                test.log.error('Attributes "{}" are not equal'.format(key_value))
                return False
        elif expect_same == False:
            if attribute_dic1[key_value] != attribute_dic2[key_value]:
                test.log.info('Attributes "{}" are changed'.format(key_value))
                return True
            else:
                test.log.error('Attributes "{}" are not changed'.format(key_value))
                return False


if "__main__" == __name__:
    unicorn.main()
