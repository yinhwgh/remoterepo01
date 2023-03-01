#responsible: jun.chen@thalesgroup.com
#location: Beijing
#TC

import unicorn
import os
import subprocess

from core.basetest import BaseTest

class TpSbnwSbnrNvBasic(BaseTest):
    def setup(test):
        pass

    def run(test):
        # Read file before encryption
        test.log.info("Step1. Read file before encryption")
        work_folder = "C:\\WorkSpace\\Test_Data\\sbnr_sbnw_data\\NV\\"
        file_name_write_before_encrypt = "write1.txt"
        bin_file_name_write_after_encrypt = "write1.bin"
        hex_file_name_write_after_encrypt = "write1.hex"
        nv_item_number = "6844"
        nv_item_length = "100"
        file_name_read_before_encrypt = "read1.txt"
        file_name_read_after_encrypt = "decode1.txt"
        file_content_before_encrypt = file_reader(work_folder + file_name_write_before_encrypt)
        test.log.info("NV tool folder is: " + work_folder)
        test.log.info("NV file (before encrypt) name is: " + file_name_write_before_encrypt)
        test.log.info("NV file (before encrypt) content is: \n" + file_content_before_encrypt)

        # Encrypt the file
        line_for_better_log_readability = "----------------------------------------------------------------------------"
        test.log.info(line_for_better_log_readability)
        test.log.info("Step2. Decrypt the file")
        # 1st Encrypt command: encode_dir.pl -d .
        encrypt_command = "encode_dir.pl -d ."
        test.log.info("Encrypt command is: " + encrypt_command)
        # Change work folder to NV folder
        os.chdir(work_folder)
        # Call cmd with subprocess
        process = subprocess.Popen(encrypt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        encrypt_command_log = process.stdout.read().decode('utf-8')
        test.log.info("Encrypt command log is: \n" + encrypt_command_log)
        test.expect(bin_file_name_write_after_encrypt in encrypt_command_log, critical=True)
        # 2nd Encrypt command: encode_dir.pl -d .
        encrypt_command = "bin2hex.pl"
        test.log.info("Change bin to hex command is: " + encrypt_command)
        # Call cmd with subprocess
        process = subprocess.Popen(encrypt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        encrypt_command_log = process.stdout.read().decode('utf-8')
        test.log.info("Change bin to hex command log is (notice empty log is expected): \r" + encrypt_command_log)
        file_content_after_encrypt = file_reader(work_folder + hex_file_name_write_after_encrypt)
        test.log.info("NV file (after encrypt) name is: " + hex_file_name_write_after_encrypt)
        test.log.info("NV file (after encrypt) content is: \n" + file_content_after_encrypt)

        # Write encrypted data with sbnw command
        test.log.info(line_for_better_log_readability)
        test.log.info("Step3. Write NV encrypted data")
        test.expect(test.dut.at1.send_and_verify("AT^SBNW=\"NV\",2", ".*CONNECT.*"), critical=True)
        test.dut.at1.send(file_content_after_encrypt, end="")
        test.dut.at1.wait_for("OK")

        test.log.info(line_for_better_log_readability)
        test.log.info("Step4. Read NV item data")
        # NV item read command at^sbnr="nv",6844,100
        test.dut.at1.send_and_verify("AT^SBNR=\"NV\"," + nv_item_number + "," + nv_item_length, ".*OK.*")
        nv_read_data = get_sbnr_response_data(test.dut.at1.last_response)
        test.log.info("Read data is: \n" + nv_read_data)
        file_writer(work_folder + file_name_read_before_encrypt, nv_read_data)

        test.log.info(line_for_better_log_readability)
        test.log.info("Step5. Decrypt read data")
        # decode.exe read1.txt decoded1.txt
        decrypt_command = "decode.exe " + file_name_read_before_encrypt + " " + file_name_read_after_encrypt
        test.log.info("NV decrypt command is: " + decrypt_command)
        # Call cmd with subprocess
        process = subprocess.Popen(decrypt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        decrypt_command_log = process.stdout.read().decode('utf-8')
        test.log.info("NV decrypt command log is: \r" + decrypt_command_log)
        file_content_after_decode = file_reader(work_folder + file_name_read_after_encrypt)
        test.log.info("NV file (after decode) name is: " + file_name_read_after_encrypt)
        test.log.info("NV file (after decode) content is: \n" + file_content_after_decode)

        test.log.info(line_for_better_log_readability)
        test.log.info("Step6. Compare two file: " + file_name_write_before_encrypt + " " + file_name_read_after_encrypt)
        test.expect(nv_file_content_compare(file_content_before_encrypt, file_content_after_decode))

    def cleanup(test):
        pass

def nv_file_content_compare(data1, data2):
    # Process for data1
    raw1 = data1.upper()
    index_head1 = raw1.index("DATA_BYTES    =")
    content_hex1 = raw1[index_head1 + 17:]
    content_final1 = content_hex1.replace("\n", "")
    # Process for data2
    raw2 = data2.upper()
    index_head2 = raw2.index("DATA_BYTES    =")
    content_hex2 = raw2[index_head2 + 17:]
    content_final2 = content_hex2.replace("\n", "")
    # Return compare result
    return content_final1 == content_final2

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
    target = raw[index_head+1:index_tail-1]
    return target

if(__name__ == "__main__"):
    unicorn.main()
