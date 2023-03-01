#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0095280.001

import unicorn
import urllib.request
from os.path import dirname, realpath
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.http_server import HttpServer

class Test(BaseTest):
    """
        TC0095280.001 DialUpConnectionWin7
        TC0095281.001 DialUpConnectionWin8.
        TC0095282.001 DialUpConnectionWin10
    """

    def setup(test):
        apn = test.dut.sim.apn_v4
        pdp_context = f"AT+CGDCONT=1,\"IPV4V6\",\"{apn}\""
        dstl_detect(test.dut)
        test.dut.at1.send_and_verify(pdp_context, "OK")
        dstl_restart(test.dut)
    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.http_server = HttpServer("IPv4")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        test.log.step("2. Dial up ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name), critical=True)
        #test.dut_devboard.send_and_verify('MC:URC=OFF', 'OK')
        test.sleep(10)
        test.log.step("3. Check if dial up successfully and Download from server")
        get_ping_result(test, server_ip_address)
        test.log.info("Download ......")
        download_file(test.http_server_url, dir)
        test.sleep(5)
        test.log.info("4. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(5)
    def cleanup(test):
        dstl_stop_public_ipv4_data_connection_over_dialup(test.dut, test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('AT', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

def get_ping_result(test, ip_address):
    try:
        result_ping = subprocess.check_output('ping %s' % ip_address)
        ping_str = str(result_ping, 'utf-8')  # convert from byte to string
        test.log.info(ping_str)
    except subprocess.CalledProcessError as error:
        test.log.error("ERROR: Can not get the server!")
        return False
def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    dstl.log.info ('%.2f%%' % per)
def download_file(url, dir):
    #root = os.getcwd()
    root = dirname(dirname(dirname(dirname(realpath(__file__)))))
    name = 'DLfile'
    dir = os.path.join(root, name)
    urllib.request.urlretrieve(url, dir, schedule)
    urllib.request.urlcleanup()

if (__name__ == "__main__"):
    unicorn.main()
