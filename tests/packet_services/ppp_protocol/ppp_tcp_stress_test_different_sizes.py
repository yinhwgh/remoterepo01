#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107260.001

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
        TC0107260.001 PPPTcpStressTestDifferentSizes
    """
    numOfLoops = 10000
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
        data_1 = dstl_generate_data(1)
        data_300 = dstl_generate_data(300)
        data_512 = dstl_generate_data(512)
        data_2048 = dstl_generate_data(2048)
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2. Establish dial-up connection ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                         test.dialup_conn_name),critical=True)
        test.sleep(10)
        test.log.step("3. Connect to the TCP receiving serve")
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info('*** Loop: {}'.format(loop))
            test.log.step("4. Send 1 byte data and Receive 1 byte data")
            test.send_data(data_1)
            test.log.step("5. Send 300 byte data and Receive 300 byte data")
            test.send_data(data_300)
            test.log.step("6. Send 512 byte data and Receive 512 byte data")
            test.send_data(data_512)
            test.log.step("7. Send 2048 byte data and Receive 2048 byte data")
            test.send_data(data_2048)
            loop = loop + 1
        test.disconnect_tcp_server()
        test.log.step("8. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)

    def send_data(test, data):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.connect((test.tcp_echo_server_ipv4, test.tcp_echo_server_port_ipv4))
            test.log.info("Connected the server successfully")
        except:
            test.log.error("Failed to connect the server.")
            tcp_socket.close()
        tcp_socket.send(data.encode('utf-8'))
        recv_data = tcp_socket.recv(2048).decode('utf-8')
        if len(recv_data) > 0:
            test.log.info("Sent data successfully.")
            test.log.info("Received data: {}".format(recv_data) + "\n" +
                          "length {} bytes".format(len(recv_data)))
        else:
            test.log.error("Server offline ...")
            return False
    def disconnect_tcp_server(test):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.close()
        except:
            test.log.error(error)

    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
