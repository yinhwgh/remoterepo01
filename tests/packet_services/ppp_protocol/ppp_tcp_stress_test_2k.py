#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107259.001

import unicorn
import urllib.request
import struct
import socket
from socket import *
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """
        TC0107259.001 PPPTcpStressTest2K
    """
    numOfLoops = 10000
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None
    def setup(test):
        dstl_detect(test.dut)
    def run(test):
        data_2k = dstl_generate_data(2000)
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {}'.format(loop))
            test.log.step("2. Establish dial-up connection ")
            test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                     test.dialup_conn_name),  critical=True)
            test.sleep(10)
            test.log.step("3. Connect to the TCP serve and Send 2k data")
            test.send_data(test.tcp_echo_server_ipv4, test.tcp_echo_server_port_ipv4, data_2k )
            test.log.step("5. Close TCP connection")
            test.disconnect_tcp_server()
            test.log.step("6. Stop dial up connection ***")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
            test.sleep(10)
            loop = loop + 1
    def disconnect_tcp_server(test):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.close()
        except:
            test.log.error(error)

    def send_data(test, addr, port, data):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.connect((addr, port))
        except:
            test.log.error("Failed to connect the server.")
            tcp_socket.close()
        tcp_socket.send(data.encode('utf-8'))
        recv_data = tcp_socket.recv(2048).decode('utf-8')
        if len(recv_data) > 0:
            test.log.info(recv_data)
            test.log.info("Sent data successfully")
        else:
            test.log.info("server offline..")
            return False

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
