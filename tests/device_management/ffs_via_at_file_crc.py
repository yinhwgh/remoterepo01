#responsible: cong.hu@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0087957.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.miscellaneous import ffs_crc_helper
from dstl.miscellaneous import ffs_properties

class Test(BaseTest):
    """
    TC0087957.001 - FfsViaAtFileCrc
    This TC verify if it is possible to get CRC of the files stored on the FFS via AT^SFSA command.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("Get disks of module.")
        drives = test.dut.dstl_get_ffs_disks()
        if drives:
            test.drive = drives[0]
            test.log.info(f'Delete all the directories and files in root path {test.drive}.')
            test.expect(test.dut.dstl_clear_directory(test.drive))
        else:
            test.drive = 'A:/'
            test.expect(test.dut.dstl_create_directory(test.drive))

    def run(test):
        test.log.step('##########1. Create few different file locations：##########')
        test.log.info(f'##########1.b - {test.drive}dir1/##########')
        test.expect(test.dut.dstl_create_directory(f"{test.drive}dir1"))
        test.log.info(f'##########1.c - {test.drive}dir1/dir2/dir2/dir2/dir2/dir2/##########')
        for i in range(5):
            test.expect(test.dut.dstl_create_directory(f"{test.drive}dir1" + "/dir2" * (i + 1)))
        test.log.info(f'##########1.d - {test.drive}dir1/dir3/dir3/dir3/dir3/dir3/##########')
        for i in range(5):
            test.expect(test.dut.dstl_create_directory(f"{test.drive}dir1" + "/dir3" * (i + 1)))
        test.log.info(f'##########1.e - {test.drive}dir1/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/##########')
        for i in range(11):
            test.expect(test.dut.dstl_create_directory(f"{test.drive}dir1"+"/dir20"*(i+1)))
        test.log.info(f'##########1.f - {test.drive}dir1/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/##########')
        for i in range(11):
            test.expect(test.dut.dstl_create_directory(f"{test.drive}dir1" + "/dir300" * (i+1)))
        test.log.info(f'##########2. In the directories: a, b, c, d, e and f create files:##########')

        write_files = [
                 {'file': f'{test.drive}file1.txt',
                  'flag': '10',
                  'size': 4,
                  'data': 'test'},
                 {'file': f'{test.drive}dir1/file2.txt',
                  'flag': '10',
                  'size': 4,
                  'data': 'stop'},
                 {'file': f'{test.drive}dir1/dir2/dir2/dir2/dir2/dir2/file3.txt',
                  'flag': '10',
                  'size': 16,
                  'data': 'this is /r/ntest'},
                 {'file': f'{test.drive}dir1/dir3/dir3/dir3/dir3/dir3/file4.txt',
                  'flag': '10',
                  'size': 16,
                  'data': 'stop /r/n that a'},
                 {'file': f'{test.drive}dir1/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/dir20/file5.txt',
                  'flag': '10',
                  'size': 7,
                  'data': 'move it'},
                 {'file': f'{test.drive}dir1/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/dir300/file6.txt',
                  'flag': '10',
                  'size': 37,
                  'data': '~~~`!@#$%^&*()_+1234567890?/>.<,:;_+"'},
                  ]
        for write_file in write_files:
            file_handle = test.dut.dstl_open_file(write_file['file'], write_file['flag'])
            if isinstance(file_handle, int):
                test.expect(test.dut.dstl_write_file(file_handle, size=write_file['size'],
                                                     data=write_file['data']))
                test.expect(test.dut.dstl_close_file(file_handle))
            else:
                test.expect(file_handle, msg=f"Fail to open file {write_file['file']}.")

        test.log.step('##########3. Get CRC of all created files: AT^SFSA="crc",<path>##########')
        test.log.step('##########4. Calculate yourself CRC for the same contents and compare with those returned by module.##########')
        for write_file in write_files:
            data_crc = test.dut.dstl_crc16_reflected(write_file['data'])
            read_crc = test.dut.dstl_get_crc(write_file['file'])
            if read_crc:
                test.expect(read_crc == data_crc, msg=f'Actual crc {read_crc} does not match with expected {data_crc}.')
            else:
                test.expect(read_crc, msg=f"Fail to read CRC for {write_file['file']}.")

    def cleanup(test):
        test.log.info(f'Delete all the directories and files in root path {test.drive}')
        test.expect(test.dut.dstl_clear_directory(f"{test.drive}"))

if "__main__" == __name__:
    unicorn.main()
