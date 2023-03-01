# responsible: mariusz.znaczko@globallogic.com
# location: Wroclaw
# TC0095336.002

# feature: LM0003197.007 - Control of Packet Switched Services

import ftplib
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from ftplib import FTP
import os
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.service.file_manage_via_ftp.file_uploader_ftp import _generate_size
from dstl.network_service.register_esim import dstl_register_to_network
from dstl.packet_domain.start_public_IPv4_data_connection import \
    dstl_start_public_ipv4_data_connection_over_dialup, \
    dstl_stop_public_ipv4_data_connection_over_dialup


class Test(BaseTest):
    """
    Intention:
    1. Establish dialup data connection
    2. Establish FTP connection
    3. Upload file to FTP server
    4. Download file from FTP server
    5. Close FTP and dialup connection
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.ftp_server = FtpServer("IPv4", extended=True)

    def run(test):
        ftp_host = test.ftp_server.dstl_get_server_ip_address()
        ftp_user = test.ftp_server.dstl_get_ftp_server_user()
        ftp_pass = test.ftp_server.dstl_get_ftp_server_passwd()

        test.log.step('Step 1: Establish dialup data connection. ')
        try:
            dstl_start_public_ipv4_data_connection_over_dialup(test.dut,
                                                            test, test.dialup_conn_name)
        except Exception:
            test.log.error("Failed to establish DialUp connection!")
            raise Exception("Failed to establish DialUp connection!")

        test.expect(upload_and_download_file_test(test, address=ftp_host, user=ftp_user,
                                                      password=ftp_pass, file_name="1 MB.txt"))

    def cleanup(test):
        test.log.step('Step 5: Close dialup connection. ')
        dstl_stop_public_ipv4_data_connection_over_dialup(test.dut, test, test.dialup_conn_name)
        try:
            test.ftp_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


def upload_and_download_file_test(device, address, user="", password="", file_name=""):
    path = os.getcwd()
    ftp = FTP()
    upload_test_status = False
    download_test_status = False

    device.log.step('Step 2: Establish FTP connection. ')
    try:
        ftp.connect(address, port=50102)
        ftp.login(user, password)
    except Exception:
        raise Exception("Failed to login FTP Server... ")

    try:
        _generate_size(file_name)
    except Exception:
        raise Exception("Failed to create file on local directory")

    device.log.step('Step 3: Upload file to FTP server. ')
    device.log.info("=========== Upload Test ===========")
    device.log.info(os.listdir(path))
    with open(file_name, 'rb') as f:
        device.log.info('uploading...')
        uploading = ftp.storbinary(f'STOR {file_name}', f)

    if "Transfer complete" in uploading:
        device.log.info('Upload Transfer complete.')
        upload_test_status = True
    else:
        device.log.error(uploading)
        raise Exception(uploading)

    try:
        ftp.dir(file_name)
        device.log.info(f"File {file_name}found on Server.")
    except ftplib.error_perm:
        device.log.error(f"File {file_name} not found")
        raise Exception("File not found")

    device.log.step('Step 4: Download file from FTP server. ')
    device.log.info("=========== Download Test ===========")
    out = file_name
    with open(out, 'wb') as f:
        device.log.info("Downloading...")
        downloading = ftp.retrbinary('RETR ' + file_name, f.write)

    if "Transfer complete" in downloading:
        device.log.info(downloading)
        device.expect("Transfer complete" in downloading)
        download_test_status = True
    else:
        device.log.error(downloading)
        device.expect(False)

    try:
        ftp.delete(file_name)
        device.log.info("Remove file from Server success")
    except AssertionError:
        device.log.info("Remove file from Server failed")

    try:
        os.remove(file_name)
        device.log.info("remove file from local directory success")
    except FileNotFoundError:
        device.log.info("remove file from local directory failed")

    ftp.quit()
    device.log.info("Server Disconnected")

    return upload_test_status & download_test_status


if "__main__" == __name__:
    unicorn.main()
