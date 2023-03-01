#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0104134.002

import unicorn

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.ip_server.http_server import HttpServer

class Test(BaseTest):
    """
        TC0104134.002 StabilityPingCheck_dialup
    """

    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        dstl_detect(test.dut)
        test.dut.at1.send_and_verify("AT+CREG=2", "OK")
        test.dut.at1.send_and_verify("AT+CEREG=2", "OK")
        test.dut.at1.send_and_verify("AT+CMEE=2", "OK")
    def run(test):
        # AT commands
        apn_v4 = test.dut.sim.apn_v4
        #apn_v6 = test.dut.sim.apn_v6
        define_pdp_context_ipv4 = f"AT+CGDCONT=1,\"IP\",\"{apn_v4}\""
        #define_pdp_context_ipv6 = f"AT+CGDCONT=1,\"IPV6\",\"{apn_v6}\""
        test.dut.at1.send_and_verify(define_pdp_context_ipv4, "OK")
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        test.log.step("Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        test.log.step("Dial up ")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name))
        test.sleep(10)
        test.log.step("IPv4 ping to any server using IPv4 address")
        test.get_ping_result(server_ipv4_address)
        test.sleep(5)
        test.log.info(" Stop dial up connection ")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)
    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)
            return False
    def cleanup(test):
        test.dut.at1.send_and_verify('ATI', 'OK')
        test.dut.at1.send_and_verify('AT&F', '.*OK.*')
        pass

if (__name__ == "__main__"):
    unicorn.main()
