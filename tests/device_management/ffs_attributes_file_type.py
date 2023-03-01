#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0093468.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.miscellaneous import access_ffs_by_at_command
from dstl.miscellaneous import ffs_crc_helper
from dstl.java import java_parameters

class Test(BaseTest):
    """
        TC0093468.001 -  TpFfsAttributes_FileType
        The module shall be able to set the CDC line of the RS232 interface to either always on or on while it
        detects a data carrier.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.dstl_enter_pin)
        # Init variables
        test.disk = 'A:/'
        test.directory = 'A:/dir1/'
        test.read_only_file_name = "ro.txt"
        test.read_only_file_path = test.directory + test.read_only_file_name
        test.file_new_name = "rename_file.txt"
        test.read_only_content = "readonly"
        test.jad_file = test.disk + 'CollI2C.jad'
        test.jar_file = test.disk + 'CollI2C.jar'
        test.access_file_readyonly = '64'
        test.access_file_create_write = '10'
        test.access_file_truncate = '16'
        test.access_file_read_truncate = '80'
        test.access_file_read_append = '20'
        test.access_file_invalid_flags = ['128', '200'] 
        # Clear up directory
        test.log.info('Setup: Delete all the directories and files in root path A:/')
        test.expect(test.dut.dstl_clear_directory("A:/"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))

    def run(test):
        test.log.info('Step 0, create a normal file with name {}'.format(test.read_only_file_name))
        test.expect(test.dut.dstl_create_directory(test.directory))
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_create_write)
        test.expect(test.dut.dstl_write_file(file_handler, size=len(test.read_only_content), data=test.read_only_content))
        test.expect(test.dut.dstl_close_file(file_handler))

        test.log.info('Step 1, Check it is impossible to write any data into the read only file.')
        # Open file with readonly flag, writing data to module returns error
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_readyonly)
        test.expect(test.dut.dstl_write_file(file_handler, size=4, data="test", expect_response="CONNECT"))
        test.expect(test.dut.at1.send_and_verify("t", expect="\^SFSA: output stream write error.*\+CME ERROR: operation not allowed"))
        test.expect(test.dut.dstl_close_file(file_handler))

        test.log.info('Step 2, Check the read only file can be computed by using command CRC.')
        test.expect(test.dut.at1.send_and_verify('AT^SFSA="crc","{}"'.format(test.read_only_file_path), "\^SFSA: {}, 0".
                                                 format(test.dut.dstl_crc16_reflected(test.read_only_content))))

        test.log.info('Step 3, Check the read only file can be read.')
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_readyonly)
        read_content = test.dut.dstl_read_file(file_handler, len(test.read_only_content))
        test.expect(read_content == test.read_only_content, msg=f"Actual read content {read_content}"
                    f"is not matched with expected content {test.read_only_content}")
        test.expect(test.dut.dstl_close_file(file_handler))

        test.log.info("Step 4, Consistently write and read from the read only file to check the if the module would hang")
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_readyonly)
        for i in range(10):
            test.log.info("Loop {} of 10: Consistently write and read from the read only file".format(i+1))
            test.expect(test.dut.dstl_write_file(file_handler, size=4, data="test", expect_response="CONNECT"))
            test.expect(test.dut.at1.send_and_verify("t", expect="\^SFSA: output stream write error.*\+CME ERROR: operation not allowed"))
            test.expect(test.dut.dstl_file_seek(file_handler,'0'))
            read_content = test.dut.dstl_read_file(file_handler, len(test.read_only_content))
            test.expect(read_content == test.read_only_content)
        test.expect(test.dut.dstl_close_file(file_handler))

        test.log.info("Step 5, Check the file attribute after open the existing file.")
        attributes_before_open = test.dut.dstl_read_status(test.read_only_file_path)
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_readyonly)
        test.expect(test.dut.dstl_close_file(file_handler))
        attributes_after_open = test.dut.dstl_read_status(test.read_only_file_path)
        test.expect(attributes_after_open["fileSize"] == attributes_before_open["fileSize"], 
        msg="File size {} after open is not equal with file size before open{}".format(attributes_after_open["fileSize"], attributes_before_open["fileSize"]))
        test.expect(attributes_after_open["Attribute"] == attributes_before_open["Attribute"], 
        msg="Attribute {} after open is not equal with attribute before open{}".format(attributes_after_open["Attribute"], attributes_before_open["Attribute"]))

        
        test.log.info("Step 6, Check the read only file can be copied.")
        test.expect(test.dut.dstl_create_directory('a:/dir2'))
        new_path = test.read_only_file_path.replace('dir1', 'dir2')
        test.expect(test.dut.dstl_copy_file(test.read_only_file_path, new_path))
        test.dut.at1.send_and_verify("at^sfsa=\"ls\",\"{}\"".format(new_path.replace(test.read_only_file_name, "")))
        last_response = test.dut.at1.last_response
        test.expect(test.read_only_file_name in last_response)

        test.log.info("Step 7, Check the read only file can be renamed.")
        test.file_new_name_path = test.directory + test.file_new_name
        test.expect(test.dut.dstl_rename_file(test.read_only_file_path, test.file_new_name))
        test.read_only_file_path = test.file_new_name_path

        test.log.info("Step 8, Check the read only file cannot be truncated.")
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_truncate)
        test.expect(test.dut.dstl_close_file(file_handler))
        test.expect(test.dut.at1.send_and_verify("at+cmee=2"))
        test.expect(test.dut.dstl_open_file(test.read_only_file_path, test.access_file_read_truncate, 
        expect_response="\^SFSA: incorrect parameter.*\+CME ERROR: operation not allowed"))
        test.expect(test.dut.at1.send_and_verify("at+cmee=1"))
        test.expect(test.dut.dstl_open_file(test.read_only_file_path, test.access_file_read_truncate, expect_response="\^SFSA: 202.*\+CME ERROR: 3"))
        
        test.log.info("Step 9, Read only file cannot be opened by any illegal file access flags.")
        for flag in test.access_file_invalid_flags:
            test.expect(test.dut.at1.send_and_verify("at+cmee=1"))
            test.expect(test.dut.dstl_open_file(test.read_only_file_path, flag, expect_response="\^SFSA: 204.*\+CME ERROR: 21"))
            test.expect(test.dut.at1.send_and_verify("at+cmee=2"))
            test.expect(test.dut.dstl_open_file(test.read_only_file_path, flag, expect_response="\^SFSA: input parameter out of range.*\+CME ERROR: invalid index"))

        test.log.info("Step 10, The operation append should not remove the file attributes")
        attributes_before_append = test.dut.dstl_read_status(test.read_only_file_path)
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, test.access_file_read_append)
        test.expect(test.dut.dstl_close_file(file_handler))
        attributes_after_append = test.dut.dstl_read_status(test.read_only_file_path)
        test.expect(attributes_after_append["fileSize"] == attributes_before_append["fileSize"],
        msg="File size {} after append is not equal with file size before append {}".format(attributes_after_append["fileSize"], attributes_before_append["fileSize"]))
        test.expect(attributes_after_append["Attribute"] == attributes_before_append["Attribute"],
        msg="Attribute {} after append is not equal with attribute before append{}".format(attributes_after_append["Attribute"], attributes_before_append["Attribute"]))

        test.log.info("Step 11, The copy operation should not modify any file attribute")
        file_handler = test.dut.dstl_open_file(test.read_only_file_path, '1')
        test.expect(test.dut.dstl_write_file(file_handler, size=len(test.read_only_content), data=test.read_only_content))
        test.expect(test.dut.dstl_close_file(file_handler))
        test.expect(test.dut.dstl_copy_file(test.read_only_file_path, test.directory + 'ro_copy.txt'))
        attributes_before_copy = test.dut.dstl_read_status(test.read_only_file_path)
        attributes_after_copy = test.dut.dstl_read_status(test.read_only_file_path)
        test.expect(attributes_after_copy == attributes_before_copy, msg="attributes after copy are not equal to before copy")
        attributes_copied_file = test.dut.dstl_read_status(test.directory + 'ro_copy.txt')
        test.expect(attributes_copied_file["fileSize"] == attributes_before_copy["fileSize"],
        msg="File size {} after copy is not equal with file size before copy {}".format(attributes_copied_file["fileSize"], attributes_before_copy["fileSize"]))
        test.expect(attributes_copied_file["Attribute"] == attributes_before_copy["Attribute"],
        msg="Attribute {} after copy is not equal with attribute before copy{}".format(attributes_copied_file["Attribute"], attributes_before_copy["Attribute"]))

        test.log.info('Step 12, Check if the read only file can be removed from FFS.')
        test.expect(test.dut.dstl_remove_file(test.read_only_file_path))

        test.log.info("Step 13, Attempt to create a JAR and JAD file on the FFS.")
        # Content need be updated for products with Intel platform which supports JRC
        file_handler = test.dut.dstl_open_file(test.jad_file, '10')
        test.expect(test.dut.dstl_write_file(file_handler, size=4, data="test"))
        test.expect(test.dut.dstl_close_file(file_handler))
        file_handler = test.dut.dstl_open_file(test.jar_file, '10')
        test.expect(test.dut.dstl_write_file(file_handler, size=4, data="test"))
        test.expect(test.dut.dstl_close_file(file_handler))

        test.log.info("Step 14, Rename to JAR and JAD file on the FFS for products supporting JRC is not allowed")
        if test.dut.dstl_support_jrc():
            expected_response = "ERROR"
            new_jar_file = test.jar_file
            new_jad_file = test.jad_file
        else:
            expected_response = "OK"
            new_jar_file = test.disk + "new_name.jar"
            new_jad_file = test.disk + "new_name.jad"
        test.expect(test.dut.dstl_rename_file(test.jad_file, "new_name.jad", expect_response = expected_response))
        test.expect(test.dut.dstl_rename_file(test.jar_file, "new_name.jar", expect_response = expected_response))

        test.log.info("Step 15, Copying JAR and JAD file on the FFS for products supporting JRC is not allowed")
        test.expect(test.dut.dstl_copy_file(new_jad_file, test.disk + "copy_file.jad", expect_response = expected_response))
        test.expect(test.dut.dstl_copy_file(new_jar_file, test.disk + "copy_file.jar", expect_response = expected_response))


    def cleanup(test):
        for i in range(4):
            test.dut.dstl_close_file(i, expect_response="OK|ERROR")


if "__main__" == __name__:
    unicorn.main()