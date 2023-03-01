#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107255.001

import unicorn
import socket
import urllib.request
from socket import *
import struct
import sys
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.generate_data import dstl_generate_data

class Test(BaseTest):
    """
        TC0107255.001 PPPUdpDLStress1Week
    """
    numOfLoops = 240
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None
    def setup(test):
        dstl_detect(test.dut)
    def run(test):
        data_50 = dstl_generate_data(50)
        data_1300 = dstl_generate_data(1300)
        data_1000 = dstl_generate_data(1000)
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2. Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                         test.dialup_conn_name),critical=True)
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {}'.format(loop))
            test.log.step("3. Connect Server and download data from the Server ")
            test.recv_data(test.udp_echo_server_ipv4, test.udp_echo_server_port_ipv4, data_50)
            test.sleep(7)
            test.recv_data(test.udp_echo_server_ipv4, test.udp_echo_server_port_ipv4, data_1300)
            test.sleep(7)
            test.recv_data(test.udp_echo_server_ipv4, test.udp_echo_server_port_ipv4, data_1000)
            test.sleep(1800)
            loop = loop + 1
        test.log.step("4. Disconnected the UDP server ")
        test.disconnect_udp_server()
        test.log.step("5. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
    def disconnect_udp_server(test):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            udp_socket.close()
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
        recv_data = udp_socket.recv(2048).decode('utf-8')
        if len(recv_data) > 0:
            test.log.info(recv_data)
            test.log.info("Received data successfully")
        else:
            test.log.info("server offline ...")
            return False

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass


if (__name__ == "__main__"):
    unicorn.main()
