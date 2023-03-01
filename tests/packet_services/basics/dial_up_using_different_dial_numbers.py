#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0010263.004

import unicorn

from core.basetest import BaseTest
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart

class DialUpConnectionWindows(BaseTest):
    """
        debuged via Viper
        TC0010263.004 DialUpUsingDifferentDialNumbers
    """
    # dial_numbers = ["*99#","*99**1*#","*99***1#","*99**1*1#"]
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        apn = test.dut.sim.apn_v4
        pdp_context = f"AT+CGDCONT=1,\"IPV4V6\",\"{apn}\""
        dstl_detect(test.dut)
        test.expect(test.dut.at1.send_and_verify(pdp_context, "OK"))
        dstl_restart(test.dut)

    def run(test):
        test.log.step("Register on Network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(10)
        test.log.step("Dail up via *99#")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name),critical=True)
        test.sleep(10)
        test.log.step("Check if dial up successfully via ping server")
        test.get_ping_result(test.ftp_server_ipv4)
        test.log.info("Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)
        test.dut.at1.send_and_verify('AT', 'OK')
        dstl_register_to_network(test.dut)
        test.log.step("Dail up via *99**1*#")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name, "*99**1*#"), critical=True)
        test.sleep(10)
        test.log.step("Check if dial up successfully via ping server")
        test.get_ping_result(test.ftp_server_ipv4)
        test.log.info("Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(5)
        test.dut.at1.send_and_verify('AT', 'OK')
        dstl_register_to_network(test.dut)
        test.log.step("Dail up via *99***1#")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name, "*99***1#"), critical=True)
        test.sleep(10)
        test.log.step("Check if dial up successfully via ping server")
        test.get_ping_result(test.ftp_server_ipv4)
        test.log.info("Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(5)
        test.dut.at1.send_and_verify('AT', 'OK')
        dstl_register_to_network(test.dut)
        test.log.step("Dail up via *99**1*1#")
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name, "*99**1*1#"),critical=True)
        test.sleep(10)
        test.log.step("Check if dial up successfully via ping server")
        test.get_ping_result(test.ftp_server_ipv4)
        test.log.info("Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        test.sleep(10)
        test.dut.at1.send_and_verify(r'AT', '.*OK.*')

    def get_ping_result(test, ip_address):
        try:
            result_ping = subprocess.check_output('ping %s' % ip_address)
            ping_str = str(result_ping, 'utf-8')  # convert from byte to string
            test.log.info(ping_str)
        except subprocess.CalledProcessError as error:
            test.log.error(error)
            return False

    def cleanup(test):
        test.dut.at1.send_and_verify(r'AT&F', '.*OK.*')
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, test.dialup_conn_name)
        pass

if (__name__ == "__main__"):
    unicorn.main()
