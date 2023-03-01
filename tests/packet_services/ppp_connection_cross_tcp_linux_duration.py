#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0107104.001

import unicorn
import urllib.request
import socket
from socket import *
from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.http_server import HttpServer

class Test(BaseTest):
    """
        TC0107104.001	pppconnection_cross_tcp_linux_duration
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
        dstl_restart(test.dut)
    def run(test):
        data_60k = 'a'*60000
        test.log.step("1. Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.http_server = HttpServer("IPv4")
        server_ip_address = test.http_server.dstl_get_server_ip_address()
        test.log.step("2. Set up a ppp diap up connection by USB port ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2",
                                                                                         test.dialup_conn_name),critical=True)
        test.sleep(10)
        test.log.step("3. Check if the ppp connection estabilishment via ping server ")
        test.get_ping_result(server_ip_address)
        test.log.step("4. Dial up disconnection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(5)
        test.dut.at1.send_and_verify('AT', 'OK')
        test.log.step("5. Set up a TCP connection and send a package at least to sever on asc0 port.")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at1",
                                                                                         test.dialup_conn_name),critical=True)
        test.log.step("6. Connect to the TCP serve and Send data 1000 times")
        loop = 1
        while loop < test.numOfLoops + 1:
            test.log.info("*** Test Loop: {}".format(loop))
            test.send_data(test.tcp_echo_server_ipv4, test.tcp_echo_server_port_ipv4, data_60k)
            loop = loop + 1
        test.log.step("7 Stop TCP connection ***")
        test.disconnect_tcp_server()
        test.log.step("8. Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)

    def get_ping_result(test, ip):
        command = 'ping %s' % ip
        p = subprocess.Popen([command],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)

        out = p.stdout.read().decode('utf-8')
        regex = r'.* time=.*ms'
        ping_results = re.findall(regex, out)
        ping_results.sort()
        if len(ping_results) == 0:
            test.log.info("Error! No data!")
        else:
            test.log.info(ping_results)
    def disconnect_tcp_server(test):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        try:
            tcp_socket.close()
            test.log.info("Disconnect TCP server successfully.")
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
        test.dut.at1.send_and_verify('AT', 'OK')
        test.dut.at1.send_and_verify(f"AT+CGDCONT=1,\"IPV4V6\",\"\"", "OK")
        test.dut_devboard.send_and_verify('MC:URC=OFF', 'OK')
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
