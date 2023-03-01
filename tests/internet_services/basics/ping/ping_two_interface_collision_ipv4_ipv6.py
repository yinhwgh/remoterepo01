#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0093658.001, TC0093658.002

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution


class Test(BaseTest):
    """
    TC0093658.001, TC0093658.002 - PingTwoInterfaceCollision_IPv4IPv6

    This test checks the possibility to ping on two interface (for ex.: USB and ASC0).

    1) Enter PIN and attach module to the network.
    2) Define two PDP contexts, or connection profiles (for IPv4 and IPv6) and activate them if applicable.
    3) Call ping command for IPv4 with <request> equal 30 on two interface separately.
    4) Call ping command with <request> equal 30 for IPv4  on two interface simultaneously.
    5) Call ping command with <request> equal 30 for IPv6  on two interface separately.
    6) Call ping command with <request> equal 30 for IPv6  on two interface simultaneously.
    7) Call ping command with <request> equal 30 for IPv4 and IPv6 on two interface at the same time.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.http_server_ipv4 = HttpServer("IPv4")
        test.http_server_ipv6 = HttpServer("IPv6")
        test.address_http_ipv4 = test.http_server_ipv4.dstl_get_server_ip_address()
        test.address_http_ipv6 = test.http_server_ipv6.dstl_get_server_ip_address()

    def run(test):
        test.log.info("TC0093658.002 - PingTwoInterfaceCollision_IPv4IPv6")
        test.log.step("1) Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Define two PDP contexts, or connection profiles (for IPv4 and IPv6) "
                      "and activate them if applicable.")
        test.define_cids_and_setup_connection_profile()

        test.log.step("3) Call ping command for IPv4 with <request> equal 30 on two interface separately.")
        test.log.info("=== Execute PING for IPv4 on 1st interface ===")
        test.execute_ping('at1', test.cid_ipv4)
        test.sleep(5)
        test.log.info("=== Execute PING for IPv4 on 2nd interface ===")
        test.execute_ping('at2', test.cid_ipv4)
        test.sleep(5)

        test.log.step("4) Call ping command with <request> equal 30 for IPv4 on two interface simultaneously.")
        test.log.info("=== Execute PING for IPv4 on both interfaces ===")
        test.start_threads(test.cid_ipv4, test.cid_ipv4)
        test.sleep(5)

        test.log.step("5) Call ping command with <request> equal 30 for IPv6 on two interface separately.")
        test.log.info("=== Execute PING for IPv6 on 1st interface ===")
        test.execute_ping('at1', test.cid_ipv6)
        test.sleep(5)
        test.log.info("=== Execute PING for IPv6 on 2nd interface ===")
        test.execute_ping('at2', test.cid_ipv6)
        test.sleep(5)

        test.log.step("6) Call ping command with <request> equal 30 for IPv6 on two interface simultaneously.")
        test.log.info("=== Execute PING for IPv6 on both interfaces ===")
        test.start_threads(test.cid_ipv6, test.cid_ipv6)
        test.sleep(5)

        test.log.step("7) Call ping command with <request> equal 30 for IPv4 and IPv6 on two interface at the same time.")
        test.log.info("=== Execute PING for IPv4 and IPv6 on both interfaces - on 1st for IPv4, on 2nd for IPv6 ===")
        test.start_threads(test.cid_ipv4, test.cid_ipv6)
        test.sleep(5)

    def cleanup(test):
        test.close_server(test.http_server_ipv4)
        test.close_server(test.http_server_ipv6)

    def define_cids_and_setup_connection_profile(test):
        test.log.info("=== Connection profile for IPv4 setup ===")
        connection_setup_ipv4 = dstl_get_connection_setup_object(test.dut)
        connection_setup_ipv4.cgdcont_parameters['cid'] = '1'
        test.expect(connection_setup_ipv4.dstl_load_internet_connection_profile())
        test.log.info("=== Connection profile for IPv6 setup ===")
        connection_setup_ipv6 = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        connection_setup_ipv6.cgdcont_parameters['cid'] = '2'
        test.expect(connection_setup_ipv6.dstl_load_internet_connection_profile())
        test.log.info("=== Activate Connection profile for IPv4 ===")
        test.expect(connection_setup_ipv4.dstl_activate_internet_connection())
        test.cid_ipv4 = connection_setup_ipv4.dstl_get_used_cid()
        test.log.info("=== Activate Connection profile for IPv6 ===")
        test.expect(connection_setup_ipv6.dstl_activate_internet_connection())
        test.cid_ipv6 = connection_setup_ipv6.dstl_get_used_cid()

    def execute_ping(test, interface_name, cid, check_statistics=True):
        if cid == test.cid_ipv4:
            address = test.address_http_ipv4
        else:
            address = test.address_http_ipv6
        ping_request = 30
        ping_time_limit = 1000
        ping_execution = InternetServiceExecution(test.dut, cid, interface_name)
        test.expect(ping_execution.dstl_execute_ping(address, request=ping_request, timelimit=ping_time_limit,
                                                     expected_response="Ping.*OK.*",
                                                     check_packet_statistics=check_statistics))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= ping_request * 0.2)

    def start_threads(test, cid_1, cid_2):
        t1 = test.thread(test.execute_ping, 'at1', cid_1, False)
        t2 = test.thread(test.execute_ping, 'at2', cid_2, False)
        t1.join()
        t2.join()

    def close_server(test, http_server):
        test.log.info("===Close HTTP service profile. ===")
        try:
            if not http_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()