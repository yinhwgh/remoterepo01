#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107106.001

import unicorn

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.ip_server.http_server import HttpServer

class Test(BaseTest):
    """
        TC0107106.001	Repeat_dialup_linux_duration
    """
    numOfLoops = 500
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None
    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.http_server = HttpServer("IPv4")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.step("2. Dail up ")
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
            test.sleep(10)
            test.log.step("3. Check if dial up successfully via ping server")
            test.get_ping_result(10, server_ip_address)
            test.log.step("4. Stop dial up connection ***")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
            test.sleep(10)
            test.dut.at1.send_and_verify('AT', 'OK')
            loop = loop + 1
        test.dut.at1.send_and_verify('AT&F', 'OK')

    def get_ping_result(test, count, ip):
        command = 'ping -c %s' % count + " %s" % ip
        p = subprocess.Popen([command],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)

        out = p.stdout.read().decode('utf-8')
        regex = r'.* time=.*ms'
        ping_results = re.findall(regex, out)
        ping_results.sort()
        index = int(0.1 * int(count))
        if len(ping_results) == 0:
            print("Error! No data!")
        elif len(ping_results) < index:
            print("Error! Index out of range!")
        else:
            print(ping_results[index])

    def cleanup(test):
        pass

if (__name__ == "__main__"):
    unicorn.main()
