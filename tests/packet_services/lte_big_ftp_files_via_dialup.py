#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0088074.003

import unicorn
import urllib.request

from ftplib import FTP
from os.path import dirname, realpath
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_lte
from dstl.auxiliary.restart_module import dstl_restart


def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per = 100
    dstl.log.info ('%.2f%%' % per)

def download_file(url,dir):
    root = dirname(dirname(dirname(realpath(__file__))))
    name = 'DLfile'
    dir = os.path.join(root, name)
    urllib.request.urlretrieve(url, dir, Schedule)
    urllib.request.urlcleanup()

#dir = 'C:\DL\downloadfil.zip'

#
download_size = 0
upload_size = 0
bufsize = 102400

class DialUpConnectionWindows(BaseTest):
    """
       TC0088074.003 LteBigFtpFilesViaDialUp_Dahlia
       need to config the server url
    """
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        apn = test.dut.sim.apn_v4
        pdp_context = f"AT+CGDCONT=1,\"IPV4V6\",\"{apn}\""
        # pdp_context = f"AT+CGDCONT=1,\"IP\",\"internet\""
        test.dut.at1.send_and_verify(pdp_context, "OK")
        dstl_detect(test.dut)
        dstl_restart(test.dut)

    def run(test):
        test.log.step("1.register on Network")
        test.expect(dstl_register_to_lte(test.dut))
        test.sleep(5)
        test.log.step("2.Dial up ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
        test.sleep(10)
        test.log.step("3.Check if dial up successfully and Download files from server")
        test.get_ping_result(test.ftp_server_ipv4)
        # download_file(test.http_server_url, dir)
        filename = "3333.7z"
        localfile = "3333.7z"
        if os.path.exists('C:\download') == True:
            localpath = 'C:\download'
        else:
            os.mkdir('C:\download')
            localpath = 'C:\download'
        test.ftp_download(localpath,filename)
        test.sleep(5)
        test.ftp_upload(localpath,localfile)
        test.log.step("4.Stop dial up connection ")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(2)
        test.dut.at1.send_and_verify('AT', '.*OK.*')

    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)
            return False

    def cleanup(test):
        test.dut.at1.send_and_verify(r'AT&F', '.*OK.*')
        pass


    def ftp_download(test,localpath,filename):
        ftp = FTP()
        os.chdir(localpath)
        ftp.set_debuglevel(2)
        ftp.connect(test.ftp_server_ipv4, test.ftp_server_port_ipv4)
        ftp.login(test.ftp_username_ipv4, test.ftp_password_ipv4)
        # print ftp.getwelcome()#显示ftp服务器欢迎信息
        # ftp.cwd('xxx/xxx/') #选择操作目录

        file_size = ftp.size(filename)
        file_handler = open(filename, 'wb')

        def download_percentage(block):
            global download_size
            file_handler.write(block)
            download_size = download_size + len(block)
            download_percentage = (download_size/file_size) * 100
            if download_percentage > 100:
                download_percentage = 100
            dstl.log.info('Downloading %.2f%%' % download_percentage)

        ftp.retrbinary('RETR %s' % os.path.basename(filename), download_percentage, bufsize)  # 接收服务器上文件并写入本地文件
        file_handler.close()
        ftp.set_debuglevel(0)

        ftp.quit()
        print("FTP download finished!!")

    def ftp_upload(test,localpath,localfile):
        ftp = FTP()
        os.chdir(localpath)
        ftp.set_debuglevel(2)
        ftp.connect(test.ftp_server_ipv4, test.ftp_server_port_ipv4)
        ftp.login(test.ftp_username_ipv4, test.ftp_password_ipv4)
        # print ftp.getwelcome()#显示ftp服务器欢迎信息
        # ftp.cwd('xxx/xxx/') #选择操作目录

        file_handler = open(localfile,'rb')
        file_size = os.path.getsize(localfile)

        def upload_percentage(block):
            global upload_size
            upload_size = upload_size + len(block)
            upload_percentage = (upload_size/file_size) * 100
            if upload_percentage > 100:
                upload_percentage =100
            dstl.log.info('Uploading %.2f%%' % upload_percentage)

        ftp.storbinary('stor %s' % os.path.basename(localfile), file_handler,bufsize,upload_percentage)
        file_handler.close()
        ftp.set_debuglevel(0)
        ftp.quit()
        print("FTP upload finished!!")


if (__name__ == "__main__"):
    unicorn.main()
