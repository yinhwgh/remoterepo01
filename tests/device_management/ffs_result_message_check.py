#responsible: cong.hu@thalesgroup.com, lei.chen@thalesgroup.com
#location: Dalian
#TC0105248.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.call import switch_to_command_mode
from dstl.miscellaneous import access_ffs_by_at_command

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        error_number_message_map = {
            'create_dir_error': [14, 'create directory error'],
            'path_not_found': [1, 'path not found'],
            'delete_file_error': [6, 'delete file error'],
            'invalid_drive': [100, 'invalid drive'],
            'open_file_error': [3, 'open file error'],
            'invalid_file_descriptor': [9, 'invalid file descriptor'],
            'remove_dir_error': [15, 'remove directory error'],
            'sharing_violation': [30, 'sharing violation'],
            'path_exists': [16, 'path already exists'],
            'file_exists': [17, 'file already exists'],
            'parameter_out_of_range': [204, 'input parameter out of range'],
            'incorrect_parameter': [202, 'incorrect parameter'],
            'negative_file_pointer': [22, 'seek to negative file pointer attempted'],
            'invalid_file_pointer': [23, 'seek to invalid file pointer attempted'],
            'no_more_file_descriptor': [24, 'no more file descriptors available'],
            'time_expired': [214, 'data transfer error: time expired'],
            'transfer_abort': [211, 'data transfer abort'],
            'invalid_path': [101, 'invalid path']
        }

        for cmee in range(2,0,-1):
            test.log.info(f"Start tests for AT+CMEE={cmee}.")
            test.expect(test.dut.at1.send_and_verify(f'at+cmee={cmee}', expect='OK'))
            error_dict={k: f'\^SFSA: {v[cmee-1]}' for k,v in error_number_message_map.items()}

            test.log.step('1. Delete all the files or directories on the FFS.')
            test.dut.dstl_list_directory('a:/')
            test.expect(test.dut.dstl_clear_directory('a:/'))

            test.log.step('2. Try to create dir whose parent dir is not exist and check the '
                          'result message(create directory error(CMEE=2) or 14(CMEE=1)).')
            test.expect(test.dut.dstl_create_directory('a:/dir1/dir2',
                                                       expect_response=error_dict['create_dir_error']))

            test.log.step('3. Try to remove dir which is not exsit on the FFS and check the '
                          'result message(path not found(CMEE=2) or 1(CMEE=1)).')
            test.expect(test.dut.dstl_remove_directory('a:/dir1/dir2/dir3/dir4',
                                                       expect_response=error_dict['path_not_found']))

            test.log.step('4. Try to remove file which is not exsit on the FFS and check '
                          'the result message(delete file error(CMEE=2) or 6(CMEE=1)).')
            test.expect(test.dut.dstl_remove_file('a:/text1',
                                                  expect_response=error_dict['delete_file_error']))

            test.log.step('5. Try to list file on invalid drive and check the result '
                          'message(invalid drive(CMEE=2) or 100(CMEE=1)).')
            test.expect(test.dut.at1.send_and_verify('at^sfsa=ls,c:/',
                                                     expect=error_dict['invalid_drive']))

            test.log.step('6. Try to open file, which is not exsit on the FFS, with read/write flag '
                          ' and check the result message(open file error(CMEE=2) or 3(CMEE=1)).')
            test.expect(test.dut.dstl_open_file("a:/test1.txt,2", flag=2,
                                                expect_response=error_dict['open_file_error']))

            test.log.step('7. Try to close a file with file handle which is not used and check the '
                          'result message(invalid file descriptor(CMEE=2) or 9(CMEE=1))')
            test.expect(test.dut.dstl_close_file(0,
                                                 expect_response=error_dict['invalid_file_descriptor']))

            test.log.step('8. Create a new dir(dir1) and create a new file(test1) in this dir with '
                          'read/write flag. Do not close the file.')
            test.expect(test.dut.dstl_create_directory('a:/dir1', expect_response='OK'))
            test.expect(isinstance(test.dut.dstl_open_file("a:/dir1/test1.txt", flag=10,
                                                           expect_response='OK'), int))

            test.log.step('9. Try to delete dir1 and check the result message(remove directory '
                          'error(CMEE=2) or 15(CMEE=1)).')
            test.expect(test.dut.dstl_remove_directory('a:/dir1',
                                                       expect_response=error_dict['remove_dir_error']))

            test.log.step('10. Try to delete test1 and check the result '
                          'message(sharing violation(CMEE=2) or 30(CMEE=1)).')
            test.expect(test.dut.dstl_remove_file('a:/dir1/test1.txt',
                                                  expect_response=error_dict['sharing_violation']))

            test.log.step('11. Try to create dir with the same name as the dir which is already '
                          'exist(dir1) and check the result message(path already exists(CMEE=2) '
                          'or 16(CMEE=1)).')
            test.expect(test.dut.dstl_create_directory('a:/dir1',
                                                       expect_response=error_dict['path_exists']))

            test.log.step('12. Close the file test1.')
            test.expect(test.dut.dstl_close_file(0, expect_response='OK'))

            test.log.step('13. Open file1 with invalid flag(256) and check the result '
                          'message(input parameter out of range(CMEE=2) or 204(CMEE=1)).')
            test.expect(test.dut.dstl_open_file("a:/dir1/test1.txt", flag=256,
                                                expect_response=error_dict['parameter_out_of_range']))

            test.log.step('14. Open file1 with truncate and read only flags(80) and check the '
                          'result message(incorrect parameter(CMEE=2) or 202(CMEE=1)).')
            test.expect(test.dut.dstl_open_file("a:/dir1/test1.txt", flag=80,
                                                expect_response=error_dict['incorrect_parameter']))

            test.log.step('15. Open file1 with read/write flag and write 20 bytes data into it.')
            file_handler = test.dut.dstl_open_file("a:/dir1/file1", flag=10, expect_response='OK')
            if not isinstance(file_handler, int):
                test.expect(False, msg='File to create file "a:/dir1/file1".')
                # to continue tests
                file_handler = 0
            test.expect(test.dut.dstl_write_file(file_handler, 20, data='1234567890abcdefghij',
                                                 expect_response='OK'))

            test.log.step('16. Seek to the start point of the file with command "at^sfsa=seek,0,0".')
            test.expect(test.dut.dstl_file_seek(file_handler, 0, expect_response='.*OK.*'))

            test.log.step('17. Try to seek to negative file pointer with command "at^sfsa=seek,0,-1" '
                          'and check the result message(seek to negative file pointer '
                          'attempted(CMEE=2) or 22(CMEE=1)).')
            test.expect(test.dut.dstl_file_seek(file_handler, -1,
                                                expect_response=error_dict['negative_file_pointer']))
            test.expect(test.dut.dstl_read_file(file_handler, 20))

            test.log.step('18. Seek to pointer 10(at^sfsa=seek,0,10)and try to seek to the pointer '
                          'out range of the file with command(at^sfsa=seek,0,15,1), then check the '
                          'result message(seek to invalid file pointer attempted(CMEE=2) or 23(CMEE=1)).')
            test.expect(test.dut.dstl_file_seek(file_handler, 10, expect_response='OK'))
            test.expect(test.dut.dstl_file_seek(file_handler, 15, 1,
                                                expect_response=error_dict['invalid_file_pointer']))

            test.log.step('19. Seek to the end of test1(at^sfsa=seek,0,20), then input '
                          '"at^sfsa=write,0,10". After that, do not wirte data and wait for the '
                          'expire. Check the result message(data transfer error: '
                          'time expired(CMEE=2) or 214(CMEE=1)).')
            test.expect(test.dut.dstl_file_seek(file_handler, 20, expect_response='OK'))
            test.expect(test.dut.at1.send_and_verify(f'at^sfsa=write,{file_handler},10',
                                                     expect='\s+CONNECT', wait_for="CONNECT"))
            test.expect(test.dut.at1.wait_for(error_dict['time_expired']))

            test.log.step('20. Input "at^sfsa=write,0,10". After that, input "+++". Check the '
                          'result message(data transfer abort(CMEE=2) or 211(CMEE=1)). '
                          'Then close the file.')
            test.expect(test.dut.at1.send_and_verify(f'at^sfsa=write,{file_handler},10',
                                                     expect='CONNECT', wait_for="CONNECT"))
            test.sleep(1)
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses(expect=error_dict['transfer_abort']))
            test.expect(test.dut.dstl_close_file(file_handler))

            test.log.step('21. Create new dir with name "!@#$%^&*" and check the result '
                          'message(invalid path(CMEE=2) or 101(CMEE=1))')
            test.expect(test.dut.dstl_create_directory('a:/!@#$%^&*',
                                                       expect_response=error_dict['invalid_path']))

            test.log.step('22. Try to rename test1 with the same name '
                          '"at^sfsa=rename,a:/dir1/test1,test1" and check the '
                          'result message(file already exists(CMEE=2) or 17(CMEE=1)).')
            test.expect(test.dut.dstl_rename_file('a:/dir1/test1.txt', 'test1.txt',
                                                  expect_response=error_dict['file_exists']))

            test.log.step('23. Try to create and open 33 files and check the result '
                          'message(no more file descriptors available(CMEE=2) or 24(CMEE=1)).')
            for i in range(32):
                test.expect(isinstance(test.dut.dstl_open_file(f"a:/file_{i}", flag=10,
                                                               expect_response=f'\s+\^SFSA: {i},\s*0\s+OK'), int))

            test.expect(test.dut.dstl_open_file(f"a:/33", flag=10,
                                                expect_response=error_dict['no_more_file_descriptor']))
            if cmee == 2:
                test.log.info('24. Close all the files.')
                for i in range(0,32):
                    test.expect(test.dut.dstl_close_file(i))


    def cleanup(test):
        test.log.info('Close all the files.')
        for i in range(32):
            test.expect(test.dut.at1.send_and_verify(f'at^sfsa=close,{i}', expect='.*OK.*'))

        test.log.info('Delete all the files.')
        test.expect(test.dut.at1.send_and_verify('AT^SFSA=rmdir,a:/', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SFSA=mkdir,a:/', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

if '__main__' == __name__:
    unicorn.main()
