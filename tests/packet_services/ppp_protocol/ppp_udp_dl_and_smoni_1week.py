#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107254.001

import unicorn
import socket
import urllib.request
import struct
import sys
from socket import *
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.generate_data import dstl_generate_data

class Test(BaseTest):
    """
        TC0107254.001 PPPUdpDLAndSmoni1Week 
    """
    numOfLoops = 240
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        data_100 = dstl_generate_data(100)
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.thread(test.check_network, test.dut.at2)
        test.log.step("2. Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                         test.dialup_conn_name), critical=True)

        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.step("3. Connect to the serve and receive data")
            test.recv_data(test.udp_echo_server_ipv4, test.udp_echo_server_port_ipv4, data_100)
            test.sleep(1800)
            loop = loop + 1
        test.log.step("4. Close TCP connection")
        test.disconnect_tcp_server()
        test.log.step("5. Stop dial up connection ***")
        test.expect(test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
        test.sleep(10)
    def disconnect_tcp_server(test):
        tcp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            tcp_socket.close()
        except:
            test.log.error(error)
    def recv_data(test, addr, port, data):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            udp_socket.connect((addr, port))
        except:
            test.log.error("Failed to connect the server.")
            udp_socket.close()
        udp_socket.send(data.encode('utf-8'))
        recv_data = udp_socket.recv(1024).decode('utf-8')
        if len(recv_data) > 0:
            test.log.info("Received data from server successfully.")
            test.log.info(recv_data)
        else:
            test.log.info("Server offline ...")
            return False

    def check_network(test, port):
        for i in range(1, 200000):
            test.expect(port.send_and_verify('AT^SMONI', 'OK'))
            test.sleep(2)

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
