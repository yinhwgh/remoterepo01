#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107103.001

import unicorn
import urllib.request

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network,dstl_enter_pin

class Test(BaseTest):
    """
        TC0107103.001	pppdialup_win_ping2hours
    """
    numOfLoops = 2000
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def get_ping_result(test,ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.log.step("2. Dail up ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
        test.sleep(10)
        test.log.step("3. Check if dial up successfully via ping server")
        loop = 1
        while loop < test.numOfLoops + 1:
            test.get_ping_result(test.ftp_server_ipv4)
            loop = loop + 1
        test.log.info("4. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)
        test.dut.at1.send_and_verify('AT', 'OK')
        test.dut.at1.send_and_verify(r'AT&F', 'OK')

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
