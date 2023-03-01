#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0084481.001

import unicorn
import urllib.request

from os.path import dirname, realpath
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network,dstl_enter_pin
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.http_server import HttpServer

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per = 100
    dstl.log.info('%.2f%%' % per)
def download_file(url,dir):
    root = dirname(dirname(dirname(realpath(__file__))))
    name = 'DLfile'
    dir = os.path.join(root, name)
    urllib.request.urlretrieve(url, dir, Schedule)
    urllib.request.urlcleanup()

class Test(BaseTest):
    """
        TC0084481.001	TpCDunSmsWithoutMux
    """
    numOfLoops = 1000

    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        apn_ipv4 = test.dut.sim.apn_v4
        define_pdp_context_ipv4 = f"AT+CGDCONT=1,\"IPV4V6\",\"{apn_ipv4}\""
        dstl_detect(test.dut)
        test.dut.at1.send_and_verify(define_pdp_context_ipv4, "OK")
        test.dut.at2.send_and_verify('at+cmee=2', 'OK')
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', "OK")  #BJ test Net do not support SMS over IMS
        dstl_restart(test.dut)
    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        test.sleep(5)
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info("**** LOOP {}".format(loop))
            test.log.step("DUN action:")
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
            test.sleep(10)
            test.log.info("Ping server ......")
            test.get_ping_result(server_ipv4_address)
            test.log.info("Download file ......")
            #download_file(test.http_server_url, dir)
            # SMS action:
            test.log.step("SMS action:")
            test.log.info("Send SMS to itself and wait for incoming SMS")
            test.dut.at2.send_and_verify('at+csca="{}"'.format(test.dut.sim.sca_int), '.*OK.*')
            test.dut.at2.send_and_verify('at+cnmi=1,1', 'OK')
            test.dut.at2.send_and_verify('at+cmgf=1', 'OK')
            test.dut.at2.send_and_verify('at+cmgd=1,4', 'OK')
            test.expect(test.dut.at2.send_and_verify(f'AT+CMGS="{test.dut.sim.int_voice_nr}"', '>', wait_for=".*>.*",
                                                      timeout=60))
            test.expect(test.dut.at2.send_and_verify('This is a test message\x1A', ".*OK.*", wait_for=r".*CMGS.*",
                                                      timeout=60))
            test.sleep(5)
            test.log.info("Stop Dial up connection ***")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
            test.sleep(10)
            test.dut.at1.send_and_verify('AT', 'OK')
            loop = loop + 1

    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)

    def cleanup(test):
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"', "OK")
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
