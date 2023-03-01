#responsible: jun.chen@thalesgroup.com
#location: Beijing
#TC

import unicorn
import os
import subprocess
import filecmp

from core.basetest import BaseTest

class TpSbnwSbnrEfsBasic(BaseTest):
    def setup(test):
        pass

    def run(test):
        # Read file before encryption
        test.log.info("Step1. Read file before encryption")
        efs_work_folder = "C:\\WorkSpace\\Test_Data\\sbnr_sbnw_data\\EFS\\"
        file_name_before_encrypt = "source1.txt"
        file_name_after_encrypt = "write1.hex"
        file_name_in_module = "/data/file1.txt"
        file_name_read_before_encrypt = "read1.hex"
        file_name_read_after_encrypt = "out1.txt"
        file_content_before_encrypt = file_reader(efs_work_folder + file_name_before_encrypt)
        test.log.info("EFS tool folder is: " + efs_work_folder)
        test.log.info("EFS file (before encrypt) name is: " + file_name_before_encrypt)
        test.log.info("EFS file (before encrypt) content is: \n" + file_content_before_encrypt)

        # Encrypt the file
        line_for_better_readability = "-------------------------------------------------------------------------------"
        test.log.info(line_for_better_readability)
        test.log.info("Step2. Decrypt the file")
        # Encrypt command: mefs -h file3_write.txt file3_write.hex
        efs_encrypt_command = "mefs -h " + file_name_before_encrypt + " " + file_name_after_encrypt
        test.log.info("EFS encrypt command is: " + efs_encrypt_command)
        # Change work folder to EFS folder
        os.chdir(efs_work_folder)
        # Call cmd with subprocess
        process = subprocess.Popen(efs_encrypt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        efs_encrypt_command_log = process.stdout.read().decode('utf-8')
        test.log.info("EFS encrypt command log is: \r" + efs_encrypt_command_log)
        test.expect("Data stored to file" in efs_encrypt_command_log, critical=True)
        file_content_after_encrypt = file_reader(efs_work_folder + file_name_after_encrypt)
        test.log.info("EFS file (after encrypt) name is: " + file_name_after_encrypt)
        test.log.info("EFS file (after encrypt) content is: " + file_content_after_encrypt)

        # Write encrypted data with sbnw command
        test.log.info(line_for_better_readability)
        test.log.info("Step3. Write EFS encrypted data")
        test.expect(test.dut.at1.send_and_verify("AT^SBNW=\"EFS\",\"" + file_name_in_module + "\",2", ".*CONNECT.*"), critical=True)
        test.dut.at1.send(file_content_after_encrypt, end="")
        test.dut.at1.wait_for("OK")

        test.log.info(line_for_better_readability)
        test.log.info("Step4. Read EFS test data")
        test.dut.at1.send_and_verify("AT^SBNR=\"EFS\",\"" + file_name_in_module + "\"", ".*OK.*")
        efs_read_data = get_sbnr_response_data(test.dut.at1.last_response)
        test.log.info("EFS read data is: " + efs_read_data)
        file_writer(efs_work_folder + file_name_read_before_encrypt, efs_read_data)

        test.log.info(line_for_better_readability)
        test.log.info("Step5. Decrypt EFS read data")
        # mefs -d read1.hex out1.txt
        efs_decrypt_command = "mefs -d " + file_name_read_before_encrypt + " " + file_name_read_after_encrypt
        test.log.info("EFS decrypt command is: " + efs_decrypt_command)
        # Call cmd with subprocess
        process = subprocess.Popen(efs_decrypt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        efs_decrypt_command_log = process.stdout.read().decode('utf-8')
        test.log.info("EFS decrypt command log is: \r" + efs_decrypt_command_log)

        test.log.info(line_for_better_readability)
        test.log.info("Step6. Compare two file: " + file_name_before_encrypt + " " + file_name_read_after_encrypt)
        test.expect(filecmp.cmp(file_name_before_encrypt, file_name_read_after_encrypt))

    def cleanup(test):
        pass

def file_writer(path, data):
    file_object = open(path, "w")
    try:
        file_object.write(data)
    finally:
        file_object.close()

def file_reader(path):
    file_object = open(path)
    try:
        file_context = file_object.read()
    finally:
        file_object.close()
    return file_context

def get_sbnr_response_data(raw):
    index_head = raw.index(":")
    index_tail = raw.index("OK")
    target = raw[index_head+1:index_tail]
    return target

if(__name__ == "__main__"):
    unicorn.main()
