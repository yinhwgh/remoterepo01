#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107256.001

import unicorn
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
        TC0107256.001 PPPUdpULStress1Week 
    """
    numOfLoops = 300
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        data_50 = dstl_generate_data(50)
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("* Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                         test.dialup_conn_name),critical=True)
        test.sleep(10)
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.step("* Connect to the UDP receiving serve and Send 50 bytes data")
            test.send_data(test.udp_echo_server_ipv4, test.udp_echo_server_port_ipv4, data_50)
            test.log.step("* Waiting 30 minutes ...... ")
            test.sleep(1800)
            loop = loop + 1
        test.log.step("* Close TCP connection")
        test.disconnect_udp_server()
        test.log.step("* Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
    def send_data(test, addr, port, data):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            udp_socket.connect((addr, port))
        except:
            test.log.error("Failed to connect the server.")
            udp_socket.close()

        udp_socket.send(data.encode('utf-8'))
        recv_data = udp_socket.recv(2048).decode('utf-8')
        if len(recv_data) > 0:
            test.log.info("Received data - {}".format(recv_data))
            test.log.info("Sent data successfully.")
        else:
            test.log.info("Server offline....")
            return False

    def disconnect_udp_server(test):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            udp_socket.close()
        except:
            test.log.error(error)

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()