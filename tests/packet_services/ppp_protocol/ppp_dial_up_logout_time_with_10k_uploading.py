#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107258.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.generate_data import dstl_generate_data

class Test(BaseTest):
    """
        TC0107258.001 PPPDialUpLogoutTimeWith10KUploading
    """
    numOfLoops = 10
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def get_ping_result(test,ip_address):
        try:
            result_ping = subprocess.check_output('ping %s -n 300' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        data_10k = dstl_generate_data(10000)
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2. Establish dial-up connection ")
        test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)
        test.log.step("3. Connect to the TCP receiving serve and Send 10k data")
        test.get_ping_result(server_ipv4_address)
        test.log.step("4. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        time_rec_disconnect_req = time.time()
        test.dut.at1.wait_for(".*NO CARRIER", timeout=4)
        time_rev_urc = time.time()
        delta_t = time_rev_urc - time_rec_disconnect_req
        if delta_t < 3:
            test.log.info("Measured time:{:.2f} in line with expectations.".format(delta_t))
        else:
            test.log.error("The time of disconnect dialup is Not meet the expectation")
    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
